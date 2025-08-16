import os
from typing import Annotated
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Path, Request, status
from pydantic import BaseModel, Field
from starlette import status
import models
from database import SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user
from starlette.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

# templates_dir = os.path.join(os.getcwd(), "templates")

# templates = Jinja2Templates(directory=templates_dir)
templates = Jinja2Templates(directory="templates")


router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, le=6)
    complete: bool

def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response


### Pages ###


@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    if request.cookies.get("access_token") is None:
        return redirect_to_login()
    
    try:
        user = await get_current_user(request.cookies.get("access_token")) # type: ignore
        if user is None:
            return redirect_to_login()
        
        todos = db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).all()
        return templates.TemplateResponse("todo.html", {"request": request, "todos": todos, "user": user})
    except:
        return redirect_to_login()
    
@router.get('/add-todo-page')
async def render_add_todo_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get("access_token")) # type: ignore
        if user is None:
            return redirect_to_login()
        
        return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})
    except:
        return redirect_to_login()
    
@router.get('/edit-todo-page/{todo_id}')
async def render_edit_todo_page(request: Request, db: db_dependency, todo_id: int = Path(gt=0)):
    try:
        user = await get_current_user(request.cookies.get("access_token")) # type: ignore
        if user is None:
            return redirect_to_login()

        todo = db.query(models.Todos).filter(models.Todos.id == todo_id, models.Todos.owner_id == user.get("id")).first()
        if todo is None:
            return redirect_to_login()

        return templates.TemplateResponse("edit-todo.html", {"request": request, "user": user, "todo": todo})
    except:
        return redirect_to_login()


### Endpoints ###

@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    todos = db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).all()
    return todos

@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id, models.Todos.owner_id == user.get("id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
       
    return todo_model

@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, todo_request: TodoRequest, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    todo_model = models.Todos(**todo_request.model_dump(), owner_id=user.get("id"))  # type: ignore
    db.add(todo_model)
    db.commit()

@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, todo_request: TodoRequest, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id, models.Todos.owner_id == user.get("id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    for key, value in todo_request.model_dump().items():
        setattr(todo_model, key, value)
    
    db.commit()
    return todo_model

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id, models.Todos.owner_id == user.get("id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.query(models.Todos).filter(models.Todos.id == todo_id, models.Todos.owner_id == user.get("id")).delete()
    db.commit()
