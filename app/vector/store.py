
# from __future__ import annotations

# from typing import Any

# from qdrant_client import QdrantClient
# from qdrant_client.models import (
#     Distance,
#     PointStruct,
#     VectorParams,
# )

# from sentence_transformers import SentenceTransformer

# from app.config import settings


# class VectorStore:
#     """
#     Qdrant Cloud vector store for ParcelPilot.

#     Responsibilities:
#     - Connect to Qdrant Cloud
#     - Create the document collection if required
#     - Generate embeddings
#     - Store document chunks
#     - Perform semantic search
#     """

#     def __init__(
#         self,
#         collection_name: str | None = None,
#     ):
#         self.collection_name = (
#             collection_name or settings.qdrant_collection
#         )

#         # -----------------------------------------------------
#         # Embedding model
#         # -----------------------------------------------------

#         self.embedding_model = SentenceTransformer(
#             settings.embedding_model
#         )

#         # -----------------------------------------------------
#         # Qdrant Cloud client
#         # -----------------------------------------------------

#         self.client = QdrantClient(
#             url=settings.qdrant_endpoint,
#             api_key=settings.qdrant_api,
#         )

#         # all-MiniLM-L6-v2 → 384 dimensions
#         self.vector_size = (self.embedding_model.get_embedding_dimension())

#         if self.vector_size is None:
#             raise RuntimeError(
#                 "Unable to determine embedding dimension."
#             )

#         # -----------------------------------------------------
#         # Ensure collection exists
#         # -----------------------------------------------------

#         self._ensure_collection()

#     # =========================================================
#     # Collection
#     # =========================================================

#     def _ensure_collection(self) -> None:
#         collections = self.client.get_collections()

#         existing_collections = {
#             collection.name
#             for collection in collections.collections
#         }

#         if self.collection_name not in existing_collections:
#             self.client.create_collection(
#                 collection_name=self.collection_name,
#                 vectors_config=VectorParams(
#                     size=self.vector_size,
#                     distance=Distance.COSINE,
#                 ),
#             )

#             print(
#                 f"Created Qdrant collection: "
#                 f"{self.collection_name}"
#             )

#         else:
#             print(
#                 f"Qdrant collection already exists: "
#                 f"{self.collection_name}"
#             )

#     # =========================================================
#     # Embeddings
#     # =========================================================

#     def embed_text(self, text: str) -> list[float]:
#         """
#         Generate an embedding for a single text.
#         """

#         embedding = self.embedding_model.encode(
#             text,
#             normalize_embeddings=True,
#         )

#         return embedding.tolist()

#     def embed_documents(
#         self,
#         texts: list[str],
#     ) -> list[list[float]]:
#         """
#         Generate embeddings for multiple documents.
#         """

#         embeddings = self.embedding_model.encode(
#             texts,
#             normalize_embeddings=True,
#         )

#         return embeddings.tolist()

#     # =========================================================
#     # Add documents
#     # =========================================================

#     def add_documents(
#         self,
#         documents: list[dict[str, Any]],
#     ) -> None:
#         """
#         Add document chunks to Qdrant.

#         Expected format:

#         {
#             "id": "document:p1:c0",
#             "text": "...",
#             "metadata": {
#                 "document_name": "...",
#                 "page_number": 1,
#                 ...
#             }
#         }
#         """

#         if not documents:
#             return

#         texts = [
#             document["text"]
#             for document in documents
#         ]

#         embeddings = self.embed_documents(texts)

#         points: list[PointStruct] = []

#         for document, embedding in zip(
#             documents,
#             embeddings,
#         ):
#             point_id = document["id"]

#             # Qdrant point IDs should preferably be UUIDs
#             # or unsigned integers. We convert the original
#             # document ID into a deterministic UUID.
#             import uuid

#             qdrant_id = str(
#                 uuid.uuid5(
#                     uuid.NAMESPACE_URL,
#                     point_id,
#                 )
#             )

#             payload = {
#                 "text": document["text"],
#                 **document.get("metadata", {}),
#                 "source_id": point_id,
#             }

#             points.append(
#                 PointStruct(
#                     id=qdrant_id,
#                     vector=embedding,
#                     payload=payload,
#                 )
#             )

#         self.client.upsert(
#             collection_name=self.collection_name,
#             points=points,
#         )

#         print(
#             f"Added {len(points)} documents to "
#             f"Qdrant collection '{self.collection_name}'"
#         )

#     # =========================================================
#     # Search
#     # =========================================================

#     def search(
#         self,
#         query: str,
#         top_k: int = 5,
#     ) -> list[dict[str, Any]]:
#         """
#         Perform semantic similarity search.
#         """

#         query_embedding = self.embed_text(query)

#         results = self.client.query_points(
#             collection_name=self.collection_name,
#             query=query_embedding,
#             limit=top_k,
#             with_payload=True,
#         )

#         documents: list[dict[str, Any]] = []

#         for result in results.points:
#             payload = result.payload or {}

#             documents.append(
#                 {
#                     "id": payload.get("source_id"),
#                     "text": payload.get("text", ""),
#                     "score": result.score,
#                     "metadata": {
#                         key: value
#                         for key, value in payload.items()
#                         if key not in {
#                             "text",
#                             "source_id",
#                         }
#                     },
#                 }
#             )

#         return documents

#     # =========================================================
#     # Collection information
#     # =========================================================

#     def count(self) -> int:
#         """
#         Return number of vectors stored in the collection.
#         """

#         result = self.client.count(
#             collection_name=self.collection_name,
#             exact=True,
#         )

#         return result.count

#     def health_check(self) -> bool:
#         """
#         Check whether Qdrant is reachable.
#         """

#         try:
#             self.client.get_collections()
#             return True

#         except Exception as exc:
#             print(
#                 f"Qdrant health check failed: {exc}"
#             )
#             return False




<<<<<<< ours






=======
>>>>>>> theirs
from __future__ import annotations

from typing import Any
import uuid
<<<<<<< ours
=======

import requests
>>>>>>> theirs

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
<<<<<<< ours
    Qdrant Cloud vector store for ParcelPilot.

    Responsibilities:
    - Connect to Qdrant Cloud
    - Create the document collection if required
    - Generate embeddings
    - Store document chunks
    - Perform semantic search

    The embedding model is loaded lazily so that FastAPI
    startup does not immediately consume large amounts
    of memory.
=======
    Qdrant Cloud vector store using Jina embeddings.
>>>>>>> theirs
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

<<<<<<< ours
        # IMPORTANT:
        # Do NOT load SentenceTransformer here.
        #
        # It will be loaded only when embedding is actually
        # required.
        self.embedding_model: SentenceTransformer | None = None

        # -----------------------------------------------------
        # Qdrant client
        # -----------------------------------------------------
=======
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
>>>>>>> theirs

        self.client = QdrantClient(
            url=settings.qdrant_endpoint,
            api_key=settings.qdrant_api,
        )

<<<<<<< ours
        # all-MiniLM-L6-v2 = 384 dimensions
        #
        # We know this from the configured default model.
        # If you change the embedding model, update this value.
        self.vector_size = 384

        # -----------------------------------------------------
        # Ensure collection
        # -----------------------------------------------------

        self._ensure_collection()

    # =========================================================
    # Embedding Model
    # =========================================================

    def _get_embedding_model(self) -> SentenceTransformer:
        """
        Lazily load the Sentence Transformer model.

        The model is loaded only when embedding is required.
        """

        if self.embedding_model is None:
            self.embedding_model = SentenceTransformer(
                settings.embedding_model
            )

        return self.embedding_model

    # =========================================================
=======
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
>>>>>>> theirs
    # Collection
    # ========================================================

    def _ensure_collection(self) -> None:
<<<<<<< ours
        """Create the Qdrant collection if it doesn't exist."""

        collections = self.client.get_collections()
=======

        try:

            collections = self.client.get_collections()

        except Exception as exc:

            raise RuntimeError(
                f"Unable to connect to Qdrant: {exc}"
            ) from exc
>>>>>>> theirs

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
<<<<<<< ours
        """
        Generate an embedding for a single text.
        """

        model = self._get_embedding_model()

        embedding = model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    # =========================================================

=======

        return self.embedding_model.embed_query(
            text
        )

>>>>>>> theirs
    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:

<<<<<<< ours
        if not texts:
            return []

        model = self._get_embedding_model()

        embeddings = model.encode(
            texts,
            normalize_embeddings=True,
        )

        return embeddings.tolist()

    # =========================================================
    # Add Documents
    # =========================================================
=======
        return self.embedding_model.embed_documents(
            texts
        )

    # ========================================================
    # Add documents
    # ========================================================
>>>>>>> theirs

    def add_documents(
        self,
        documents: list[dict[str, Any]],
    ) -> None:
<<<<<<< ours
        """
        Add document chunks to Qdrant.

        Expected format:

        {
            "id": "document:p1:c0",
            "text": "...",
            "metadata": {
                "document_name": "...",
                "page_number": 1
            }
        }
        """
=======
>>>>>>> theirs

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

<<<<<<< ours
            point_id = document["id"]
=======
            point_id = str(
                document["id"]
            )

            # ------------------------------------------------
            # Deterministic UUID
            # ------------------------------------------------
>>>>>>> theirs

            # Convert application ID into deterministic UUID
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

<<<<<<< ours
    # =========================================================
    # Collection Information
    # =========================================================

    def count(self) -> int:
        """Return the number of vectors in the collection."""
=======
    # ========================================================
    # Count
    # ========================================================

    def count(self) -> int:
>>>>>>> theirs

        result = self.client.count(
            collection_name=self.collection_name,
            exact=True,
        )

        return result.count

<<<<<<< ours
    # =========================================================
    # Health Check
    # =========================================================

    def health_check(self) -> bool:
        """Check whether Qdrant is reachable."""
=======
    # ========================================================
    # Health check
    # ========================================================

    def health_check(self) -> bool:
>>>>>>> theirs

        try:

            self.client.get_collections()

            return True

        except Exception as exc:

            print(
                f"Qdrant health check failed: "
                f"{exc}"
            )

<<<<<<< ours
            return False
=======
            return False
>>>>>>> theirs
