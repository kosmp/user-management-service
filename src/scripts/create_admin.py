import asyncio

from sqlalchemy import select

from src.adapters.database.database_settings import async_session
from src.adapters.database.models.groups import Group
from src.adapters.database.models.users import User
from src.core import settings
from src.core.services.hasher import PasswordHasher


async def create_admin_user():
    async with async_session() as session:
        if await session.scalar(select(Group).where(Group.name == "base")) is not None:
            return

        new_group = Group(name="base")
        session.add(new_group)
        await session.flush()

        new_user = User(
            role="admin",
            name="Admin",
            surname="Admin",
            username=settings.admin_username,
            phone_number=settings.admin_phone_number,
            email=settings.admin_email,
            password=PasswordHasher.get_password_hash(settings.admin_password),
            group_id=new_group.id,
        )

        session.add(new_user)

        await session.commit()


asyncio.run(create_admin_user())
