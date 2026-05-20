from fastapi import FastAPI, status, HTTPException, Request
from fastapi.responses import JSONResponse
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

# Custom exception for user not found
class UserNotFoundException(Exception):
    def __init__(self, user_id: int):
        self.user_id = user_id

# Global exception handler for UserNotFoundException
@app.exception_handler(UserNotFoundException)
def user_not_found_exception_handler(request: Request, exc: UserNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"status": "error", "message": f"User with ID {exc.user_id} not found", "data": None}
    )

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
    raise UserNotFoundException(user_id)