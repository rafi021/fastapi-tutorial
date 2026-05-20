from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    id: int
    name: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

users = []

@app.post("/users/", response_model=UserResponse)
def create_user(user: User):
    users.append(user)
    return UserResponse(id=user.id, name=user.name, email=user.email)

@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int):
    for user in users:
        if user.id == user_id:
            return UserResponse(id=user.id, name=user.name, email=user.email)
    return {"error": "User not found"}