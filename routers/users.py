from fastapi import APIRouter, Depends, HTTPException, Path, status
from typing import Annotated, cast
from pydantic import BaseModel, Field
from models import Todos, Users
from database import SessionLocal
from sqlalchemy.orm import Session
from routers import auth
from passlib.context import CryptContext

router = APIRouter(prefix='/users', tags=['users'])

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(auth.get_current_user)]

@router.get('/user-info', status_code=status.HTTP_200_OK)
def get_active_users(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
    current_user = db.query(Users).filter(Users.id == user['id']).first()
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    user_info = {'ID': current_user.id,
                 'Username': current_user.username,
                 'Email': current_user.email,
                 'First Name': current_user.first_name,
                 'Last Name': current_user.last_name,
                 'Status': current_user.is_active,
                 'Role': current_user.role,
                 'Phone Number': current_user.phone_number}
    return user_info

@router.post('/change-password', status_code=status.HTTP_204_NO_CONTENT)
def change_password(user: user_dependency, db: db_dependency, old_password: str, new_password: str):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
    current_user = db.query(Users).filter(Users.id == user['id']).first()
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    match = bcrypt_context.verify(old_password, str(current_user.hashed_password))
    if not match:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Current password is incorrect')
    hashed_new_password = bcrypt_context.hash(new_password)
    setattr(current_user, 'hashed_password', hashed_new_password)
    db.commit()
    # Return 204 No Content for successful password change

@router.post('/change-phone-number', status_code=status.HTTP_204_NO_CONTENT)
def change_phone_number(user: user_dependency, db: db_dependency, new_phone_number: str):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
    current_user = db.query(Users).filter(Users.id == user['id']).first()
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    setattr(current_user, 'phone_number', new_phone_number)
    db.commit()
    # Return 204 No Content for successful phone number change