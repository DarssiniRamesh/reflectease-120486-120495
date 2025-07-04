from pydantic import BaseModel, Field

# PUBLIC_INTERFACE
class UserBase(BaseModel):
    """Base model for user information"""
    username: str = Field(..., min_length=3, max_length=32, description="Unique username for the user")


# PUBLIC_INTERFACE
class UserCreate(UserBase):
    """User registration input model"""
    password: str = Field(..., min_length=6, description="User password (min 6 chars)")


# PUBLIC_INTERFACE
class UserInDB(UserBase):
    """User as stored in DB with password hash"""
    id: int
    password_hash: str

    class Config:
        from_attributes = True


# PUBLIC_INTERFACE
class UserLogin(BaseModel):
    """User login input model"""
    username: str
    password: str


# PUBLIC_INTERFACE
class UserPublic(UserBase):
    """Public user model (returned to frontend, contains no password info)"""
    id: int

    class Config:
        from_attributes = True
