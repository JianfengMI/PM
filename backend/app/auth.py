import hmac
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from backend.app.datastore import JsonDataStore, UserRecord


security = HTTPBasic()


def get_current_user(
    credentials: HTTPBasicCredentials = Depends(security),
    datastore: JsonDataStore = Depends(JsonDataStore),
) -> UserRecord:
    expected_username = os.environ.get("KANBAN_USERNAME", "user")
    expected_password = os.environ.get("KANBAN_PASSWORD", "password")
    username_matches = hmac.compare_digest(credentials.username, expected_username)
    password_matches = hmac.compare_digest(credentials.password, expected_password)

    if not username_matches or not password_matches:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    try:
        return datastore.get_user_by_username(credentials.username)
    except KeyError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not registered",
            headers={"WWW-Authenticate": "Basic"},
        ) from error