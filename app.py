import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/echo")
def read_root(message: str):
    return {"echo": message}


if __name__ == '__main__':
    uvicorn.run("app:app", port=8080)
