from fastapi import APIRouter, Depends, HTTPException, Path, status
from typing import Annotated
from pydantic import BaseModel, Field
from models import Todos
from database import SessionLocal
from sqlalchemy.orm import Session
from routers import auth

router = APIRouter(prefix='/todos', tags=['todos'])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(auth.get_current_user)]


#get all todos based on user
@router.get('/', status_code=status.HTTP_200_OK)
def get_todo_of_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='could not validate user')
    todos = db.query(Todos).filter(Todos.owner_id == user['id']).all()
    return todos

#fetch todo of user by ID
@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
def get_todo_by_id(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='could not validate user')
    todo = db.query(Todos).filter(Todos.owner_id == user['id']).filter(Todos.id == todo_id).first()
    if todo is not None:
        return todo
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="todo not found")
    
#post validation
class TodoRequest(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    priority: int = Field(gt=0, lt=6)

#update validation - allows updating complete status
class TodoUpdateRequest(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool
    
#create a todo
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_todo(user: user_dependency, db: db_dependency, todo: TodoRequest):
    if user['username'] is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='could not validate user')
    Todos_model = Todos(**todo.model_dump())
    Todos_model.owner_id = user['id']
    db.add(Todos_model)
    db.commit()
    db.refresh(Todos_model)
    return {"message": "Todo created successfully", "todo": Todos_model}

@router.put("/{todo_id}", status_code=status.HTTP_200_OK)
def update_todo(user: user_dependency,
                db: db_dependency,
                todo: TodoUpdateRequest,
                todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='could not validate user')
    original_todo = db.query(Todos).filter(Todos.owner_id == user['id']).filter(Todos.id == todo_id).first()
    if original_todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="todo not found")
    
    update = todo.model_dump()
    for key, value in update.items():
        setattr(original_todo, key, value)
    db.commit()
    db.refresh(original_todo)
    return {"message": "Todo updated successfully", "todo": original_todo}

#del req func
@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='could not validate user')
    todo = db.query(Todos).filter(Todos.owner_id == user['id']).filter(Todos.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="todo not found")
    
    db.delete(todo)
    db.commit()
    return None  # 204 No Content returns empty response