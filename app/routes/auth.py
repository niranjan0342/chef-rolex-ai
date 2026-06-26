from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import database, schemas
from app.db import crud
from app.utils.auth import get_password_hash, verify_password, create_access_token, SECRET_KEY, ALGORITHM
from app.utils.limiter import limiter
import jwt
from jwt.exceptions import InvalidTokenError

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user


def get_current_user_optional(token: str = Depends(OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)), db: Session = Depends(get_db)):
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except InvalidTokenError:
        return None
    user = crud.get_user_by_username(db, username=username)
    return user


@router.post("/register", response_model=schemas.UserResponse)
@limiter.limit("5/minute")
def register(request: Request, user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    db_email = crud.get_user_by_email(db, email=user.email)
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    new_user = database.User(username=user.username, email=user.email, password_hash=hashed_password)
    return crud.create_user(db, new_user)


@router.post("/login", response_model=schemas.Token)
@limiter.limit("5/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user: database.User = Depends(get_current_user)):
    return current_user