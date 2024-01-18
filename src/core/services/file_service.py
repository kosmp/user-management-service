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


async def upload_image(image_file: UploadFile) -> str:
    await validate_file(image_file)

    contents = await image_file.read()

    image_hash = hashlib.md5(contents).hexdigest()

    filename = f"{image_hash}.png"

    await AwsRepository().add_one(contents, filename)

    return f"{settings.localstack_endpoint_url}/{settings.s3_bucket_name}/{filename}"
