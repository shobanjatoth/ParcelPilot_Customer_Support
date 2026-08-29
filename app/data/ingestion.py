from __future__ import annotations

import os
import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.data.models import Account, Order, Ticket
from app.services.reliability import DOCUMENT_METADATA
from app.vector.store import VectorStore


# ============================================================
# Paths
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
    )
)

RAW_DIR = os.path.join(
    BASE_DIR,
    "data",
    "raw",
)

EXCEL_FILE = "ParcelPilot_Assessment_Data.xlsx"


PDF_FILES = [
    "01_Support_Policy_v3_CURRENT.pdf",
    "02_Support_Policy_v2_DEPRECATED.pdf",
    "03_Cancellation_and_Service_Credit_SOP_v4.pdf",
    "04_Product_Operations_Guide_and_Known_Issues.pdf",
    "05_Northstar_Logistics_Enterprise_Agreement.pdf",
    "06_LumenWorks_Service_Agreement.pdf",
]


# ============================================================
# Excel Helpers
# ============================================================

def _find_sheet(
    workbook,
    preferred_names: list[str],
) -> str | None:

    # Exact match first
    for name in preferred_names:
        if name in workbook.sheetnames:
            return name

    # Partial match
    for sheet_name in workbook.sheetnames:

        lower_name = sheet_name.lower()

        for preferred in preferred_names:

            if preferred.lower() in lower_name:
                return sheet_name

    return None


def _read_sheet_rows(
    sheet,
) -> list[dict[str, Any]]:

    rows = list(
        sheet.iter_rows(
            values_only=True
        )
    )

    if not rows:
        return []

    headers = [
        str(header).strip()
        if header is not None
        else ""
        for header in rows[0]
    ]

    result: list[dict[str, Any]] = []

    for row in rows[1:]:

        if not any(
            value is not None
            for value in row
        ):
            continue

        data = dict(
            zip(
                headers,
                row,
            )
        )

        result.append(data)

    return result


# ============================================================
# Utility
# ============================================================

def _string_or_none(
    value: Any,
) -> str | None:

    if value is None:
        return None

    return str(value)


# ============================================================
# Excel → PostgreSQL
# ============================================================

def ingest_excel(
    db: Session,
) -> None:
    """
    Read the ParcelPilot Excel dataset and insert/update
    Accounts, Orders and Tickets in PostgreSQL.

    openpyxl is imported lazily so importing this module
    does not load Excel dependencies unnecessarily.
    """

    # --------------------------------------------------------
    # Lazy import
    # --------------------------------------------------------

    import openpyxl

    path = os.path.join(
        RAW_DIR,
        EXCEL_FILE,
    )

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Excel file not found: {path}"
        )

    print(
        f"Reading Excel: {path}"
    )

    workbook = openpyxl.load_workbook(
        path,
        data_only=True,
    )

    try:

        # ====================================================
        # Accounts
        # ====================================================

        accounts_sheet = _find_sheet(
            workbook,
            [
                "accounts",
                "account",
            ],
        )

        if accounts_sheet:

            rows = _read_sheet_rows(
                workbook[accounts_sheet]
            )

            for data in rows:

                account_id = data.get(
                    "account_id"
                )

                if not account_id:
                    continue

                account = Account(
                    account_id=str(
                        account_id
                    ),
                    account_name=str(
                        data.get(
                            "account_name",
                            "",
                        )
                    ),
                    plan=str(
                        data.get(
                            "plan",
                            "",
                        )
                    ),
                    status=str(
                        data.get(
                            "status",
                            "active",
                        )
                    ),
                    csm=(
                        str(data["csm"])
                        if data.get("csm")
                        else None
                    ),
                    contract_file=(
                        str(
                            data["contract_file"]
                        )
                        if data.get(
                            "contract_file"
                        )
                        else None
                    ),
                    premium_support=bool(
                        data.get(
                            "premium_support",
                            False,
                        )
                    ),
                    notes=(
                        str(data["notes"])
                        if data.get("notes")
                        else None
                    ),
                )

                db.merge(account)

            print(
                f"Accounts ingested: {len(rows)}"
            )

        # ====================================================
        # Orders
        # ====================================================

        orders_sheet = _find_sheet(
            workbook,
            [
                "orders",
                "order",
            ],
        )

        if orders_sheet:

            rows = _read_sheet_rows(
                workbook[orders_sheet]
            )

            for data in rows:

                order_id = data.get(
                    "order_id"
                )

                if not order_id:
                    continue

                order = Order(
                    order_id=str(
                        order_id
                    ),
                    account_id=str(
                        data.get(
                            "account_id",
                            "",
                        )
                    ),
                    carrier=str(
                        data.get(
                            "carrier",
                            "",
                        )
                    ),
                    status=str(
                        data.get(
                            "status",
                            "",
                        )
                    ),
                    booked_at=_string_or_none(
                        data.get(
                            "booked_at"
                        )
                    ),
                    pickup_window_start=(
                        _string_or_none(
                            data.get(
                                "pickup_window_start"
                            )
                        )
                    ),
                    pickup_window_end=(
                        _string_or_none(
                            data.get(
                                "pickup_window_end"
                            )
                        )
                    ),
                    pickup_actual_at=(
                        _string_or_none(
                            data.get(
                                "pickup_actual_at"
                            )
                        )
                    ),
                    shipment_fee_inr=float(
                        data.get(
                            "shipment_fee_inr",
                            0,
                        )
                        or 0
                    ),
                    carrier_fault=bool(
                        data.get(
                            "carrier_fault",
                            False,
                        )
                    ),
                    customer_fault=bool(
                        data.get(
                            "customer_fault",
                            False,
                        )
                    ),
                    cancellation_requested_at=(
                        _string_or_none(
                            data.get(
                                "cancellation_requested_at"
                            )
                        )
                    ),
                    notes=_string_or_none(
                        data.get("notes")
                    ),
                )

                db.merge(order)

            print(
                f"Orders ingested: {len(rows)}"
            )

        # ====================================================
        # Tickets
        # ====================================================

        tickets_sheet = _find_sheet(
            workbook,
            [
                "tickets",
                "ticket",
            ],
        )

        if tickets_sheet:

            rows = _read_sheet_rows(
                workbook[tickets_sheet]
            )

            for data in rows:

                ticket_id = data.get(
                    "ticket_id"
                )

                if not ticket_id:
                    continue

                ticket = Ticket(
                    ticket_id=str(
                        ticket_id
                    ),
                    account_id=str(
                        data.get(
                            "account_id",
                            "",
                        )
                    ),
                    created_at=_string_or_none(
                        data.get(
                            "created_at"
                        )
                    ),
                    status=str(
                        data.get(
                            "status",
                            "open",
                        )
                    ),
                    subject=_string_or_none(
                        data.get("subject")
                    ),
                    description=_string_or_none(
                        data.get("description")
                    ),
                    channel=_string_or_none(
                        data.get("channel")
                    ),
                    assigned_to=_string_or_none(
                        data.get("assigned_to")
                    ),
                    last_customer_message_at=(
                        _string_or_none(
                            data.get(
                                "last_customer_message_at"
                            )
                        )
                    ),
                    historical_resolution=(
                        _string_or_none(
                            data.get(
                                "historical_resolution"
                            )
                        )
                    ),
                )

                db.merge(ticket)

            print(
                f"Tickets ingested: {len(rows)}"
            )

        # ----------------------------------------------------
        # Commit
        # ----------------------------------------------------

        db.commit()

        print(
            "Excel → PostgreSQL complete."
        )

    except Exception:

        db.rollback()

        raise

    finally:

        workbook.close()


# ============================================================
# PDF Chunking
# ============================================================

def _chunk_text(
    text: str,
    max_chars: int = 1500,
    overlap: int = 200,
) -> list[str]:
    """
    Split PDF text into overlapping chunks.

    Same chunking strategy as the original application.
    """

    text = text.strip()

    if not text:
        return []

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split(
            "\n\n"
        )
        if paragraph.strip()
    ]

    chunks: list[str] = []

    current = ""

    for paragraph in paragraphs:

        # ----------------------------------------------------
        # Add paragraph to current chunk
        # ----------------------------------------------------

        if (
            len(current)
            + len(paragraph)
            + 2
            <= max_chars
        ):

            if current:
                current += "\n\n"

            current += paragraph

        # ----------------------------------------------------
        # Current chunk is full
        # ----------------------------------------------------

        else:

            if current:
                chunks.append(
                    current
                )

            # Preserve overlap
            if overlap > 0 and current:

                overlap_text = current[
                    max(
                        0,
                        len(current) - overlap,
                    ):
                ]

                current = (
                    overlap_text
                    + "\n\n"
                    + paragraph
                )

            else:

                current = paragraph

    # --------------------------------------------------------
    # Final chunk
    # --------------------------------------------------------

    if current:
        chunks.append(current)

    return chunks


# ============================================================
# PDFs → Qdrant
# ============================================================

def ingest_pdfs(
    vector_store: VectorStore,
) -> None:
    """
    Read the ParcelPilot PDF knowledge base,
    create chunks and store embeddings in Qdrant.

    PyMuPDF is imported lazily to keep application startup
    lightweight.
    """

    # --------------------------------------------------------
    # Lazy import
    # --------------------------------------------------------

    import pymupdf

    total_chunks = 0

    for pdf_file in PDF_FILES:

        path = os.path.join(
            RAW_DIR,
            pdf_file,
        )

        # ----------------------------------------------------
        # Missing file
        # ----------------------------------------------------

        if not os.path.exists(path):

            print(
                f"Skipping missing PDF: "
                f"{pdf_file}"
            )

            continue

        metadata = DOCUMENT_METADATA.get(
            pdf_file,
            {},
        )

        print(
            f"Processing PDF: {pdf_file}"
        )

        # ----------------------------------------------------
        # Open PDF
        # ----------------------------------------------------

        document = pymupdf.open(path)

        try:

            chunks: list[
                dict[str, Any]
            ] = []

            # =================================================
            # Process pages
            # =================================================

            for page_index in range(
                len(document)
            ):

                page_number = (
                    page_index + 1
                )

                page = document[
                    page_index
                ]

                text = page.get_text()

                if not text.strip():
                    continue

                page_chunks = _chunk_text(
                    text
                )

                # ------------------------------------------------
                # Process chunks
                # ------------------------------------------------

                for (
                    chunk_index,
                    chunk,
                ) in enumerate(
                    page_chunks
                ):

                    if len(
                        chunk.strip()
                    ) < 20:
                        continue

                    source_id = (
                        f"{pdf_file}:"
                        f"p{page_number}:"
                        f"c{chunk_index}"
                    )

                    # Deterministic UUID
                    chunk_uuid = str(
                        uuid.uuid5(
                            uuid.NAMESPACE_URL,
                            source_id,
                        )
                    )

                    chunk_metadata = {
                        "document_name": metadata.get(
                            "document_name",
                            pdf_file,
                        ),
                        "document_type": metadata.get(
                            "document_type",
                            "unknown",
                        ),
                        "version": metadata.get(
                            "version",
                            "unknown",
                        ),
                        "status": metadata.get(
                            "status",
                            "unknown",
                        ),
                        "effective_date": metadata.get(
                            "effective_date",
                            "unknown",
                        ),
                        "customer_account_id": (
                            metadata.get(
                                "customer_account_id"
                            )
                        ),
                        "source_priority": metadata.get(
                            "source_priority",
                            50,
                        ),
                        "section": metadata.get(
                            "section",
                            "general",
                        ),
                        "page_number": page_number,
                        "source_file": pdf_file,
                        "chunk_index": chunk_index,
                    }

                    chunks.append(
                        {
                            "id": chunk_uuid,
                            "text": chunk,
                            "metadata": chunk_metadata,
                        }
                    )

            # =================================================
            # Send chunks to Qdrant
            # =================================================

            if chunks:

                vector_store.add_documents(
                    chunks
                )

                total_chunks += len(
                    chunks
                )

                print(
                    f"  Added "
                    f"{len(chunks)} chunks"
                )

        finally:

            # Always close PDF
            document.close()

            # Release reference
            del document

    print(
        "PDF → Qdrant complete. "
        f"Total chunks: {total_chunks}"
    )


# ============================================================
# Complete Ingestion
# ============================================================

def run_ingestion(
    db: Session,
    vector_store: VectorStore,
) -> None:
    """
    Run the complete ParcelPilot ingestion pipeline.

    1. Excel → PostgreSQL
    2. PDFs → Qdrant
    """

    print("=" * 60)
    print(
        "PARCELPILOT DATA INGESTION"
    )
    print("=" * 60)

    # --------------------------------------------------------
    # Excel
    # --------------------------------------------------------

    print(
        "\n[1/2] Excel → PostgreSQL"
    )

    ingest_excel(db)

    # --------------------------------------------------------
    # PDFs
    # --------------------------------------------------------

    print(
        "\n[2/2] PDFs → Qdrant Cloud"
    )

    ingest_pdfs(
        vector_store
    )

    # --------------------------------------------------------
    # Complete
    # --------------------------------------------------------

    print(
        "\n"
        + "=" * 60
    )

    print(
        "INGESTION COMPLETE"
    )

    print(
        "=" * 60
    )
