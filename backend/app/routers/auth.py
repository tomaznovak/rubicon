from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from .. import schemas, utils, oauth2
from backend.db import models, database


router = APIRouter(tags=['Authentication'])

@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=f"Invalid Credentials",
            headers={"WWW-Authenticate": "Bearer"}
            )
    
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=f"Invalid Credentials",
            headers={"WWW-Authenticate": "Bearer"}
            )
    
    access_token = oauth2.create_access_token(data = {"user_id": user.id})

    refresh_token = oauth2.create_refresh_token(data={"user_id": user.id})
    
    return {"access_token": access_token, 
            "refresh_token": refresh_token,
            "token_type": "bearer"
            }

@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut) 
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):

    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/refresh")
async def refresh_token(refresh_token: str = Depends(oauth2.oauth2_scheme)):
    try:
        payload = oauth2.verify_refresh_token(refresh_token)
        access_token = oauth2.create_access_token(data={"user_id": payload.get("user_id")})
        return {"access_token": access_token, "token_type": "bearer"}
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )