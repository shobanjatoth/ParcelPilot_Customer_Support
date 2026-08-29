
from __future__ import annotations

from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)

from sentence_transformers import SentenceTransformer

from app.config import settings


class VectorStore:
    """
    Qdrant Cloud vector store for ParcelPilot.

    Responsibilities:
    - Connect to Qdrant Cloud
    - Create the document collection if required
    - Generate embeddings
    - Store document chunks
    - Perform semantic search
    """

    def __init__(
        self,
        collection_name: str | None = None,
    ):
        self.collection_name = (
            collection_name or settings.qdrant_collection
        )

        # -----------------------------------------------------
        # Embedding model
        # -----------------------------------------------------

        self.embedding_model = SentenceTransformer(
            settings.embedding_model
        )

        # -----------------------------------------------------
        # Qdrant Cloud client
        # -----------------------------------------------------

        self.client = QdrantClient(
            url=settings.qdrant_endpoint,
            api_key=settings.qdrant_api,
        )

        # all-MiniLM-L6-v2 → 384 dimensions
        self.vector_size = (self.embedding_model.get_embedding_dimension())

        if self.vector_size is None:
            raise RuntimeError(
                "Unable to determine embedding dimension."
            )

        # -----------------------------------------------------
        # Ensure collection exists
        # -----------------------------------------------------

        self._ensure_collection()

    # =========================================================
    # Collection
    # =========================================================

    def _ensure_collection(self) -> None:
        collections = self.client.get_collections()

        existing_collections = {
            collection.name
            for collection in collections.collections
        }

        if self.collection_name not in existing_collections:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                ),
            )

            print(
                f"Created Qdrant collection: "
                f"{self.collection_name}"
            )

        else:
            print(
                f"Qdrant collection already exists: "
                f"{self.collection_name}"
            )

    # =========================================================
    # Embeddings
    # =========================================================

    def embed_text(self, text: str) -> list[float]:
        """
        Generate an embedding for a single text.
        """

        embedding = self.embedding_model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple documents.
        """

        embeddings = self.embedding_model.encode(
            texts,
            normalize_embeddings=True,
        )

        return embeddings.tolist()

    # =========================================================
    # Add documents
    # =========================================================

    def add_documents(
        self,
        documents: list[dict[str, Any]],
    ) -> None:
        """
        Add document chunks to Qdrant.

        Expected format:

        {
            "id": "document:p1:c0",
            "text": "...",
            "metadata": {
                "document_name": "...",
                "page_number": 1,
                ...
            }
        }
        """

        if not documents:
            return

        texts = [
            document["text"]
            for document in documents
        ]

        embeddings = self.embed_documents(texts)

        points: list[PointStruct] = []

        for document, embedding in zip(
            documents,
            embeddings,
        ):
            point_id = document["id"]

            # Qdrant point IDs should preferably be UUIDs
            # or unsigned integers. We convert the original
            # document ID into a deterministic UUID.
            import uuid

            qdrant_id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    point_id,
                )
            )

            payload = {
                "text": document["text"],
                **document.get("metadata", {}),
                "source_id": point_id,
            }

            points.append(
                PointStruct(
                    id=qdrant_id,
                    vector=embedding,
                    payload=payload,
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

        print(
            f"Added {len(points)} documents to "
            f"Qdrant collection '{self.collection_name}'"
        )

    # =========================================================
    # Search
    # =========================================================

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Perform semantic similarity search.
        """

        query_embedding = self.embed_text(query)

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=top_k,
            with_payload=True,
        )

        documents: list[dict[str, Any]] = []

        for result in results.points:
            payload = result.payload or {}

            documents.append(
                {
                    "id": payload.get("source_id"),
                    "text": payload.get("text", ""),
                    "score": result.score,
                    "metadata": {
                        key: value
                        for key, value in payload.items()
                        if key not in {
                            "text",
                            "source_id",
                        }
                    },
                }
            )

        return documents

    # =========================================================
    # Collection information
    # =========================================================

    def count(self) -> int:
        """
        Return number of vectors stored in the collection.
        """

        result = self.client.count(
            collection_name=self.collection_name,
            exact=True,
        )

        return result.count

    def health_check(self) -> bool:
        """
        Check whether Qdrant is reachable.
        """

        try:
            self.client.get_collections()
            return True

        except Exception as exc:
            print(
                f"Qdrant health check failed: {exc}"
            )
            return False
