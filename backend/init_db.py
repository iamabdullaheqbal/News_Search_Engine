import asyncio
import sys

from app.db.database import engine
from app.db.schema import ensure_schema


async def init_db():
    print("Connecting to the database...")
    try:
        async with engine.begin() as conn:
            await ensure_schema(conn)
        print("Database schema initialized successfully!")
    except Exception as e:
        print(f"\n[ERROR] Failed to initialize database: {e}", file=sys.stderr)
        print("\nPlease make sure that:", file=sys.stderr)
        print("1. PostgreSQL server is running.", file=sys.stderr)
        print("2. The database 'veritas' exists. (Run 'CREATE DATABASE veritas;' if needed)", file=sys.stderr)
        print("3. The 'pgvector' extension is installed on your PostgreSQL server.", file=sys.stderr)
        print("4. The DATABASE_URL in backend/.env has the correct username and password.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(init_db())
