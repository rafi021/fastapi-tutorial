from fastapi import FastAPI, status
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

class ResponseModel(BaseModel):
    status: str
    message: str
    data: UserResponse

users = []

@app.post("/users/", response_model=ResponseModel, status_code=status.HTTP_201_CREATED)
def create_user(user: User):
    users.append(user)
    return ResponseModel(
        status="success",
        message=f"User {user.name} created successfully",
        data=UserResponse(id=user.id, name=user.name, email=user.email)
    )
    # return UserResponse(id=user.id, name=user.name, email=user.email)

@app.get("/users/{user_id}", response_model=ResponseModel)
def read_user(user_id: int):
    for user in users:
        if user.id == user_id:
            return ResponseModel(
                status="success",
                message="User retrieved successfully",
                data=UserResponse(id=user.id, name=user.name, email=user.email)
            )
    return ResponseModel(
        status="error",
        message="User not found",
        data=None
    )