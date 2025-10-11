from typing import List, Optional
from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# Хранилище данных в памяти
todos = []
current_id = 1

class Todo(BaseModel):
    id: Optional[int] = None
    item: str

    @classmethod
    def as_form(
        cls,
        item: str = Form(...)
    ):
        return cls(item=item)

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "item": "Example schema!"
            }
        }

class TodoItem(BaseModel):
    item: str

    class Config:
        schema_extra = {
            "example": {
                "item": "Read the next chapter of the book"
            }
        }

class TodoItems(BaseModel):
    todos: List[TodoItem]

    class Config:
        schema_extra = {
            "example": {
                "todos": [
                    {
                        "item": "Example schema 1!"
                    },
                    {
                        "item": "Example schema 2!"
                    }
                ]
            }
        }

# Роуты для работы с todo

@app.get("/todos", response_model=TodoItems)
async def get_todos():
    """Получить все todos"""
    return TodoItems(todos=[TodoItem(item=todo.item) for todo in todos])

@app.get("/todos/{todo_id}", response_model=Todo)
async def get_todo(todo_id: int):
    """Получить todo по ID"""
    todo = next((todo for todo in todos if todo.id == todo_id), None)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.post("/todos", response_model=Todo)
async def create_todo(todo: Todo):
    """Создать todo через JSON"""
    global current_id
    todo.id = current_id
    current_id += 1
    todos.append(todo)
    return todo

@app.post("/todos/form", response_model=Todo)
async def create_todo_via_form(todo: Todo = Form(...)):
    """Создать todo через форму"""
    global current_id
    todo.id = current_id
    current_id += 1
    todos.append(todo)
    return todo

@app.post("/todos/form-alternative", response_model=Todo)
async def create_todo_via_form_alternative(item: str = Form(...)):
    """Создать todo через форму (альтернативный способ)"""
    global current_id
    todo = Todo(id=current_id, item=item)
    current_id += 1
    todos.append(todo)
    return todo

@app.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(todo_id: int, updated_todo: Todo):
    """Обновить todo"""
    todo_index = next((index for index, todo in enumerate(todos) if todo.id == todo_id), None)
    if todo_index is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    updated_todo.id = todo_id
    todos[todo_index] = updated_todo
    return updated_todo

@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    """Удалить todo"""
    todo_index = next((index for index, todo in enumerate(todos) if todo.id == todo_id), None)
    if todo_index is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    deleted_todo = todos.pop(todo_index)
    return {"message": "Todo deleted", "todo": deleted_todo}

# Инициализация некоторых тестовых данных
@app.on_event("startup")
async def startup_event():
    """Добавляем тестовые данные при запуске"""
    global todos, current_id
    if not todos:
        sample_todos = [
            Todo(id=1, item="Изучить FastAPI"),
            Todo(id=2, item="Написать приложение"),
            Todo(id=3, item="Протестировать API")
        ]
        todos.extend(sample_todos)
        current_id = 4

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)