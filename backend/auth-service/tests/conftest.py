import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.config import Settings
from dotenv import load_dotenv

# Load test environment
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env.test'))

TEST_DATABASE_URL = os.getenv("DATABASE_URL")

# Create test engine and session
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Drop and recreate all tables for a clean state
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client(setup_database):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
