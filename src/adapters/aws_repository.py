from src.ports.repositories.aws_repository import AwsAbstractRepository
from src.core.services.s3_service import aws_client
from src.core import settings


class AwsRepository(AwsAbstractRepository):
    async def add_one(self, body: bytes, key: str):
        async with aws_client("s3") as s3:
            await s3.put_object(Body=body, Bucket=settings.s3_bucket_name, Key=key)

    async def delete(self, key: str):
        async with aws_client("s3") as s3:
            await s3.delete_object(Bucket=settings.s3_bucket_name, Key=key)

    async def get(self, key: str):
        async with aws_client("s3") as s3:
            return await s3.get_object(Bucket=settings.s3_bucket_name, Key=key)
