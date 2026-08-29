from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from app.data.models import Ticket
from app.data.repository import Repository


class IssueDetectionService:
    """
    Detect operational and customer-support issues from ParcelPilot data.

    Detection categories:
    - SLA breaches
    - Repeated complaints
    - Carrier fault patterns
    - High-severity unresolved tickets
    - Unusual cancellation patterns
    """

    SLA_THRESHOLDS = {
        "Enterprise": {
            "P1": 0.25,
            "P2": 2.0,
            "P3": 8.0,
        },
        "Growth": {
            "P1": 2.0,
            "P2": 4.0,
            "P3": 16.0,
        },
        "Standard": {
            "P1": 4.0,
            "P2": 8.0,
            "P3": 16.0,
        },
    }

    HIGH_SEVERITY_KEYWORDS = (
        "security",
        "api key",
        "exposure",
        "outage",
        "failing",
        "failure",
        "breach",
        "compromised",
    )

    P1_KEYWORDS = (
        "security",
        "api key",
        "exposure",
        "outage",
        "breach",
        "compromised",
    )

    P3_KEYWORDS = (
        "how do",
        "how to",
        "question",
        "information",
    )

    def __init__(self, repo: Repository):
        self.repo = repo

    # =========================================================
    # Public API
    # =========================================================

    def detect_issues(
        self,
        user_id: Optional[str] = None,
    ) -> list[dict]:
        """
        Detect all relevant operational issues.

        If user_id is provided, it is treated as an account ID and
        issue detection is restricted to that account where possible.
        """

        issues: list[dict] = []

        issues.extend(
            self._detect_sla_breaches(
                account_id=user_id,
            )
        )

        issues.extend(
            self._detect_repeated_complaints(
                account_id=user_id,
            )
        )

        issues.extend(
            self._detect_carrier_issues(
                account_id=user_id,
            )
        )

        issues.extend(
            self._detect_high_severity_unresolved(
                account_id=user_id,
            )
        )

        issues.extend(
            self._detect_unusual_patterns(
                account_id=user_id,
            )
        )

        return issues

    # =========================================================
    # Severity helpers
    # =========================================================

    @classmethod
    def _classify_ticket_severity(
        cls,
        ticket: Ticket,
    ) -> str:
        """
        Classify a ticket into P1/P2/P3 using deterministic rules.

        This is intentionally rule-based. The LLM/agent layer can
        perform richer classification later without coupling it to
        the database service.
        """

        subject = (ticket.subject or "").strip().lower()
        description = (ticket.description or "").strip().lower()

        text = f"{subject} {description}"

        if any(keyword in text for keyword in cls.P1_KEYWORDS):
            return "P1"

        if any(
            keyword in text
            for keyword in (
                "failing",
                "failure",
                "degraded",
                "down",
                "blocked",
            )
        ):
            return "P1"

        if any(keyword in text for keyword in cls.P3_KEYWORDS):
            return "P3"

        return "P2"

    @staticmethod
    def _hours_open(
        created_at: datetime,
    ) -> float:
        """
        Return ticket age in hours.
        """

        now = datetime.now(timezone.utc)

        if created_at.tzinfo is None:
            created_at = created_at.replace(
                tzinfo=timezone.utc,
            )

        return max(
            0.0,
            (now - created_at).total_seconds() / 3600,
        )

    # =========================================================
    # SLA breaches
    # =========================================================

    def _detect_sla_breaches(
        self,
        account_id: Optional[str] = None,
    ) -> list[dict]:
        issues: list[dict] = []

        tickets = self.repo.get_open_tickets()

        for ticket in tickets:
            if (
                account_id
                and ticket.account_id != account_id
            ):
                continue

            if ticket.created_at is None:
                continue

            account = self.repo.get_account(
                ticket.account_id,
            )

            if account is None:
                continue

            severity_level = self._classify_ticket_severity(
                ticket,
            )

            thresholds = self.SLA_THRESHOLDS.get(
                account.plan,
                self.SLA_THRESHOLDS["Standard"],
            )

            threshold_hours = thresholds.get(
                severity_level,
                self.SLA_THRESHOLDS["Standard"]["P2"],
            )

            hours_open = self._hours_open(
                ticket.created_at,
            )

            if hours_open < threshold_hours:
                continue

            issue_severity = (
                "urgent"
                if severity_level == "P1"
                else "high"
                if severity_level == "P2"
                else "medium"
            )

            issues.append(
                {
                    "type": "sla_breach",
                    "severity": issue_severity,
                    "ticket_id": ticket.ticket_id,
                    "account_id": ticket.account_id,
                    "account_name": account.account_name,
                    "subject": ticket.subject,
                    "severity_level": severity_level,
                    "sla_threshold_hours": threshold_hours,
                    "hours_open": round(hours_open, 2),
                    "created_at": ticket.created_at,
                    "message": (
                        f"{ticket.ticket_id} "
                        f"({account.account_name}) exceeded "
                        f"the {severity_level} SLA of "
                        f"{threshold_hours} hours "
                        f"(open for {hours_open:.2f} hours)"
                    ),
                }
            )

        return issues

    # =========================================================
    # Repeated complaints
    # =========================================================

    def _detect_repeated_complaints(
        self,
        account_id: Optional[str] = None,
    ) -> list[dict]:
        issues: list[dict] = []

        tickets = self.repo.get_all_tickets()

        subject_groups: dict[str, list[Ticket]] = {}

        for ticket in tickets:
            if (
                account_id
                and ticket.account_id != account_id
            ):
                continue

            subject = (ticket.subject or "").strip()

            if not subject:
                continue

            key = " ".join(subject.lower().split())

            subject_groups.setdefault(
                key,
                [],
            ).append(ticket)

        for subject, group in subject_groups.items():
            if len(group) < 2:
                continue

            accounts = {
                ticket.account_id
                for ticket in group
            }

            severity = (
                "high"
                if len(accounts) >= 2
                else "medium"
            )

            issues.append(
                {
                    "type": "repeated_complaint",
                    "severity": severity,
                    "subject": subject,
                    "count": len(group),
                    "accounts": sorted(accounts),
                    "ticket_ids": [
                        ticket.ticket_id
                        for ticket in group
                    ],
                    "message": (
                        f"Repeated complaint '{subject}' "
                        f"reported across {len(group)} tickets "
                        f"from {len(accounts)} account(s)"
                    ),
                }
            )

        return issues

    # =========================================================
    # Carrier issues
    # =========================================================

    def _detect_carrier_issues(
        self,
        account_id: Optional[str] = None,
    ) -> list[dict]:
        issues: list[dict] = []

        orders = self.repo.get_all_orders()

        carrier_faults: dict[str, list] = {}

        for order in orders:
            if (
                account_id
                and order.account_id != account_id
            ):
                continue

            if not order.carrier_fault:
                continue

            carrier = (
                order.carrier.strip()
                if order.carrier
                else "Unknown"
            )

            carrier_faults.setdefault(
                carrier,
                [],
            ).append(order)

        for carrier, fault_orders in carrier_faults.items():
            affected_accounts = {
                order.account_id
                for order in fault_orders
            }

            # Avoid generating noisy carrier alerts for
            # a single isolated fault.
            if len(fault_orders) < 2:
                continue

            issues.append(
                {
                    "type": "carrier_issue",
                    "severity": "high",
                    "carrier": carrier,
                    "fault_count": len(fault_orders),
                    "affected_accounts": sorted(
                        affected_accounts,
                    ),
                    "order_ids": [
                        order.order_id
                        for order in fault_orders
                    ],
                    "message": (
                        f"Carrier {carrier} has "
                        f"{len(fault_orders)} orders with "
                        f"reported faults affecting "
                        f"{len(affected_accounts)} accounts"
                    ),
                }
            )

        return issues

    # =========================================================
    # High-severity unresolved tickets
    # =========================================================

    def _detect_high_severity_unresolved(
        self,
        account_id: Optional[str] = None,
    ) -> list[dict]:
        issues: list[dict] = []

        tickets = self.repo.get_open_tickets()

        for ticket in tickets:
            if (
                account_id
                and ticket.account_id != account_id
            ):
                continue

            subject = (
                ticket.subject or ""
            ).strip().lower()

            description = (
                ticket.description or ""
            ).strip().lower()

            text = f"{subject} {description}"

            if not any(
                keyword in text
                for keyword in self.HIGH_SEVERITY_KEYWORDS
            ):
                continue

            issues.append(
                {
                    "type": "high_severity_unresolved",
                    "severity": "urgent",
                    "ticket_id": ticket.ticket_id,
                    "account_id": ticket.account_id,
                    "subject": ticket.subject,
                    "assigned_to": ticket.assigned_to,
                    "created_at": ticket.created_at,
                    "message": (
                        f"URGENT: High-severity ticket "
                        f"{ticket.ticket_id} remains open: "
                        f"{ticket.subject}"
                    ),
                }
            )

        return issues

    # =========================================================
    # Unusual patterns
    # =========================================================

    def _detect_unusual_patterns(
        self,
        account_id: Optional[str] = None,
    ) -> list[dict]:
        issues: list[dict] = []

        orders = self.repo.get_all_orders()

        filtered_orders = [
            order
            for order in orders
            if (
                not account_id
                or order.account_id == account_id
            )
        ]

        cancellations = [
            order
            for order in filtered_orders
            if order.cancellation_requested_at
        ]

        # Keep this deterministic and conservative.
        if len(cancellations) >= 3:
            affected_accounts = {
                order.account_id
                for order in cancellations
            }

            issues.append(
                {
                    "type": "unusual_pattern",
                    "severity": "medium",
                    "pattern": "high_cancellation_activity",
                    "count": len(cancellations),
                    "affected_accounts": sorted(
                        affected_accounts,
                    ),
                    "order_ids": [
                        order.order_id
                        for order in cancellations
                    ],
                    "message": (
                        f"High cancellation activity: "
                        f"{len(cancellations)} orders have "
                        f"cancellation requests"
                    ),
                }
            )

        return issues