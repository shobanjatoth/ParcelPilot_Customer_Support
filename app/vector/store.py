from __future__ import annotations

from typing import Any
import uuid

import requests

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)

from app.config import settings


# ============================================================
# JINA EMBEDDINGS
# ============================================================

class JinaEmbeddings:
    """
    Jina AI embeddings client.

    Uses Jina's hosted embedding API instead of loading
    SentenceTransformer / PyTorch locally.

    This significantly reduces Render memory usage.
    """

    def __init__(self) -> None:

        if not settings.jina_api_key:
            raise RuntimeError(
                "JINA_API_KEY is not configured."
            )

        self.api_key = settings.jina_api_key

        self.base_url = (
            settings.jina_base_url
            or "https://api.jina.ai/v1/embeddings"
        )

        self.model = (
            settings.embedding_model
            or "jina-embeddings-v3"
        )

    # --------------------------------------------------------
    # Jina API request
    # --------------------------------------------------------

    def _request(
        self,
        texts: list[str],
        task: str,
    ) -> list[list[float]]:

        if not texts:
            return []

        payload = {
            "model": self.model,
            "input": texts,
            "task": task,
        }

        try:

            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": (
                        f"Bearer {self.api_key}"
                    ),
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=120,
            )

        except requests.RequestException as exc:

            raise RuntimeError(
                f"Unable to connect to Jina API: {exc}"
            ) from exc

        # ----------------------------------------------------
        # IMPORTANT:
        # Do not use response.raise_for_status()
        # because we want Jina's actual error message.
        # ----------------------------------------------------

        if not response.ok:

            try:
                error_body = response.json()
            except Exception:
                error_body = response.text

            raise RuntimeError(
                f"Jina API error "
                f"(HTTP {response.status_code}): "
                f"{error_body}"
            )

        try:

            data = response.json()

        except ValueError as exc:

            raise RuntimeError(
                "Jina API returned invalid JSON."
            ) from exc

        if "data" not in data:

            raise RuntimeError(
                f"Unexpected Jina API response: {data}"
            )

        embeddings: list[list[float]] = []

        for item in data["data"]:

            embedding = item.get("embedding")

            if embedding is None:

                raise RuntimeError(
                    f"Jina response contains no embedding: "
                    f"{item}"
                )

            embeddings.append(embedding)

        return embeddings

    # ========================================================
    # Document embeddings
    # ========================================================

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        return self._request(
            texts,
            task="retrieval.passage",
        )

    # ========================================================
    # Query embedding
    # ========================================================

    def embed_query(
        self,
        text: str,
    ) -> list[float]:

        embeddings = self._request(
            [text],
            task="retrieval.query",
        )

        if not embeddings:

            raise RuntimeError(
                "Jina returned no embedding for query."
            )

        return embeddings[0]


# ============================================================
# VECTOR STORE
# ============================================================

class VectorStore:
    """
    Qdrant Cloud vector store using Jina embeddings.
    """

    def __init__(
        self,
        collection_name: str | None = None,
    ) -> None:

        self.collection_name = (
            collection_name
            or settings.qdrant_collection
        )

        # ----------------------------------------------------
        # Jina embeddings
        # ----------------------------------------------------

        self.embedding_model = JinaEmbeddings()

        # ----------------------------------------------------
        # Validate Qdrant configuration
        # ----------------------------------------------------

        if not settings.qdrant_endpoint:

            raise RuntimeError(
                "QDRANT_ENDPOINT is not configured."
            )

        if not settings.qdrant_api:

            raise RuntimeError(
                "QDRANT_API is not configured."
            )

        # ----------------------------------------------------
        # Qdrant Cloud client
        # ----------------------------------------------------

        self.client = QdrantClient(
            url=settings.qdrant_endpoint,
            api_key=settings.qdrant_api,
        )

        # Jina embeddings dimension
        #
        # Must match the Qdrant collection.
        # jina-embeddings-v3 commonly uses 1024 dimensions
        # when no dimension reduction is requested.
        # ----------------------------------------------------

        self.vector_size = settings.embedding_dimension

        if not self.vector_size:

            raise RuntimeError(
                "EMBEDDING_DIMENSION is not configured."
            )

        # ----------------------------------------------------
        # Ensure collection
        # ----------------------------------------------------

        self._ensure_collection()

    # ========================================================
    # Collection
    # ========================================================

    def _ensure_collection(self) -> None:

        try:

            collections = self.client.get_collections()

        except Exception as exc:

            raise RuntimeError(
                f"Unable to connect to Qdrant: {exc}"
            ) from exc

        existing_collections = {
            collection.name
            for collection in collections.collections
        }

        # ----------------------------------------------------
        # Create collection if it doesn't exist
        # ----------------------------------------------------

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

    # ========================================================
    # Embeddings
    # ========================================================

    def embed_text(
        self,
        text: str,
    ) -> list[float]:

        return self.embedding_model.embed_query(
            text
        )

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        return self.embedding_model.embed_documents(
            texts
        )

    # ========================================================
    # Add documents
    # ========================================================

    def add_documents(
        self,
        documents: list[dict[str, Any]],
    ) -> None:

        if not documents:
            return

        # ----------------------------------------------------
        # Extract text
        # ----------------------------------------------------

        texts = [
            document["text"]
            for document in documents
        ]

        # ----------------------------------------------------
        # Generate Jina embeddings
        # ----------------------------------------------------

        embeddings = self.embed_documents(
            texts
        )

        if len(embeddings) != len(documents):

            raise RuntimeError(
                "Number of embeddings returned by Jina "
                "does not match number of documents."
            )

        # ----------------------------------------------------
        # Create Qdrant points
        # ----------------------------------------------------

        points: list[PointStruct] = []

        for document, embedding in zip(
            documents,
            embeddings,
        ):

            point_id = str(
                document["id"]
            )

            # ------------------------------------------------
            # Deterministic UUID
            # ------------------------------------------------

            qdrant_id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    point_id,
                )
            )

            # ------------------------------------------------
            # Payload
            # ------------------------------------------------

            payload = {
                "text": document["text"],
                **document.get(
                    "metadata",
                    {},
                ),
                "source_id": point_id,
            }

            points.append(
                PointStruct(
                    id=qdrant_id,
                    vector=embedding,
                    payload=payload,
                )
            )

        # ----------------------------------------------------
        # Upload to Qdrant
        # ----------------------------------------------------

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

        print(
            f"Added {len(points)} documents to "
            f"Qdrant collection "
            f"'{self.collection_name}'"
        )

    # ========================================================
    # Search
    # ========================================================

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:

        # ----------------------------------------------------
        # Create query embedding using Jina
        # ----------------------------------------------------

        query_embedding = self.embed_text(
            query
        )

        # ----------------------------------------------------
        # Search Qdrant
        # ----------------------------------------------------

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
                    "id": payload.get(
                        "source_id"
                    ),

                    "text": payload.get(
                        "text",
                        "",
                    ),

                    "score": result.score,

                    "metadata": {
                        key: value
                        for key, value
                        in payload.items()
                        if key not in {
                            "text",
                            "source_id",
                        }
                    },
                }
            )

        return documents

    # ========================================================
    # Count
    # ========================================================

    def count(self) -> int:

        result = self.client.count(
            collection_name=self.collection_name,
            exact=True,
        )

        return result.count

    # ========================================================
    # Health check
    # ========================================================

    def health_check(self) -> bool:

        try:

            self.client.get_collections()

            return True

        except Exception as exc:

            print(
                f"Qdrant health check failed: "
                f"{exc}"
            )

            return False