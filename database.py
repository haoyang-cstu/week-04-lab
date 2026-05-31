import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load variables from the .env file into the environment so that
# os.getenv() below can read DATABASE_URL.
load_dotenv()

# The connection string, e.g. postgresql://postgres:password@localhost:5432/booktracker
DATABASE_URL = os.getenv("DATABASE_URL")

# The engine is the core interface to the database. It manages a pool of
# connections and knows how to talk to PostgreSQL via the psycopg2 driver.
engine = create_engine(DATABASE_URL)

# SessionLocal is a factory: calling SessionLocal() gives you a new database
# session (a "conversation" with the DB) that you use to run queries.
# autocommit/autoflush are off so we control when changes are written.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class that all ORM models (tables) inherit from.
# SQLAlchemy uses it to keep track of every model so it can create tables.
Base = declarative_base()


def get_db():
    """FastAPI dependency that provides a database session per request.

    It yields a session for the route to use, then guarantees the session
    is closed afterwards (even if the route raises an error).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
