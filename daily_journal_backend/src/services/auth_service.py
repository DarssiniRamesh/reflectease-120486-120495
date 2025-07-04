from typing import Optional, Dict
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from ..models.user import UserCreate, UserInDB
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secret-key")  # Should be overridden in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory user store: username -> UserInDB
class UserStore:
    def __init__(self):
        self._users: Dict[str, UserInDB] = {}
        self._id_counter = 1

    # PUBLIC_INTERFACE
    def get_user(self, username: str) -> Optional[UserInDB]:
        """Return the user by username, or None."""
        return self._users.get(username)

    # PUBLIC_INTERFACE
    def get_user_by_id(self, user_id: int) -> Optional[UserInDB]:
        for user in self._users.values():
            if user.id == user_id:
                return user
        return None

    # PUBLIC_INTERFACE
    def create_user(self, user_create: UserCreate) -> UserInDB:
        if user_create.username in self._users:
            raise ValueError("Username already exists")
        password_hash = pwd_context.hash(user_create.password)
        user = UserInDB(id=self._id_counter, username=user_create.username, password_hash=password_hash)
        self._users[user_create.username] = user
        self._id_counter += 1
        return user

    # PUBLIC_INTERFACE
    def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        user = self._users.get(username)
        if not user:
            return None
        if not pwd_context.verify(password, user.password_hash):
            return None
        return user

user_store = UserStore()

# PUBLIC_INTERFACE
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Generate a JWT token with username and user_id"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# PUBLIC_INTERFACE
def verify_access_token(token: str) -> Optional[dict]:
    """Verify JWT and return payload if valid, else None"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
