

# from __future__ import annotations

# from typing import Any


# # ============================================================
# # Document metadata
# # ============================================================

# DOCUMENT_METADATA: dict[str, dict[str, Any]] = {
#     "01_Support_Policy_v3_CURRENT.pdf": {
#         "document_name": "Support Policy v3",
#         "document_type": "support_policy",
#         "version": "v3",
#         "status": "CURRENT",
#         "effective_date": "2026-05-01",
#         "customer_account_id": None,
#         "source_priority": 80,
#         "section": "support_policy",
#     },
#     "02_Support_Policy_v2_DEPRECATED.pdf": {
#         "document_name": "Support Policy v2",
#         "document_type": "support_policy",
#         "version": "v2",
#         "status": "DEPRECATED",
#         "effective_date": "2025-01-01",
#         "customer_account_id": None,
#         "source_priority": 20,
#         "section": "support_policy",
#     },
#     "03_Cancellation_and_Service_Credit_SOP_v4.pdf": {
#         "document_name": "Cancellation & Service Credit SOP v4",
#         "document_type": "sop",
#         "version": "v4",
#         "status": "CURRENT",
#         "effective_date": "2026-06-15",
#         "customer_account_id": None,
#         "source_priority": 75,
#         "section": "cancellation_sop",
#     },
#     "04_Product_Operations_Guide_and_Known_Issues.pdf": {
#         "document_name": "Product Operations Guide",
#         "document_type": "product_docs",
#         "version": "current",
#         "status": "CURRENT",
#         "effective_date": "2026-08-14",
#         "customer_account_id": None,
#         "source_priority": 70,
#         "section": "product_ops",
#     },
#     "05_Northstar_Logistics_Enterprise_Agreement.pdf": {
#         "document_name": "Northstar Logistics Enterprise Agreement",
#         "document_type": "customer_agreement",
#         "version": "current",
#         "status": "ACTIVE",
#         "effective_date": "2026-01-01",
#         "customer_account_id": "ACCT-001",
#         "source_priority": 90,
#         "section": "enterprise_agreement",
#     },
#     "06_LumenWorks_Service_Agreement.pdf": {
#         "document_name": "LumenWorks Service Agreement",
#         "document_type": "customer_agreement",
#         "version": "current",
#         "status": "ACTIVE",
#         "effective_date": "2026-03-01",
#         "customer_account_id": "ACCT-002",
#         "source_priority": 85,
#         "section": "service_agreement",
#     },
# }


# ACCOUNT_TO_DOCUMENT: dict[str, str] = {
#     "ACCT-001": (
#         "05_Northstar_Logistics_Enterprise_Agreement.pdf"
#     ),
#     "ACCT-002": (
#         "06_LumenWorks_Service_Agreement.pdf"
#     ),
# }


# # ============================================================
# # Authority
# # ============================================================

# def get_authority_priority(
#     metadata: dict[str, Any],
# ) -> int:
#     """
#     Return the configured authority priority.

#     Higher value means a more authoritative source.
#     """

#     value = metadata.get(
#         "source_priority",
#         50,
#     )

#     try:
#         return int(value)
#     except (TypeError, ValueError):
#         return 50


# def get_customer_agreement_priority(
#     account_id: str,
# ) -> int:
#     """
#     Return the authority priority of an account-specific agreement.
#     """

#     document_name = ACCOUNT_TO_DOCUMENT.get(
#         account_id,
#     )

#     if not document_name:
#         return 0

#     metadata = DOCUMENT_METADATA.get(
#         document_name,
#         {},
#     )

#     return get_authority_priority(
#         metadata,
#     )


# # ============================================================
# # Source ranking
# # ============================================================

# def rank_sources(
#     sources: list[dict],
# ) -> list[dict]:
#     """
#     Rank sources by authority.

#     Current/active documents receive priority over deprecated
#     documents when authority is otherwise comparable.
#     """

#     def sort_key(source: dict) -> tuple[int, int]:
#         metadata = source.get(
#             "metadata",
#             {},
#         )

#         status = str(
#             metadata.get(
#                 "status",
#                 "unknown",
#             )
#         ).upper()

#         active_bonus = (
#             1
#             if status in {"CURRENT", "ACTIVE"}
#             else 0
#         )

#         return (
#             get_authority_priority(metadata),
#             active_bonus,
#         )

#     return sorted(
#         sources,
#         key=sort_key,
#         reverse=True,
#     )


# # ============================================================
# # Deprecated sources
# # ============================================================

# def filter_deprecated(
#     sources: list[dict],
# ) -> list[dict]:
#     """
#     Remove deprecated sources.
#     """

#     return [
#         source
#         for source in sources
#         if str(
#             source.get("metadata", {}).get(
#                 "status",
#                 "",
#             )
#         ).upper()
#         != "DEPRECATED"
#     ]


# # ============================================================
# # Conflict detection
# # ============================================================

# def detect_conflicts(
#     sources: list[dict],
# ) -> list[dict]:
#     """
#     Detect potential authority conflicts between documents.

#     Multiple chunks from the same document are not considered
#     conflicts. Conflicts are evaluated at document level.
#     """

#     conflicts: list[dict] = []

#     documents: dict[str, dict[str, dict]] = {}

#     for source in sources:
#         metadata = source.get(
#             "metadata",
#             {},
#         )

#         document_name = str(
#             metadata.get(
#                 "document_name",
#                 "unknown",
#             )
#         )

#         document_type = str(
#             metadata.get(
#                 "document_type",
#                 "unknown",
#             )
#         )

#         documents.setdefault(
#             document_type,
#             {},
#         )[document_name] = source

#     for document_type, document_map in documents.items():
#         if len(document_map) < 2:
#             continue

#         document_sources = list(
#             document_map.values()
#         )

#         priorities = [
#             get_authority_priority(
#                 source.get(
#                     "metadata",
#                     {},
#                 )
#             )
#             for source in document_sources
#         ]

#         if max(priorities) == min(priorities):
#             continue

#         highest_priority = max(priorities)

#         authoritative_sources = [
#             source
#             for source in document_sources
#             if get_authority_priority(
#                 source.get(
#                     "metadata",
#                     {},
#                 )
#             )
#             == highest_priority
#         ]

#         conflicts.append(
#             {
#                 "document_type": document_type,
#                 "sources": [
#                     source.get(
#                         "metadata",
#                         {},
#                     ).get(
#                         "document_name",
#                         "unknown",
#                     )
#                     for source in document_sources
#                 ],
#                 "highest_priority": highest_priority,
#                 "authoritative_sources": [
#                     source.get(
#                         "metadata",
#                         {},
#                     ).get(
#                         "document_name",
#                         "unknown",
#                     )
#                     for source in authoritative_sources
#                 ],
#                 "resolution": (
#                     "Use the highest-priority authoritative "
#                     "source and prefer CURRENT/ACTIVE versions."
#                 ),
#             }
#         )

#     return conflicts




from __future__ import annotations

from typing import Any


# ============================================================
# Document metadata
# ============================================================

DOCUMENT_METADATA: dict[str, dict[str, Any]] = {
    "01_Support_Policy_v3_CURRENT.pdf": {
        "document_name": "Support Policy v3",
        "document_type": "support_policy",
        "version": "v3",
        "status": "CURRENT",
        "effective_date": "2026-05-01",
        "customer_account_id": None,
        "source_priority": 80,
        "section": "support_policy",
    },
    "02_Support_Policy_v2_DEPRECATED.pdf": {
        "document_name": "Support Policy v2",
        "document_type": "support_policy",
        "version": "v2",
        "status": "DEPRECATED",
        "effective_date": "2025-01-01",
        "customer_account_id": None,
        "source_priority": 20,
        "section": "support_policy",
    },
    "03_Cancellation_and_Service_Credit_SOP_v4.pdf": {
        "document_name": "Cancellation & Service Credit SOP v4",
        "document_type": "sop",
        "version": "v4",
        "status": "CURRENT",
        "effective_date": "2026-06-15",
        "customer_account_id": None,
        "source_priority": 75,
        "section": "cancellation_sop",
    },
    "04_Product_Operations_Guide_and_Known_Issues.pdf": {
        "document_name": "Product Operations Guide",
        "document_type": "product_docs",
        "version": "current",
        "status": "CURRENT",
        "effective_date": "2026-08-14",
        "customer_account_id": None,
        "source_priority": 70,
        "section": "product_ops",
    },
    "05_Northstar_Logistics_Enterprise_Agreement.pdf": {
        "document_name": "Northstar Logistics Enterprise Agreement",
        "document_type": "customer_agreement",
        "version": "current",
        "status": "ACTIVE",
        "effective_date": "2026-01-01",
        "customer_account_id": "ACCT-001",
        "source_priority": 90,
        "section": "enterprise_agreement",
    },
    "06_LumenWorks_Service_Agreement.pdf": {
        "document_name": "LumenWorks Service Agreement",
        "document_type": "customer_agreement",
        "version": "current",
        "status": "ACTIVE",
        "effective_date": "2026-03-01",
        "customer_account_id": "ACCT-002",
        "source_priority": 85,
        "section": "service_agreement",
    },
}


ACCOUNT_TO_DOCUMENT: dict[str, str] = {
    "ACCT-001": (
        "05_Northstar_Logistics_Enterprise_Agreement.pdf"
    ),
    "ACCT-002": (
        "06_LumenWorks_Service_Agreement.pdf"
    ),
}


# ============================================================
# Authority
# ============================================================

def get_authority_priority(
    metadata: dict[str, Any],
) -> int:
    """
    Return the configured authority priority.

    Higher value means a more authoritative source.
    """

    value = metadata.get(
        "source_priority",
        50,
    )

    try:
        return int(value)
    except (TypeError, ValueError):
        return 50


def get_customer_agreement_priority(
    account_id: str,
) -> int:
    """
    Return the authority priority of an account-specific agreement.
    """

    document_name = ACCOUNT_TO_DOCUMENT.get(
        account_id,
    )

    if not document_name:
        return 0

    metadata = DOCUMENT_METADATA.get(
        document_name,
        {},
    )

    return get_authority_priority(
        metadata,
    )


# ============================================================
# Source ranking
# ============================================================

def rank_sources(
    sources: list[dict],
) -> list[dict]:
    """
    Rank sources by authority.

    Current/active documents receive priority over deprecated
    documents when authority is otherwise comparable.
    """

    def sort_key(source: dict) -> tuple[int, int]:
        metadata = source.get(
            "metadata",
            {},
        )

        status = str(
            metadata.get(
                "status",
                "unknown",
            )
        ).upper()

        active_bonus = (
            1
            if status in {"CURRENT", "ACTIVE"}
            else 0
        )

        return (
            get_authority_priority(metadata),
            active_bonus,
        )

    return sorted(
        sources,
        key=sort_key,
        reverse=True,
    )


# ============================================================
# Deprecated sources
# ============================================================

def filter_deprecated(
    sources: list[dict],
) -> list[dict]:
    """
    Remove deprecated sources.
    """

    return [
        source
        for source in sources
        if str(
            source.get("metadata", {}).get(
                "status",
                "",
            )
        ).upper()
        != "DEPRECATED"
    ]


# ============================================================
# Conflict detection
# ============================================================

def detect_conflicts(
    sources: list[dict],
) -> list[dict]:
    """
    Detect potential authority conflicts between documents.

    Skips deprecated documents and only flags conflicts when 
    competing documents have differing active statuses or priorities.
    """

    conflicts: list[dict] = []

    documents: dict[str, dict[str, dict]] = {}

    for source in sources:
        metadata = source.get(
            "metadata",
            {},
        )

        # Skip deprecated documents from triggering conflicts
        if str(metadata.get("status", "")).upper() == "DEPRECATED":
            continue

        document_name = str(
            metadata.get(
                "document_name",
                "unknown",
            )
        )

        document_type = str(
            metadata.get(
                "document_type",
                "unknown",
            )
        )

        documents.setdefault(
            document_type,
            {},
        )[document_name] = source

    for document_type, document_map in documents.items():
        if len(document_map) < 2:
            continue

        document_sources = list(
            document_map.values()
        )

        statuses = {
            str(source.get("metadata", {}).get("status", "")).upper()
            for source in document_sources
        }

        if len(statuses) <= 1:
            continue

        priorities = [
            get_authority_priority(
                source.get(
                    "metadata",
                    {},
                )
            )
            for source in document_sources
        ]

        if max(priorities) == min(priorities):
            continue

        highest_priority = max(priorities)

        authoritative_sources = [
            source
            for source in document_sources
            if get_authority_priority(
                source.get(
                    "metadata",
                    {},
                )
            )
            == highest_priority
        ]

        conflicts.append(
            {
                "document_type": document_type,
                "sources": [
                    source.get(
                        "metadata",
                        {},
                    ).get(
                        "document_name",
                        "unknown",
                    )
                    for source in document_sources
                ],
                "highest_priority": highest_priority,
                "authoritative_sources": [
                    source.get(
                        "metadata",
                        {},
                    ).get(
                        "document_name",
                        "unknown",
                    )
                    for source in authoritative_sources
                ],
                "resolution": (
                    "Use the highest-priority authoritative "
                    "source and prefer CURRENT/ACTIVE versions."
                ),
            }
        )

    return conflicts