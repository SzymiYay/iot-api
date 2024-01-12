from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from fastapi_sqlalchemy import db

from src.auth import crud as auth_crud
from src.utils import jwt_util
from src.utils import constant_util

from src.auth import schemas as auth_schema
from src import models as auth_model


router = APIRouter(
    prefix="/api/v1",
    tags=["Auth"]
)


@router.post("/auth/signup", 
          response_model=auth_schema.User, 
          tags=["Auth"], 
          status_code=status.HTTP_201_CREATED,
          response_description="User created successfully")
async def create_user(user: auth_schema.UserCreate):
    auth_crud.check_existing_user(user.username)
    db_user = auth_crud.create_user(user)
    return db_user


@router.post("/auth/login", 
          response_model=auth_schema.Token, 
          tags=["Auth"],
          status_code=status.HTTP_201_CREATED,
          response_description="Token created successfully")
async def login_for_access_token(from_data: OAuth2PasswordRequestForm = Depends()):
    user = jwt_util.authenticate_user(from_data.username, from_data.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    
    if user.disabled:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user", headers={"WWW-Authenticate": "Bearer"})
    
    existing_token = auth_crud.find_token_by_user_id(user.id)

    if not existing_token:
        access_token_expires = timedelta(minutes=constant_util.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(minutes=constant_util.REFRESH_TOKEN_EXPIRE_MINUTES)
        access_token = jwt_util.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
        refresh_token = jwt_util.create_access_token(data={"sub": user.username}, expires_delta=refresh_token_expires)

        db_token = auth_model.Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer", status=True, user_id=user.id)
        db.session.add(db_token)
        db.session.commit()

        return {"access_token": access_token,"refresh_token": refresh_token, "token_type": "bearer"}
    
    jwt_util.get_current_active_user(existing_token.access_token)
    
    return {"access_token": existing_token.access_token,"refresh_token": existing_token.refresh_token, "token_type": "bearer"}


@router.post("/auth/token/refresh", 
          response_model=auth_schema.RefreshToken, 
          tags=["Auth"],
          status_code=status.HTTP_201_CREATED,
          response_description="Token refreshed successfully")
async def refresh_token(from_data: OAuth2PasswordRequestForm = Depends()):
    user = jwt_util.authenticate_user(from_data.username, from_data.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    
    if user.disabled:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user", headers={"WWW-Authenticate": "Bearer"})
    
    token = auth_crud.find_token_by_user_id(user.id)

    if not token.status:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is not active", headers={"WWW-Authenticate": "Bearer"})
    
    access_token_expires = timedelta(minutes=constant_util.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=constant_util.REFRESH_TOKEN_EXPIRE_MINUTES)
    access_token = jwt_util.create_access_token(data={"sub": token.user.username}, expires_delta=access_token_expires)
    refresh_token = jwt_util.create_access_token(data={"sub": token.user.username}, expires_delta=refresh_token_expires)

    db_token = auth_crud.find_token_by_id(token.id)
    db_token.access_token = access_token
    db_token.refresh_token = refresh_token
    auth_crud.update_token(db_token)

    return {"refresh_token": refresh_token}
