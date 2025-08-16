import pytest
from routers.todos import get_db, get_current_user
from fastapi import status
from models import Todos
from test.utils import *


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

    
def test_read_all_authenticated(test_todo):
    response = client.get("/todos")
    assert response.status_code == status.HTTP_200_OK
    print("Printing response", response.json())
    assert response.json() == [{"complete": False, "description": "This is a test todo", "owner_id": 1, "priority": 1, "title": "Test Todo", "id": 1}]

def test_read_one_authenticated(test_todo):
    response = client.get("/todos/todo/1")
    assert response.status_code == status.HTTP_200_OK
    print("Printing response", response.json())
    assert response.json() == {"complete": False, "description": "This is a test todo", "owner_id": 1, "priority": 1, "title": "Test Todo", "id": 1}


def test_read_one_authenticated_not_found():
    response = client.get("/todos/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}

def test_create_todo(test_todo):
    todo_data = {
        "title": "New Todo",
        "description": "This is a new todo",
        "priority": 2,
        "complete": False
    }
    response = client.post("/todos/todo", json=todo_data)
    assert response.status_code == status.HTTP_201_CREATED
    db = TestingSessionLocal()
    new_todo = db.query(Todos).filter(Todos.id == 2).first()
    # assert new_todo is not None
    assert new_todo.title == todo_data.get("title") # type: ignore
    assert new_todo.description == todo_data.get("description") # type: ignore
    assert new_todo.priority == todo_data.get("priority") # type: ignore
    assert new_todo.complete == todo_data.get("complete") # type: ignore

def test_update_todo(test_todo):
    update_data = {
        "title": "Updated Todo",
        "description": "This is a test todo",
        "priority": 1,
        "complete": False
    }
    response = client.put("/todos/todo/1", json=update_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    updated_todo = db.query(Todos).filter(Todos.id == 1).first()
    assert updated_todo.title == "Updated Todo" # type: ignore

def test_delete_todo(test_todo):
    response = client.delete("/todos/todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    deleted_todo = db.query(Todos).filter(Todos.id == 1).first()
    assert deleted_todo is None # type: ignore

def test_delete_todo_not_found():
    response = client.delete("/todos/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}
    