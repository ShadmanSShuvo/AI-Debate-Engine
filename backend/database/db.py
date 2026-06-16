import os
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import event
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

# Load env files
load_dotenv()

# Default to local SQLite database in the backend directory
DEFAULT_DB_URL = "sqlite:///debate.db"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

# SQLite-specific arguments: disable thread checking since FastAPI is multi-threaded
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Create engine
engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)

# Enable foreign keys for SQLite (essential for ON DELETE CASCADE)
if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

def init_db():
    # Import models to register them with SQLModel metadata
    from .models import Debate, Argument, Fallacy, Evidence, Rebuttal, Verification
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
