import asyncio
import sys
from sqlalchemy import text
from app.db.database import engine, Base
# Import models so they are registered in the Base.metadata
from app.db.models import User, UserInterest, ReadHistory, Article

async def init_db():
    print("Connecting to the database...")
    try:
        # 1. Create pgvector extension
        async with engine.begin() as conn:
            print("Enabling pgvector extension (CREATE EXTENSION IF NOT EXISTS vector)...")
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            
            # 2. Create tables
            print("Creating tables based on models (Base.metadata.create_all)...")
            await conn.run_sync(Base.metadata.create_all)
            
        print("Database tables created and initialized successfully!")
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
