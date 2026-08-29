# from qdrant_client import QdrantClient

# from app.config import settings


# def main():
#     print("Connecting to Qdrant Cloud...")

#     client = QdrantClient(
#         url=settings.qdrant_url,
#         api_key=settings.qdrant_api_key,
#     )

#     collections = client.get_collections()

#     print("Qdrant connection successful!")
#     print("Collections:")

#     for collection in collections.collections:
#         print(f" - {collection.name}")


# if __name__ == "__main__":
#     main()


from qdrant_client import QdrantClient

from app.config import settings


def main():
    print("Connecting to Qdrant Cloud...")

    client = QdrantClient(
        url=settings.qdrant_endpoint,
        api_key=settings.qdrant_api,
    )

    collections = client.get_collections()

    print("Qdrant connection successful!")
    print("Collections:")

    for collection in collections.collections:
        print(f" - {collection.name}")


if __name__ == "__main__":
    main()