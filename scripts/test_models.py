# from sqlalchemy import inspect, text

# from app.data.database import Base, engine
# from app.data.models import Account, Order, Ticket, Action, AuditLog


# def main():
#     print("=" * 60)
#     print("PARCELPILOT SQLALCHEMY MODEL TEST")
#     print("=" * 60)

#     # --------------------------------------------------
#     # 1. Check database connection
#     # --------------------------------------------------
#     print("\n[1] Testing PostgreSQL connection...")

#     with engine.connect() as connection:
#         result = connection.execute(text("SELECT 1"))
#         print(f"Database connection: {result.scalar()}")

#     # --------------------------------------------------
#     # 2. Check registered models
#     # --------------------------------------------------
#     print("\n[2] Checking SQLAlchemy models...")

#     expected_tables = {
#         "accounts",
#         "orders",
#         "tickets",
#         "actions",
#         "audit_log",
#     }

#     actual_tables = set(Base.metadata.tables.keys())

#     print("Registered tables:")
#     for table in actual_tables:
#         print(f"  ✓ {table}")

#     missing = expected_tables - actual_tables

#     if missing:
#         print(f"\n❌ Missing tables in metadata: {missing}")
#         return

#     print("✓ All models registered correctly")

#     # --------------------------------------------------
#     # 3. Check table definitions
#     # --------------------------------------------------
#     print("\n[3] Checking model columns...")

#     for table_name in expected_tables:
#         table = Base.metadata.tables[table_name]

#         print(f"\n{table_name}:")

#         for column in table.columns:
#             print(
#                 f"  - {column.name}: "
#                 f"{column.type} "
#                 f"{'PK' if column.primary_key else ''}"
#             )

#     # --------------------------------------------------
#     # 4. Check database tables
#     # --------------------------------------------------
#     print("\n[4] Checking PostgreSQL tables...")

#     inspector = inspect(engine)

#     existing_tables = set(inspector.get_table_names())

#     for table in expected_tables:
#         if table in existing_tables:
#             print(f"  ✓ {table}")
#         else:
#             print(f"  ❌ {table} does not exist yet")

#     # --------------------------------------------------
#     # 5. Summary
#     # --------------------------------------------------
#     print("\n" + "=" * 60)
#     print("MODEL TEST COMPLETE")
#     print("=" * 60)


# if __name__ == "__main__":
#     main()



from sqlalchemy import text, inspect

from app.data.database import Base, engine
from app.data.models import Account, Order, Ticket, Action, AuditLog


def main():
    print("=" * 60)
    print("PARCELPILOT SQLALCHEMY MODEL TEST")
    print("=" * 60)

    # --------------------------------------------------
    # 1. Check database connection
    # --------------------------------------------------
    print("\n[1] Testing PostgreSQL connection...")

    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print(f"Database connection: {result.scalar()}")
    except Exception as exc:
        print(f"❌ Database connection failed: {exc}")
        return

    # --------------------------------------------------
    # 2. Check registered models
    # --------------------------------------------------
    print("\n[2] Checking SQLAlchemy models...")

    expected_tables = {
        "accounts",
        "orders",
        "tickets",
        "actions",
        "audit_log",
    }

    actual_tables = set(Base.metadata.tables.keys())

    print("Registered tables:")
    for table in sorted(actual_tables):
        print(f"  ✓ {table}")

    missing = expected_tables - actual_tables

    if missing:
        print(f"\n❌ Missing tables in metadata: {missing}")
        return

    print("✓ All models registered correctly")

    # --------------------------------------------------
    # 3. Check model columns
    # --------------------------------------------------
    print("\n[3] Checking model columns...")

    for table_name in sorted(expected_tables):
        table = Base.metadata.tables[table_name]

        print(f"\n{table_name}:")

        for column in table.columns:
            pk = "PK" if column.primary_key else ""

            print(
                f"  - {column.name}: "
                f"{column.type} "
                f"{pk}"
            )

    # --------------------------------------------------
    # 4. Create PostgreSQL tables
    # --------------------------------------------------
    print("\n[4] Creating PostgreSQL tables...")

    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Tables created/verified")
    except Exception as exc:
        print(f"❌ Table creation failed: {exc}")
        return

    # --------------------------------------------------
    # 5. Check PostgreSQL tables
    # --------------------------------------------------
    print("\n[5] Checking PostgreSQL tables...")

    try:
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names(schema="public"))
    except Exception as exc:
        print(f"❌ Could not inspect PostgreSQL tables: {exc}")
        return

    all_tables_exist = True

    for table_name in sorted(expected_tables):
        if table_name in existing_tables:
            print(f"  ✓ {table_name}")
        else:
            print(f"  ❌ {table_name} does not exist")
            all_tables_exist = False

    # --------------------------------------------------
    # 6. Summary
    # --------------------------------------------------
    print("\n" + "=" * 60)

    if all_tables_exist:
        print("MODEL TEST PASSED")
        print("=" * 60)
        print("✓ PostgreSQL connection working")
        print("✓ All SQLAlchemy models registered")
        print("✓ All PostgreSQL tables exist")
    else:
        print("MODEL TEST FAILED")
        print("=" * 60)
        print("Some PostgreSQL tables are missing")


if __name__ == "__main__":
    main()