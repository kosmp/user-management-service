import uuid
from fastapi import status
import pytest
from datetime import timedelta, datetime
from jose import jwt
from src.core.exceptions import CredentialsException
from src.ports.enums import TokenType
from src.ports.schemas.user import TokenDataWithTokenType
from src.core import settings
from src.core.services.token import get_token_payload, generate_token


@pytest.fixture
def mock_settings(mocker):
    return mocker.patch(
        "src.core.settings", secret_key="test_secret", algorithm="test_algorithm"
    )


def test_get_token_payload_valid_token(mock_settings):
    payload_data = {
        "user_id": "test_user_id",
        "role": "test_role",
        "group_id": "test_group_id",
        "is_blocked": False,
        "token_type": TokenType.ACCESS,
    }
    valid_token = jwt.encode(
        payload_data, settings.secret_key, algorithm=settings.algorithm
    )

    result = get_token_payload(valid_token)

    assert result == TokenDataWithTokenType(**payload_data)


def test_get_token_payload_invalid_token(mock_settings):
    invalid_token = "invalid_token"

    with pytest.raises(CredentialsException) as exc_info:
        get_token_payload(invalid_token)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_expired_token():
    expired_token = jwt.encode(
        {"exp": datetime.now() - timedelta(days=1)},
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    with pytest.raises(CredentialsException) as exc_info:
        get_token_payload(expired_token)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_generate_token(mock_settings):
    expires_delta = timedelta(minutes=1)
    test_user_uuid = str(uuid.uuid4())
    test_group_uuid = str(uuid.uuid4())
    payload_data = {
        "user_id": test_user_uuid,
        "role": "test_role",
        "group_id": test_group_uuid,
        "is_blocked": False,
        "token_type": TokenType.ACCESS,
    }
    payload = TokenDataWithTokenType(**payload_data)

    result = generate_token(payload, expires_delta)

    decoded_payload = jwt.decode(
        result, settings.secret_key, algorithms=[settings.algorithm]
    )
    assert decoded_payload["user_id"] == test_user_uuid
