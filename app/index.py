from fastapi import FastAPI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}

@app.get("/user/{user_name}")
def read_user(user_name: str):
    return {"message": f"You got this {user_name}!!!"}

@app.get("/test_env")
def test_env():
    return {"message": os.getenv("TEST_VARIABLE")}