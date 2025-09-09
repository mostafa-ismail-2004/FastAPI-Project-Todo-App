from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError

router = APIRouter(prefix='/auth', tags=['auth'])

secret_key = '1f50912d83cc725d6d98f40422a225df6a72c91b1f09f013464273bb0c980e11'
algorithm = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#dependencies
db_dependency = Annotated[Session, Depends(get_db)]
login_dependency = Annotated[OAuth2PasswordRequestForm, Depends()]
oauth2bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

#Validating user creation request
class UserRequest(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    password: str
    is_active: bool = True
    role: str
    phone_number: str

class Token(BaseModel):
    access_token: str
    token_type: str


#Adding the user to the Users class to be added to the database
@router.post("/new-user", status_code=status.HTTP_201_CREATED)
def create_user(user: UserRequest, db: db_dependency):
    new_user = Users(
        email = user.email,
        username = user.username,
        first_name = user.first_name,
        last_name = user.last_name,
        hashed_password = bcrypt_context.hash(user.password),
        is_active = user.is_active,
        role = user.role,
        phone_number = user.phone_number
        )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "user_id": new_user.id}

#authenticate user and login

#spearate function for user authentication
def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return None
    match = bcrypt_context.verify(password, user.hashed_password)
    if not match:
        return False
    return user

#token creation function
def create_access_token(username, user_id, role, expiry_delta: timedelta):
    cairo_time = timezone(timedelta(hours=2))
    expiry = datetime.now(cairo_time) + expiry_delta
    encode = {'sub': username, 'id': user_id, 'role': role, 'exp': expiry}
    access_token = jwt.encode(encode, secret_key, algorithm=algorithm)
    return access_token

#A function to decode JWTs
def get_current_user(token: Annotated[str, Depends(oauth2bearer)]):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username = payload['sub']
        user_id = payload['id']
        user_role = payload['role']
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail='could not validate user')
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(status_code=401, detail='could not validate user')
    


#login endpoint
@router.post("/token", response_model=Token)
def login_for_access_token(credentials: login_dependency, db: db_dependency):
    user = authenticate_user(credentials.username, credentials.password, db)
    match user:
        case None:
            raise HTTPException(status_code=404, detail="User not found")
        case False:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        case _:
            token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
            return {"access_token": token, "token_type": "bearer"}