import pytest
from fastapi import UploadFile, HTTPException, status
from starlette.datastructures import Headers

from src.ports.enums import SupportedFileTypes
from src.core.services.file_service import validate_file


@pytest.fixture
def upload_valid_file(tmp_path):
    file_path = tmp_path / "test.png"
    file_path.write_bytes(b"some_binary_data")

    return UploadFile(
        filename="test.png",
        file=file_path.open("rb"),
        headers=Headers({"content-type": SupportedFileTypes.PNG}),
    )


@pytest.fixture
def upload_invalid_size_file(tmp_path):
    file_path = tmp_path / "test.png"
    file_path.write_bytes(b"x" * (1024 * 1024 + 1))

    return UploadFile(
        filename="test.png",
        file=file_path.open("rb"),
        headers=Headers({"content-type": SupportedFileTypes.PNG}),
    )


@pytest.fixture
def upload_invalid_type_file(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_bytes(b"some_binary_data")

    return UploadFile(
        filename="test.txt",
        file=file_path.open("rb"),
        headers=Headers({"content-type": "text/plain"}),
    )


@pytest.mark.asyncio
async def test_validate_file_success(upload_valid_file):
    result = await validate_file(upload_valid_file)

    assert result is True


@pytest.mark.asyncio
async def test_validate_file_invalid_size(upload_invalid_size_file):
    with pytest.raises(HTTPException) as exc_info:
        await validate_file(upload_invalid_size_file)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_validate_file_invalid_type(upload_invalid_type_file):
    with pytest.raises(HTTPException) as exc_info:
        await validate_file(upload_invalid_type_file)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
