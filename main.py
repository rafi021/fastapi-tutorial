from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Let's create a Todo CRUD API
todos = []

class Todo(BaseModel):
    id: int
    title: str
    completed: bool

@app.post("/todos")
def create_todo(todo: Todo):
    todos.append(todo)
    return {"message": "Todo created", "todo": todo}

@app.get("/todos")
def get_todos():
    return {"message": "Fetch All Todos", "todos": todos}

@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    todo = next((t for t in todos if t.id == todo_id), None)
    if todo:
        return {"message": "Fetch Todo", "todo": todo}
    return {"message": "Todo not found"}, 404

@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, updated_todo: Todo):
    # Find the index of the todo we want to update
    for index, todo in enumerate(todos):
        if todo.id == todo_id:
            todos[index] = updated_todo
            return {"message": "Todo updated", "todo": updated_todo}

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    for index, todo in enumerate(todos):
        if todo.id == todo_id:
            deleted_todo = todos.pop(index)
            return {"message": "Todo deleted", "todo": deleted_todo}