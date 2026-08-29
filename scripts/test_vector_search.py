from app.vector.store import VectorStore


def main():
    store = VectorStore()

    documents = [
        {
            "id": "test:1",
            "text": (
                "Customers can request shipment cancellation "
                "before pickup according to the cancellation policy."
            ),
            "metadata": {
                "document_name": "Test Policy",
                "document_type": "policy",
                "source_priority": 100,
            },
        },
        {
            "id": "test:2",
            "text": (
                "Premium customers receive priority support "
                "for operational shipment issues."
            ),
            "metadata": {
                "document_name": "Test Support Policy",
                "document_type": "policy",
                "source_priority": 90,
            },
        },
    ]

    store.add_documents(documents)

    results = store.search(
        "Can I cancel my shipment before pickup?",
        top_k=2,
    )

    print("\nSearch results:\n")

    for result in results:
        print(
            f"Score: {result['score']:.4f}"
        )
        print(
            f"Text: {result['text']}"
        )
        print(
            f"Metadata: {result['metadata']}"
        )
        print("-" * 60)


if __name__ == "__main__":
    main()