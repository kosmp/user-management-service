from fastapi import APIRouter

router = APIRouter()


@router.get("/users")
async def get_users(
    page: int,
    limit: int = 30,
    filter_by_name: str = None,
    sort_by: str = None,
    order_by: str = "asc",
):
    pass


@router.get("/user/me")
async def get_me():
    pass


@router.patch("/user/me")
async def update_me():
    pass


@router.delete("/user/me")
async def delete_me():
    pass


@router.get("/user/{user_id}")
async def get_user(user_id: int):
    pass


@router.patch("/user/{user_id}")
async def update_user(user_id: int):
    pass
