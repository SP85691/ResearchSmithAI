from pydantic import BaseModel, EmailStr

class CreateUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    phone: str
    password: str

class UpdateUser(BaseModel):
    first_name: str
    last_name: str
    phone: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    phone: str

    class Config:
        orm_mode = True
        
class UpdatePasswordSchema(BaseModel):
    old_password: str
    new_password: str

class ForgotPassword(BaseModel):
    email: EmailStr
