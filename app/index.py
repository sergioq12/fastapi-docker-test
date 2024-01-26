from fastapi import FastAPI

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
