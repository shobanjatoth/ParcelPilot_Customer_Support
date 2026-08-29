from __future__ import annotations

import logging
import re
import time
from typing import Optional

import httpx

from app.agent.prompts import SYSTEM_PROMPT
from app.agent.state import AgentState
from app.config import get_settings
from app.data.repository import Repository
from app.security.auth import can_access_account, is_internal
from app.services.retrieval import RetrievalService
from app.tools.actions import create_escalation_tool
from app.tools.documents import search_documents_tool
from app.tools.operations import (
    get_account_tool,
    get_order_tool,
    get_orders_by_account_tool,
    get_ticket_tool,
    get_tickets_by_account_tool,
)

logger = logging.getLogger("parcelpilot.agent")


# ============================================================
# Input Security
# ============================================================

_INJECTION_PATTERNS = [
    r"ignore\s+(previous|all|above)\s+(instructions?|prompts?|rules?)",
    r"you\s+are\s+now\s+",
    r"system\s*:",
    r"act\s+as\s+",
    r"pretend\s+you\s+are\s+",
    r"disregard\s+(previous|all|above)",
    r"override\s+(previous|all|above)",
    r"new\s+instructions?\s*:",
    r"forget\s+(everything|all|previous)",
]


def sanitize_query(query: str) -> str:
    """
    Normalize and limit user input.

    Detection of prompt injection is logged, but the query is not
    silently rewritten because changing user intent can be dangerous.
    Retrieved documents are treated as untrusted data by the system
    prompt.
    """

    if not isinstance(query, str):
        return ""

    sanitized = query.strip()

    if len(sanitized) > 2000:
        sanitized = sanitized[:2000]

    for pattern in _INJECTION_PATTERNS:
        if re.search(pattern, sanitized, re.IGNORECASE):
            logger.warning(
                "Potential prompt injection detected: %s",
                sanitized[:200],
            )
            break

    return sanitized


# ============================================================
# Entity Extraction
# ============================================================

def extract_account_id(query: str) -> Optional[str]:
    """
    Extract a known ParcelPilot account identifier from the query.
    """

    patterns = [
        (r"\bnorthstar\b", "ACCT-001"),
        (r"\blumenworks\b", "ACCT-002"),
        (r"\bbeacon\b", "ACCT-003"),
        (r"\baxis\s*labs\b", "ACCT-004"),
        (r"\bACCT-\d+\b", None),
    ]

    for pattern, account_override in patterns:
        match = re.search(pattern, query, re.IGNORECASE)

        if not match:
            continue

        if account_override:
            return account_override

        return match.group(0).upper()

    return None


def extract_order_id(query: str) -> Optional[str]:
    match = re.search(r"\bORD-\d+\b", query, re.IGNORECASE)

    if not match:
        return None

    return match.group(0).upper()


def extract_ticket_id(query: str) -> Optional[str]:
    match = re.search(r"\bTKT-\d+\b", query, re.IGNORECASE)

    if not match:
        return None

    return match.group(0).upper()


# ============================================================
# LLM
# ============================================================

def call_llm(messages: list[dict]) -> str:
    """
    Call Gemini through its OpenAI-compatible API endpoint.
    """

    settings = get_settings()

    if not settings.gemini_api_key:
        logger.error("GEMINI_API_KEY is not configured")
        return (
            "The AI service is not configured correctly. "
            "Please contact support."
        )

    start = time.perf_counter()

    try:
        response = httpx.post(
            f"{settings.gemini_base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.gemini_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.llm_model,
                "messages": messages,
                "max_tokens": 2000,
                "temperature": 0.1,
            },
            timeout=60.0,
        )

        response.raise_for_status()

        payload = response.json()

        choices = payload.get("choices", [])

        if not choices:
            logger.error("Gemini returned no choices")
            return (
                "I could not generate a response from the AI service."
            )

        message = choices[0].get("message", {})
        content = message.get("content")

        if not content:
            logger.error("Gemini returned an empty response")
            return (
                "I could not generate a response from the AI service."
            )

        latency = round(time.perf_counter() - start, 3)

        logger.info(
            "LLM call successful model=%s latency=%ss",
            settings.llm_model,
            latency,
        )

        return str(content).strip()

    except httpx.TimeoutException:
        logger.error("LLM request timed out")

        return (
            "The AI service took too long to respond. "
            "Please try again."
        )

    except httpx.HTTPStatusError as exc:
        logger.error(
            "LLM HTTP error status=%s response=%s",
            exc.response.status_code,
            exc.response.text[:500],
        )

        return (
            "The AI service is temporarily unavailable. "
            "Please try again later."
        )

    except (httpx.RequestError, ValueError) as exc:
        logger.error(
            "LLM request failed error=%s",
            exc,
        )

        return (
            "I could not connect to the AI service. "
            "Please try again later."
        )

    except Exception:
        logger.exception("Unexpected LLM failure")

        return (
            "An unexpected error occurred while generating "
            "the response."
        )


# ============================================================
# Context Construction
# ============================================================

def _build_document_context(citations: list[dict]) -> str:
    """
    Build a compact context from retrieved citations.
    """

    if not citations:
        return "No documents retrieved."

    context_parts: list[str] = []

    for citation in citations[:5]:
        document = citation.get("document", "Unknown")
        page = citation.get("page", 0)
        authority = citation.get("authority", 50)
        excerpt = citation.get("excerpt", "")

        context_parts.append(
            f"- {document} "
            f"(Page {page}, Authority: {authority}): "
            f"{excerpt}"
        )

    return "\n".join(context_parts)


def _build_data_context(structured_data: dict) -> str:
    """
    Convert structured tool results into concise LLM context.
    """

    context: list[str] = []

    # --------------------------------------------------------
    # Account
    # --------------------------------------------------------

    account_result = structured_data.get("account")

    if account_result:
        account = account_result.get("account", {})

        if account:
            context.append(
                "Account: "
                f"{account.get('account_name')} "
                f"({account.get('account_id')}) - "
                f"Plan: {account.get('plan')}"
            )

    # --------------------------------------------------------
    # Single Order
    # --------------------------------------------------------

    order_result = structured_data.get("order")

    if order_result:
        order = order_result.get("order", {})

        if order:
            order_context = (
                f"Order: {order.get('order_id')} - "
                f"Status: {order.get('status')} - "
                f"Carrier: {order.get('carrier')} - "
                f"Fee: INR {order.get('shipment_fee_inr', 0)}"
            )

            if order.get("carrier_fault"):
                order_context += " - Carrier fault: YES"

            if order.get("customer_fault"):
                order_context += " - Customer fault: YES"

            if order.get("cancellation_requested_at"):
                order_context += (
                    " - Cancellation requested: "
                    f"{order.get('cancellation_requested_at')}"
                )

            if order.get("notes"):
                order_context += (
                    f" - Notes: {order.get('notes')}"
                )

            context.append(order_context)

    # --------------------------------------------------------
    # Multiple Orders
    # --------------------------------------------------------

    orders_result = structured_data.get("orders")

    if orders_result:
        orders = orders_result.get("orders", [])

        if orders:
            context.append(
                f"Orders for account ({len(orders)} total):"
            )

            for order in orders[:10]:
                line = (
                    f"  - {order.get('order_id')}: "
                    f"{order.get('status')}, "
                    f"Carrier: {order.get('carrier')}, "
                    f"Fee: INR {order.get('shipment_fee_inr', 0)}"
                )

                if order.get("carrier_fault"):
                    line += " [CARRIER FAULT]"

                context.append(line)

    # --------------------------------------------------------
    # Single Ticket
    # --------------------------------------------------------

    ticket_result = structured_data.get("ticket")

    if ticket_result:
        ticket = ticket_result.get("ticket", {})

        if ticket:
            ticket_context = (
                f"Ticket: {ticket.get('ticket_id')} - "
                f"Status: {ticket.get('status')} - "
                f"Subject: {ticket.get('subject')}"
            )

            if ticket.get("assigned_to"):
                ticket_context += (
                    f" - Assigned to: {ticket.get('assigned_to')}"
                )

            if ticket.get("historical_resolution"):
                ticket_context += (
                    " - Historical resolution: "
                    f"{ticket.get('historical_resolution')}"
                )

            context.append(ticket_context)

    # --------------------------------------------------------
    # Multiple Tickets
    # --------------------------------------------------------

    tickets_result = structured_data.get("tickets")

    if tickets_result:
        tickets = tickets_result.get("tickets", [])

        if tickets:
            context.append(
                f"Tickets for account ({len(tickets)} total):"
            )

            for ticket in tickets[:10]:
                line = (
                    f"  - {ticket.get('ticket_id')}: "
                    f"{ticket.get('status')}, "
                    f"Subject: {ticket.get('subject')}"
                )

                context.append(line)

    if not context:
        return "No structured data retrieved."

    return "\n".join(context)


# ============================================================
# Tool Helpers
# ============================================================

def _record_tool_call(
    state: AgentState,
    name: str,
    result: dict,
) -> None:
    """
    Store tool execution information for observability.
    """

    state.tool_calls.append(
        {
            "tool": name,
            "result": result,
        }
    )


# ============================================================
# Main Agent
# ============================================================

def run_agent(
    state: AgentState,
    repo: Repository,
    retrieval: RetrievalService,
) -> AgentState:
    """
    Execute one ParcelPilot support request.

    The agent performs:
        1. Input sanitization
        2. Entity extraction
        3. Authorization
        4. Structured-data retrieval
        5. Document retrieval
        6. LLM response generation
        7. Optional pending action creation

    State-changing actions are never directly executed here.
    They remain pending until explicitly confirmed.
    """

    query = sanitize_query(state.user_query)

    if not query:
        state.response = "Please provide a question or request."
        state.confidence = "high"
        return state

    state.user_query = query

    user = state.user

    account_id = extract_account_id(query)
    order_id = extract_order_id(query)
    ticket_id = extract_ticket_id(query)

    logger.info(
        "Agent request user=%s account=%s order=%s ticket=%s",
        user.user_id,
        account_id,
        order_id,
        ticket_id,
    )

    # ========================================================
    # Authorization
    # ========================================================

    if account_id and not can_access_account(user, account_id):
        logger.warning(
            "Unauthorized account access user=%s account=%s",
            user.user_id,
            account_id,
        )

        state.response = (
            "Access denied: you do not have permission "
            "to access this account's data."
        )
        state.confidence = "high"

        return state

    # ========================================================
    # Account
    # ========================================================

    if account_id:
        state.account_id = account_id

        result = get_account_tool(
            repo,
            user,
            account_id,
        )

        state.structured_data["account"] = result

        _record_tool_call(
            state,
            "get_account",
            result,
        )

    # ========================================================
    # Single Order
    # ========================================================

    if order_id:
        result = get_order_tool(
            repo,
            user,
            order_id,
        )

        state.structured_data["order"] = result

        _record_tool_call(
            state,
            "get_order",
            result,
        )

    # ========================================================
    # Single Ticket
    # ========================================================

    if ticket_id:
        result = get_ticket_tool(
            repo,
            user,
            ticket_id,
        )

        state.structured_data["ticket"] = result

        _record_tool_call(
            state,
            "get_ticket",
            result,
        )

    # ========================================================
    # Account-level Orders and Tickets
    # ========================================================

    if account_id and not order_id and not ticket_id:
        orders_result = get_orders_by_account_tool(
            repo,
            user,
            account_id,
        )

        state.structured_data["orders"] = orders_result

        _record_tool_call(
            state,
            "get_orders_by_account",
            orders_result,
        )

        tickets_result = get_tickets_by_account_tool(
            repo,
            user,
            account_id,
        )

        state.structured_data["tickets"] = tickets_result

        _record_tool_call(
            state,
            "get_tickets_by_account",
            tickets_result,
        )

    # ========================================================
    # Document Retrieval
    # ========================================================

    document_result = search_documents_tool(
        retrieval=retrieval,
        user=user,
        query=query,
        account_id=account_id,
    )

    state.retrieved_docs = document_result.get(
        "citations",
        [],
    )

    state.citations = document_result.get(
        "citations",
        [],
    )

    state.conflicts = document_result.get(
        "conflicts",
        [],
    )

    _record_tool_call(
        state,
        "search_documents",
        document_result,
    )

    logger.info(
        "Document retrieval results=%s conflicts=%s",
        document_result.get("result_count", 0),
        len(state.conflicts),
    )

    # ========================================================
    # Context
    # ========================================================

    data_context = _build_data_context(
        state.structured_data
    )

    document_context = _build_document_context(
        state.citations
    )

    conflict_context = (
        str(state.conflicts)
        if state.conflicts
        else "None"
    )

    # ========================================================
    # LLM
    # ========================================================

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": (
                f"User query:\n{query}\n\n"
                f"Structured data retrieved:\n"
                f"{data_context}\n\n"
                f"Documents retrieved:\n"
                f"{document_context}\n\n"
                f"Source conflicts:\n"
                f"{conflict_context}\n\n"
                "Answer the user's request directly using "
                "only the retrieved information."
            ),
        },
    ]

    llm_response = call_llm(messages)

    # ========================================================
    # State-changing Action Detection
    # ========================================================

    query_lower = query.lower()

    wants_escalation = any(
        phrase in query_lower
        for phrase in (
            "escalate",
            "escalation",
        )
    )

    if wants_escalation:
        target_ticket_id = ticket_id

        if not target_ticket_id:
            ticket_result = state.structured_data.get(
                "ticket"
            )

            if ticket_result:
                ticket = ticket_result.get(
                    "ticket",
                    {},
                )

                target_ticket_id = ticket.get(
                    "ticket_id"
                )

        if target_ticket_id:
            action_result = create_escalation_tool(
                repo=repo,
                user=user,
                ticket_id=target_ticket_id,
                reason="Customer-requested escalation",
                priority="high",
                team="Support",
            )

            state.pending_actions.append(
                action_result
            )

            _record_tool_call(
                state,
                "create_escalation",
                action_result,
            )

            # Do not execute the action.
            # The confirmation workflow must execute it later.

    # ========================================================
    # Final State
    # ========================================================

    state.response = llm_response

    if state.error:
        state.confidence = "low"

    elif not state.citations and not state.structured_data:
        state.confidence = "low"

    elif state.conflicts:
        state.confidence = "medium"

    elif state.citations or state.structured_data:
        state.confidence = "high"

    else:
        state.confidence = "medium"

    logger.info(
        "Agent completed user=%s confidence=%s "
        "citations=%s pending_actions=%s",
        user.user_id,
        state.confidence,
        len(state.citations),
        len(state.pending_actions),
    )

    return state