from test.utils import *
from fastapi import status
from models import Todos
from routers.auth import get_db, authenticate_user, SECRET_KEY, ALGORITHM, create_access_token, get_current_user
from jose import jwt
from datetime import datetime, timedelta
import pytest
from fastapi import HTTPException

app.dependency_overrides[get_db] = override_get_db


def test_authenticate_user_success(test_user):
    db = TestingSessionLocal()

    authenticated_user = authenticate_user(test_user.username, "testpassword", db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username # type: ignore
    assert authenticated_user.email == test_user.email# type: ignore
    assert authenticated_user.first_name == test_user.first_name# type: ignore
    assert authenticated_user.last_name == test_user.last_name# type: ignore
    assert authenticated_user.phone_number == test_user.phone_number# type: ignore

    non_existent_user = authenticate_user("nonexistent", "wrongpassword", db)
    assert non_existent_user is False

    wrong_password_user = authenticate_user(test_user.username, "wrongpassword", db)
    assert wrong_password_user is False

def test_create_access_token(test_user):
    username = 'testuser'
    user_id = 1
    role = 'user'
    expires_delta = timedelta(minutes=30)

    token = create_access_token(username, user_id, role, expires_delta)

    decode_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})

    assert decode_token['sub'] == username
    assert decode_token['id'] == user_id
    assert decode_token['role'] == role

@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode = {'sub': 'testuser', 'id': 1, 'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token)
    assert user == {"id": 1, "username": "testuser", "user_role": "admin"}

@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {'sub': 'testuser'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid authentication credentials"
