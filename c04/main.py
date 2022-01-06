from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, root_validator, constr

description = """
## APIの詳細
- TODOの作成及び削除ができます
"""

app = FastAPI(
    title="はじめてのTodo API",
    description=description,
    openapi_tags=[{
        "name": "Todo",
        "description": "Todoの管理ができます"
    }],
    version="1.0.0",
    contact={
        "name": "Todoサポート",
        "url": "https://github.com/issues"
    },
)

Title = constr(max_length=100)


class Todo(BaseModel):
    """Todoの状態を管理するモデル"""
    id: UUID = Field(default_factory=uuid4, description="ID")
    title: Title = Field(..., description="Todoの内容")
    created_at: datetime = Field(default_factory=datetime.now,
                                 description="作成時刻")
    finished_at: Optional[datetime] = Field(None, description="完了時刻")
    finished: bool = Field(False, description="完了したか否か")

    class Config():
        schema_extra = {
            "example": {
                "id": "01234567-89ab-cddf-0123-456789abcdef",
                "title": "はじめてのTodo",
                "created_at": "2022-01-01T00:00:00Z",
                "finished": False,
                "finished_at": None,
            }
        }

    @root_validator()
    def set_finished_at(cls, values):
        if values.get('finished') and values.get('finished_at') is None:
            values['finished_at'] = datetime.now()
        return values

    def set_finished(self, finished: bool):
        if self.finished is finished:
            return

        self.finished = finished
        self.finished_at = None if not finished else datetime.now()


class CreateTodoParams(BaseModel):
    title: Title
    finished: bool


class UpdateTodoParams(BaseModel):
    title: Optional[Title] = None
    finished: Optional[bool] = None


todos: Dict[UUID, Todo] = {}


@app.post("/todos", response_model=Todo)
def create_todo(params: CreateTodoParams):
    todo = Todo(
        title=params.title,
        finished=params.finished,
    )
    todos[todo.id] = todo
    return todo


query_finished_description = """
trueのときは完了したTodoのみ表示

falseのときは未完了のTodoのみ表示

未指定の場合はフィルタリングを行わない
"""


@app.get(
    "/todos",
    response_model=List[Todo],
    summary="Todoの一覧取得",
    tags=["Todo"],
    operation_id="get_todos",
)
def get_todos(finished: Optional[bool] = Query(
    None, description=query_finished_description)):
    """
    Todoの一覧を取得します。

    `finished` のクエリパラメータで、完了/未完了のもののみを表示できます

    \f

    \\fより下の記述はドキュメントには表示されません
    """
    values = todos.values()
    if finished:
        values = filter(lambda x: x.finished == finished, values)

    return list(values)


class ErrorMessage(BaseModel):
    """エラーメッセージ"""
    message: str


@app.patch("/todos/{id}",
           response_model=Todo,
           responses={404: {
               "model": ErrorMessage
           }})
def update_todo(id: UUID, params: UpdateTodoParams):
    todo = todos.get(id)

    if todo is None:
        return JSONResponse(
            status_code=404,
            content=ErrorMessage(message="Todoがありません").dict(),
        )

    if params.title:
        todo.title = params.title

    if params.finished is not None:
        todo.set_finished(params.finisehd)

    return todo


@app.delete("/todos/{id}", status_code=204)
def delete_todo(id: UUID):
    try:
        del todos[id]
    except KeyError:
        pass
