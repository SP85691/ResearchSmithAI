from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.db.SessionManager import get_db
from app.models.UserModel import User
from app.configs.PasswordValidator import hash_password, verify_password
from app.schemas.UserSchema import CreateUser, UserLogin, UserResponse, UpdateUser, UpdatePasswordSchema
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = str(os.getenv("SECRET_KEY"))
ALGORITHM = str(os.getenv("ALGORITHM"))
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

router = APIRouter()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

@router.get("/user-details", response_model=UserResponse)
def get_user_details(current_user: User = Depends(get_current_user)):
    """
    Fetch the current user's details.
    """
    return current_user

@router.post("/register", response_model=UserResponse)
def register_user(user: CreateUser, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = hash_password(user.password)
    
    # Exclude 'password' from user.dict() since we provide it explicitly
    new_user = User(**user.dict(exclude={"password"}), password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login_user(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    access_token = create_access_token(data={"sub": db_user.username})
    
    # Set token as an HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=30 * 60,  # Token expiration (30 minutes)
        samesite="Strict",
        secure=True  # Use `True` in production for HTTPS
    )
    
    return {"message": "Login successful"}

@router.put("/update", response_model=UserResponse)
def update_user(
    user_update: UpdateUser,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_user = db.query(User).filter(User.id == current_user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.first_name = user_update.first_name
    db_user.last_name = user_update.last_name
    db_user.phone = user_update.phone
    db.commit()
    db.refresh(db_user)
    return db_user

@router.put("/update-password")
def update_password(
    payload: UpdatePasswordSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update the user's password after validating the old password.
    """
    old_password = payload.old_password
    new_password = payload.new_password

    # Fetch the current user from the database
    db_user = db.query(User).filter(User.id == current_user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate the old password
    if not verify_password(old_password, db_user.password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    # Ensure the new password meets security requirements
    if len(new_password) < 8:
        raise HTTPException(
            status_code=400, detail="New password must be at least 8 characters long"
        )

    # Hash and update the new password
    db_user.password = hash_password(new_password)
    db.commit()

    return {"message": "Password updated successfully"}

@router.post("/logout")
def logout_user(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}



