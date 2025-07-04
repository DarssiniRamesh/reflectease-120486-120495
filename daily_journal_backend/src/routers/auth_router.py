from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from ..models.user import UserCreate, UserPublic
from ..services.auth_service import user_store, create_access_token, verify_access_token

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# PUBLIC_INTERFACE
@router.post("/register", response_model=UserPublic, status_code=201, summary="Register a new user", description="Register a new user with username and password.")
async def register(user: UserCreate):
    """User registration endpoint."""
    try:
        user_in_db = user_store.create_user(user)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return UserPublic(id=user_in_db.id, username=user_in_db.username)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# PUBLIC_INTERFACE
@router.post("/login", response_model=TokenResponse, summary="Login and receive JWT", description="Authenticate and get a JWT token.")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_store.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token({"sub": user.username, "user_id": user.id})
    return TokenResponse(access_token=token)

# PUBLIC_INTERFACE
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    username = payload.get("sub")
    user_id = payload.get("user_id")
    user = user_store.get_user(username)
    if not user or user.id != user_id:
        raise HTTPException(status_code=401, detail="Invalid token / user")
    return user
