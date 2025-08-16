from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from database import Base
from main import app
from fastapi.testclient import TestClient
import pytest
from models import Todos, Users
from routers.auth import bcrypt_context

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {"id": 1, "username": "testuser", "user_role": "admin"}

client = TestClient(app)

@pytest.fixture(scope="session")  # Runs once after all tests
def cleanup_todos():
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()

@pytest.fixture
def test_todo():
    todo = Todos(title="Test Todo", description="This is a test todo", priority=1, complete=False, owner_id=1, id=1)
    
    db = TestingSessionLocal()
    # Clear the table before each test
    db.query(Todos).delete()
    db.commit()
    db.add(todo)
    db.commit()
    db.refresh(todo)
    yield todo
    # No cleanup here!  cleanup_todos will handle it.
    # Clean up after each test (optional, but good practice)
    db.delete(todo)
    db.commit()


@pytest.fixture
def test_user():
    user = Users(
        username="testuser", 
        email="testuser@example.com", 
        first_name ="Test",
        last_name="User",
        hashed_password=bcrypt_context.hash("testpassword"),
        role="admin",
        phone_number="1234567890"
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.delete(user)
    db.commit()