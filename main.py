from fastapi import FastAPI, Request, Depends
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel

# MYSQL Database setup
DATABASE_URL = "mysql+pymysql://root:lerd@127.0.0.1/fastapi_db"

engine = create_engine(DATABASE_URL, connect_args={"charset": "utf8mb4"})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Define a Todo model
class Todo(Base):
    __tablename__='todos'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True)
    completed = Column(Boolean, default=False)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Request to create a new todo item
class TodoCreateRequest(BaseModel):
    title: str
    completed: bool = False

# Response model for a todo item
class TodoResponse(BaseModel):
    id: int
    title: str
    completed: bool

@app.post("/todos/", response_model=TodoResponse)
async def create_todo(request: TodoCreateRequest, db: Session = Depends(get_db)):
    new_todo = Todo(**request.dict())
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

@app.get("/todos", response_model=list[TodoResponse])
async def get_todos(db: Session = Depends(get_db)):
    todos = db.query(Todo).all()
    return todos