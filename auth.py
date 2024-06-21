from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import JWTError , jwt

router=APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY='a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6'
ALGORITHM='HS256'

bcrypt_context=CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer=OAuth2PasswordBearer(tokenUrl='/auth/token')

class Create_User_Request(BaseModel):
    username:str
    password:str
    
class Token(BaseModel):
    access_token:str
    token_type:str

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session, Depends(get_db)]

@router.post("/" , status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependency , create_user_request:Create_User_Request):
    create_user_model=Users(
        username=create_user_request.username,
        hashed_password=bcrypt_context.hash(create_user_request.password),
    )
    db.add(create_user_model)
    db.commit()

@router.post("/token", response_model=Token)
async def login_for_access_token(db:db_dependency,
                                 form_data:Annotated[OAuth2PasswordRequestForm, Depends()]):
    user=authenticate_user(form_data.username,form_data.password,db)
    if not user:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, 
                            detail="Couldn't validate user")
    token=create_access_token(user.username , user.id , timedelta(minutes=20))
    
    return {"access_token":token , "token_type":"bearer"}

def authenticate_user(username:str, password:str, db:db_dependency):
    user=db.query(Users).filter(Users.username==username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password , user.hashed_password): ##check this line if code doesnt work
        return False
    return user

def create_access_token(username:str , user_id:int , expires_delta:timedelta):
    encode={'sub':username , 'id':user_id}
    expires=datetime.utcnow() + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode , SECRET_KEY , algorithm=ALGORITHM)

def get_current_user(token:Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload=jwt.decode(token , SECRET_KEY, algorithms=ALGORITHM)
        username:str = payload.get("sub")
        user_id:int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return {"username":username , "id":user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate user")
