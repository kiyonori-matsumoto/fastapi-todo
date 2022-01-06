from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()


class Todo(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    created_at: datetime = Field(default_factory=datetime.now)
    finished_at: Optional[datetime]
    finished: bool = False

    def set_finished(self, finished: bool):
        if self.finished is finished:
            return

        self.finished = finished
        self.finished_at = None if not finished else datetime.now()


class CreateTodoParams(BaseModel):
    title: str
    finished: bool


class UpdateTodoParams(BaseModel):
    title: Optional[str] = None
    finished: Optional[bool] = None


todos: Dict[UUID, Todo] = {}


@app.post("/todos", response_model=Todo)
def create_todo(params: CreateTodoParams):
    todo = Todo(title=params.title, )
    todo.set_finished(params.finished)
    todos[todo.id] = todo
    return todo


@app.get("/todos", response_model=List[Todo])
def get_todos(finished: Optional[bool] = None):
    values = todos.values()
    if finished:
        values = filter(lambda x: x.finished == finished, values)

    return list(values)


@app.patch("/todos/{id}", response_model=Todo)
def update_todo(id: UUID, params: UpdateTodoParams):
    todo = todos.get(id)

    if todo is None:
        # 404
        raise HTTPException(status_code=404)

    if params.title:
        todo.title = params.title

    if params.finished is not None:
        todo.set_finished(params.finisehd)

    return todo


@app.delete("/todos/{id}")
def delete_todo(id: UUID):
    try:
        del todos[id]
    except KeyError:
        pass
