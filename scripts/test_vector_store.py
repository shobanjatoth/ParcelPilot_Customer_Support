from app.vector.store import VectorStore


def main():
    print("Initializing Qdrant VectorStore...")

    store = VectorStore()

    print("Qdrant health:", store.health_check())

    print(
        "Collection:",
        store.collection_name,
    )

    print(
        "Vector count:",
        store.count(),
    )

    print("VectorStore test successful!")


if __name__ == "__main__":
    main()