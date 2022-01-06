from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timezone

app = FastAPI()


class Todo(BaseModel):
    title: str
    created_at: datetime
    finished_at: datetime
    finished: bool


@app.post("/test-todo")
def post_dummy_todo(todo: Todo):
    return Todo(
        title=todo.title,
        created_at=todo.created_at.astimezone(timezone.utc),
        finished_at=todo.finished_at.astimezone(timezone.utc),
        finished=todo.finished,
    )


@app.post("/test-todo-invalid", response_model=Todo)
def post_dummy_todo_invalid(todo: Todo):
    return {
        "title": todo.title,
        "created_at": todo.created_at.astimezone(timezone.utc),
        "finished_at": "invalid",
        "finished": todo.finished,
    }
