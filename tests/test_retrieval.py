from app.vector.store import VectorStore
from app.services.retrieval import RetrievalService


def main():
    print("=" * 60)
    print("PARCELPILOT RETRIEVAL TEST")
    print("=" * 60)

    vector_store = VectorStore()

    print(f"\nCollection: {vector_store.collection_name}")
    print(f"Vector count: {vector_store.count()}")

    retrieval = RetrievalService(vector_store)

    query = "What is the cancellation policy?"

    print(f"\nQuery: {query}")
    print("-" * 60)

    result = retrieval.search_documents(
        query=query,
        n_results=5,
    )

    print(f"Results: {len(result['results'])}")
    print(f"Citations: {len(result['citations'])}")
    print(f"Conflicts: {len(result['conflicts'])}")

    for i, item in enumerate(result["results"], start=1):
        print(f"\n[{i}]")
        print("ID:", item.get("id"))
        print("Score:", item.get("score"))
        print("Document:", item.get("metadata", {}).get("document_name"))
        print("Page:", item.get("metadata", {}).get("page_number"))
        print("Status:", item.get("metadata", {}).get("status"))
        print("Text:", item.get("text", "")[:250])

    print("\n" + "=" * 60)
    print("CITATIONS")
    print("=" * 60)

    for citation in result["citations"]:
        print(citation)

    print("\n" + "=" * 60)
    print("CONFLICTS")
    print("=" * 60)

    for conflict in result["conflicts"]:
        print(conflict)

    print("\n" + "=" * 60)
    print("RETRIEVAL TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
