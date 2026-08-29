

from __future__ import annotations

from typing import Optional

from app.services.reliability import (
    ACCOUNT_TO_DOCUMENT,
    detect_conflicts,
    filter_deprecated,
    get_authority_priority,
    rank_sources,
)
from app.vector.store import VectorStore


class RetrievalService:
    """
    Retrieval layer for ParcelPilot.

    Responsibilities:
    - Query Qdrant through VectorStore.
    - Apply account-level access filtering.
    - Remove deprecated sources when requested.
    - Rank sources by authority.
    - Prefer customer-specific agreements.
    - Produce citation-ready results.
    - Surface potential source conflicts.
    """

    def __init__(
        self,
        vector_store: VectorStore,
    ):
        self.vector_store = vector_store

    # =========================================================
    # Public search
    # =========================================================

    def search_documents(
        self,
        query: str,
        account_id: Optional[str] = None,
        include_deprecated: bool = False,
        n_results: int = 10,
    ) -> dict:
        """
        Search document chunks relevant to a user query.

        Account-specific documents are available only to their
        corresponding account. General documents remain available
        to all accounts.
        """

        query = query.strip()

        if not query:
            return {
                "results": [],
                "citations": [],
                "conflicts": [],
                "query": query,
                "account_id": account_id,
            }

        if n_results <= 0:
            return {
                "results": [],
                "citations": [],
                "conflicts": [],
                "query": query,
                "account_id": account_id,
            }

        # Retrieve extra candidates because filtering and
        # authority ranking happen after vector search.
        candidate_count = max(
            n_results * 3,
            20,
        )

        raw_results = self.vector_store.search(
            query=query,
            top_k=candidate_count,
        )

        # -----------------------------------------------------
        # Account-level filtering
        # -----------------------------------------------------

        raw_results = self._filter_by_account(
            raw_results,
            account_id=account_id,
        )

        # -----------------------------------------------------
        # Deprecated filtering
        # -----------------------------------------------------

        if not include_deprecated:
            raw_results = filter_deprecated(
                raw_results,
            )

        # -----------------------------------------------------
        # Customer agreement prioritization
        # -----------------------------------------------------

        raw_results = self._prioritize_customer_agreement(
            raw_results,
            account_id=account_id,
        )

        # -----------------------------------------------------
        # Authority ranking
        # -----------------------------------------------------

        ranked = rank_sources(
            raw_results,
        )

        # Remove duplicate source chunks only when they have
        # the exact same source ID.
        ranked = self._deduplicate_results(
            ranked,
        )

        ranked = ranked[:n_results]

        # -----------------------------------------------------
        # Conflict detection
        # -----------------------------------------------------

        conflicts = detect_conflicts(
            ranked,
        )

        # -----------------------------------------------------
        # Citations
        # -----------------------------------------------------

        citations = [
            self._build_citation(result)
            for result in ranked
        ]

        return {
            "results": ranked,
            "citations": citations,
            "conflicts": conflicts,
            "query": query,
            "account_id": account_id,
        }

    # =========================================================
    # Account filtering
    # =========================================================

    @staticmethod
    def _filter_by_account(
        results: list[dict],
        account_id: Optional[str],
    ) -> list[dict]:
        """
        Keep:
        - general documents
        - documents belonging to the requested account

        Reject:
        - another customer's agreement.
        """

        if not account_id:
            return results

        filtered: list[dict] = []

        for result in results:
            metadata = result.get(
                "metadata",
                {},
            )

            document_account_id = metadata.get(
                "customer_account_id",
            )

            # General document.
            if document_account_id in (
                None,
                "",
            ):
                filtered.append(result)
                continue

            # Account-specific document.
            if document_account_id == account_id:
                filtered.append(result)

        return filtered

    # =========================================================
    # Customer agreement prioritization
    # =========================================================

    @staticmethod
    def _prioritize_customer_agreement(
        results: list[dict],
        account_id: Optional[str],
    ) -> list[dict]:
        """
        Ensure the customer's agreement is considered before
        generic documents when the query returns both.
        """

        if not account_id:
            return results

        agreement_file = ACCOUNT_TO_DOCUMENT.get(
            account_id,
        )

        if not agreement_file:
            return results

        agreement_results: list[dict] = []
        general_results: list[dict] = []

        for result in results:
            metadata = result.get(
                "metadata",
                {},
            )

            source_file = metadata.get(
                "source_file",
            )

            if source_file == agreement_file:
                agreement_results.append(result)
            else:
                general_results.append(result)

        return agreement_results + general_results

    # =========================================================
    # Deduplication
    # =========================================================

    @staticmethod
    def _deduplicate_results(
        results: list[dict],
    ) -> list[dict]:
        """
        Remove exact duplicate source IDs while preserving order.
        """

        seen: set[str] = set()
        unique_results: list[dict] = []

        for result in results:
            source_id = result.get("id")

            if source_id is None:
                unique_results.append(result)
                continue

            source_id = str(source_id)

            if source_id in seen:
                continue

            seen.add(source_id)
            unique_results.append(result)

        return unique_results

    # =========================================================
    # Citations
    # =========================================================

    @staticmethod
    def _build_citation(
        result: dict,
    ) -> dict:
        """
        Convert a retrieval result into a citation object.
        """

        metadata = result.get(
            "metadata",
            {},
        )

        text = str(
            result.get(
                "text",
                "",
            )
        )

        return {
            "document": metadata.get(
                "document_name",
                "unknown",
            ),
            "source_file": metadata.get(
                "source_file",
                "unknown",
            ),
            "page": metadata.get(
                "page_number",
                0,
            ),
            "section": metadata.get(
                "section",
                "general",
            ),
            "source_type": metadata.get(
                "document_type",
                "unknown",
            ),
            "authority": get_authority_priority(
                metadata,
            ),
            "status": metadata.get(
                "status",
                "unknown",
            ),
            "version": metadata.get(
                "version",
                "unknown",
            ),
            "customer_account_id": metadata.get(
                "customer_account_id",
            ),
            "score": result.get(
                "score",
                0.0,
            ),
            "excerpt": text[:300],
        }