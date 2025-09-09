from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use SQLite for testing, PostgreSQL for production
if os.getenv("TESTING") in ["true", "1"]:
    SQLALCHEMY_DATABASE_URL = 'sqlite:///./test_database.db'
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
    if not SQLALCHEMY_DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required")
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()