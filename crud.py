from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt

import models


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# get user by username
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


# get all user
def get_users(db: Session):
    return db.query(models.User).all()


# register user
def create_user(db: Session, username: str, password: str):
    hashed_password = pwd_context.hash(password)
    user = models.User(username=username, password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# verify password
def verify_password(plain_password: str, hashed_password: str):
    verify_user_password = pwd_context.verify(plain_password, hashed_password)
    if not verify_user_password:
        return False
    return True


# get token
def get_token(id: int, username:str):
    encoded_jwt = jwt.encode({"id":id, "username":username}, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
