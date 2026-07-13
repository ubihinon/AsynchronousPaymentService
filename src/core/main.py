import logging

from fastapi import FastAPI

from core.logger_setup import setup_logging

logger = logging.getLogger(__name__)


setup_logging()

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

# app.include_router(users_router)
