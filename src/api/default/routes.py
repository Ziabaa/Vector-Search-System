from fastapi import APIRouter

default_router = APIRouter(tags=["defaults"])


@default_router.get("/")
async def read_root():
    return {"message": "Hello World"}


@default_router.get("/echo")
async def read_root(message: str):
    return {"echo": message}
