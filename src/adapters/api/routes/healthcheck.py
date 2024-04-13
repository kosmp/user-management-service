from fastapi import APIRouter

router = APIRouter()


@router.get("/healthcheck")
async def get_health_status():
    return {"status": "OK"}
