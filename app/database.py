import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

postgres_url = os.getenv(
    "POSTGRES_URL",
    "postgresql://postgres:2003@localhost:5432/docs_llm_db"
)

databaseEngine = create_engine(postgres_url, echo=False)
DatabaseSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=databaseEngine
)
DatabaseBase = declarative_base()

def initializeDatabase():
    DatabaseBase.metadata.create_all(bind=databaseEngine)