import hashlib

from fastapi import UploadFile, HTTPException, status

from src.core import settings
from src.adapters.aws_repository import AwsRepository
from src.ports.enums import SupportedFileTypes


async def validate_file(file: UploadFile) -> bool:
    contents = await file.read()
    size = len(contents)
    if not 0 < size < 1024 * 1024:
        await file.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supported file size is 0 - 1 MB.",
        )

    await file.seek(0)

    content_type = file.content_type
    if (
        content_type != SupportedFileTypes.PNG
        and content_type != SupportedFileTypes.JPEG
    ):
        await file.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supported file types are png and jpeg.",
        )

    return True


async def upload_image(image_file: UploadFile, key: str) -> str:
    await validate_file(image_file)

    contents = await image_file.read()

    image_hash = hashlib.md5()
    image_hash.update(contents)
    image_hash.update(key.encode())

    combined_hash = image_hash.hexdigest()

    filename = f"{combined_hash}.png"

    await AwsRepository().add_one(contents, filename)

    return f"{settings.localstack_endpoint_url}/{settings.s3_bucket_name}/{filename}"


async def delete_old_image(url: str):
    last_slash_index = url.rfind("/")

    filename = url[last_slash_index + 1 :]

    try:
        await AwsRepository().delete(filename)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error with retrieving from bucket.",
        )
