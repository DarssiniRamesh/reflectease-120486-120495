from datetime import date
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends, Header
from fastapi import status
from ..models.journal_entry import JournalEntry, JournalEntryCreate, JournalEntryUpdate
from ..services.database_service import db_service
import requests
import os
import jwt

CLERK_JWT_ISSUER = os.getenv("CLERK_JWT_ISSUER", "https://api.clerk.dev")
CLERK_JWT_PUBLIC_KEY_URL = os.getenv("CLERK_JWT_PUBLIC_KEY_URL")

def get_clerk_public_key():
    """
    Fetch Clerk public key once and cache it (use proper JWKS in production).
    """
    if not hasattr(get_clerk_public_key, "cache"):
        if not CLERK_JWT_PUBLIC_KEY_URL:
            raise RuntimeError("CLERK_JWT_PUBLIC_KEY_URL must be set in environment for Clerk JWT verification.")
        key_response = requests.get(CLERK_JWT_PUBLIC_KEY_URL)
        if key_response.status_code != 200:
            raise RuntimeError("Failed to fetch Clerk JWT public key")
        get_clerk_public_key.cache = key_response.text
    return get_clerk_public_key.cache

# PUBLIC_INTERFACE
async def verify_clerk_jwt(authorization: str = Header(..., description="Bearer Clerk JWT Token")) -> str:
    """
    FastAPI dependency to check & decode Clerk JWT, returning Clerk user ID.

    This ensures every endpoint using this dependency is protected by Clerk.
    Raises HTTP_401 if missing or invalid.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Bearer token")
    token = authorization[len("Bearer "):]
    try:
        public_key = get_clerk_public_key()
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            options={"verify_aud": False},
            issuer=CLERK_JWT_ISSUER,
        )
        clerk_user_id = payload.get("sub") or payload.get("user_id")
        if not clerk_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Clerk JWT: user_id missing"
            )
        return clerk_user_id
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired Clerk JWT")

router = APIRouter(
    prefix="/entries",
    tags=["journal_entries"],
    responses={404: {"description": "Not found"}},
)

# PUBLIC_INTERFACE
@router.get(
    "/",
    response_model=List[JournalEntry],
    summary="List all journal entries for the authenticated Clerk user",
    description="Get all journal entries associated with the authenticated Clerk user."
)
async def get_all_entries(
    mood: Optional[str] = Query(None, description="Filter by mood"),
    start_date: Optional[date] = Query(None, description="Start date for date range filter"),
    end_date: Optional[date] = Query(None, description="End date for date range filter"),
    user_id: str = Depends(verify_clerk_jwt),
):
    """
    Get all journal entries for the authenticated Clerk user.
    """
    if mood:
        return db_service.get_entries_by_mood(user_id, mood)
    elif start_date and end_date:
        return db_service.get_entries_by_date_range(user_id, start_date, end_date)
    elif start_date:
        today = date.today()
        return db_service.get_entries_by_date_range(user_id, start_date, today)
    else:
        return db_service.get_all_entries(user_id)

# PUBLIC_INTERFACE
@router.get(
    "/{entry_id}",
    response_model=JournalEntry,
    summary="Get a journal entry by ID for the authenticated Clerk user",
    description="Retrieve a specific journal entry by its ID for the Clerk user."
)
async def get_entry(
    entry_id: int,
    user_id: str = Depends(verify_clerk_jwt)
):
    """
    Get a specific journal entry for the authenticated Clerk user by ID.
    """
    entry = db_service.get_entry_by_id(entry_id, user_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return entry

# PUBLIC_INTERFACE
@router.post(
    "/",
    response_model=JournalEntry,
    status_code=201,
    summary="Create a new journal entry for the authenticated Clerk user",
    description="Create a journal entry for the current Clerk authenticated user."
)
async def create_entry(
    entry: JournalEntryCreate,
    user_id: str = Depends(verify_clerk_jwt)
):
    """
    Create a new journal entry for the authenticated Clerk user.
    """
    return db_service.create_entry(entry, user_id)

# PUBLIC_INTERFACE
@router.put(
    "/{entry_id}",
    response_model=JournalEntry,
    summary="Update a journal entry for the authenticated Clerk user",
    description="Update an existing journal entry for the Clerk user."
)
async def update_entry(
    entry_id: int,
    entry_update: JournalEntryUpdate,
    user_id: str = Depends(verify_clerk_jwt)
):
    """
    Update an existing journal entry for the authenticated Clerk user.
    """
    updated_entry = db_service.update_entry(entry_id, entry_update, user_id)
    if updated_entry is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return updated_entry

# PUBLIC_INTERFACE
@router.delete(
    "/{entry_id}",
    status_code=204,
    summary="Delete a journal entry for the authenticated Clerk user",
    description="Delete a journal entry owned by the Clerk user."
)
async def delete_entry(
    entry_id: int,
    user_id: str = Depends(verify_clerk_jwt)
):
    """
    Delete a journal entry by ID for the authenticated Clerk user.
    """
    success = db_service.delete_entry(entry_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return None
