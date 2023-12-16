from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

import crud, models, middleware
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)


app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Schemas
class User(BaseModel):
    username: str
    password: str


# register user
@app.post("/user/register")
def register_user(user: User, db: Session = Depends(get_db)):
    get_user = crud.get_user_by_username(db, username=user.username)
    if get_user:
        raise HTTPException(status_code=400, detail="username already registered")
    userCreated = crud.create_user(db, username=user.username, password=user.password)
    return {"data": userCreated}


# login user
@app.post("/user/login")
async def login_user(user: User, db: Session = Depends(get_db)):
    get_user = crud.get_user_by_username(db, username=user.username)
    if get_user is None:
        raise HTTPException(status_code=400, detail="username not registered")
    verify_password = crud.verify_password(plain_password=user.password, hashed_password=get_user.password)
    if not verify_password:
        raise HTTPException(status_code=400, detail="password not match")
    token = crud.get_token(id=get_user.id, username=get_user.username)
    return {"data": token}


# get all user with custom auth middleware
@app.get("/user")
async def get_users(current_user: Annotated[str, Depends(middleware.verify_user)], db: Session = Depends(get_db)):
    users = crud.get_users(db)
    return {"signed_user":current_user, "data": users}

# Update user by ID
@app.put("/user/{user_id}")
async def update_user(user_id: int, new_user: User, db: Session = Depends(get_db)):
    updated_user = crud.update_user(db, user_id, new_user.username, new_user.password)
    if updated_user:
        return {"data": updated_user}
    raise HTTPException(status_code=404, detail="User not found")

# Delete user by ID
@app.delete("/user/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    success = crud.delete_user(db, user_id)
    if success:
        return {"message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")

# Read user by ID
@app.get("/user/{user_id}")
async def read_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, user_id)
    if user:
        return {"data": user}
    raise HTTPException(status_code=404, detail="User not found")