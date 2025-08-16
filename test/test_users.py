from test.utils import *
from fastapi import status
from models import Todos    
from routers.users import get_db, get_current_user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_return_users(test_user):
    response = client.get("/users/user")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == "testuser"
    assert response.json()['email'] == "testuser@example.com"
    assert response.json()['first_name'] == "Test"
    assert response.json()['last_name'] == "User"
    assert response.json()['phone_number'] == "1234567890"

def test_change_password_success(test_user):
    new_password = "newpassword"
    response = client.put("/users/password", json={"password": "testpassword", "new_password": new_password})
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_change_password_failure(test_user):
    new_password = "newpassword"
    response = client.put("/users/password", json={"password": "wrongpassword", "new_password": new_password})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid password"}

def test_update_phone_number_success(test_user):
    new_phone_number = "0987654321"
    response = client.put(f"/users/phonenumber/{new_phone_number}")
    assert response.status_code == status.HTTP_204_NO_CONTENT