from unittest import mock
from unittest.mock import patch, AsyncMock

import pytest

from src.core.services.file_service import upload_image
from tests.unit.test_valid_file import valid_file


@pytest.fixture
def aws_repo_mock():
    with patch("src.core.services.file_service.AwsRepository") as mock_aws_repo:
        mock_aws_repo.return_value.add_one = AsyncMock()
        yield mock_aws_repo


@pytest.mark.asyncio
async def test_upload_image(valid_file, aws_repo_mock):
    with patch.object(valid_file, "read", AsyncMock(return_value=b"some_binary_data")):
        key = "test_key"
        result = await upload_image(valid_file, key)

        aws_repo_mock.return_value.add_one.assert_called_once_with(
            b"some_binary_data", mock.ANY
        )

        assert result.endswith(".png")
