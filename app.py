import uvicorn
from fastapi import FastAPI

from api.default.routes import default_router
from api.program.routes import program_router
from src.api.weaviate.routes import weaviate_router

app = FastAPI()

app.include_router(default_router)

app.include_router(weaviate_router)

app.include_router(program_router)

if __name__ == '__main__':
    uvicorn.run("app:app", port=8080)
