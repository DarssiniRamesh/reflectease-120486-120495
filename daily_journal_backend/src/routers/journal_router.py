from datetime import date
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from ..models.journal_entry import JournalEntry, JournalEntryCreate, JournalEntryUpdate
from ..services.database_service import db_service
from .auth_router import get_current_user

router = APIRouter(
    prefix="/entries",
    tags=["journal_entries"],
    responses={404: {"description": "Not found"}},
    # Note: Do not set a global dependency here to facilitate OpenAPI display for unauthenticated routes.
)

# PUBLIC_INTERFACE
@router.get(
    "/", 
    response_model=List[JournalEntry],
    summary="List all journal entries (user-specific)",
    description="Get all journal entries for the current user, optionally filtering by mood or date range.",
)
async def get_all_entries(
    mood: Optional[str] = Query(None, description="Filter by mood"),
    start_date: Optional[date] = Query(None, description="Start date for date range filter"),
    end_date: Optional[date] = Query(None, description="End date for date range filter"),
    user=Depends(get_current_user),
):
    """
    Get all journal entries for the authenticated user, with optional filtering.

    - **mood**: Filter entries by mood (e.g., happy, sad, excited)
    - **start_date**: Filter entries from this date onwards
    - **end_date**: Filter entries up to this date

    Only entries owned by the current user are returned.
    """
    user_id = user.id
    if mood:
        return db_service.get_entries_by_mood(user_id, mood)
    elif start_date and end_date:
        return db_service.get_entries_by_date_range(user_id, start_date, end_date)
    elif start_date:
        # If only start_date is provided, get entries from start_date to today
        today = date.today()
        return db_service.get_entries_by_date_range(user_id, start_date, today)
    else:
        return db_service.get_all_entries(user_id)

# PUBLIC_INTERFACE
@router.get(
    "/{entry_id}", 
    response_model=JournalEntry,
    summary="Get a journal entry by ID (user-specific)",
    description="Retrieve a specific journal entry by its ID. Only entries owned by the current user can be accessed.",
)
async def get_entry(
    entry_id: int, 
    user=Depends(get_current_user)
):
    """
    Get a specific journal entry for the authenticated user by ID.

    The entry must belong to the current user or a 404 will be returned.
    """
    entry = db_service.get_entry_by_id(entry_id, user.id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return entry

# PUBLIC_INTERFACE
@router.post(
    "/", 
    response_model=JournalEntry,
    status_code=201,
    summary="Create a new journal entry (user-specific)",
    description="Create a journal entry for the current authenticated user."
)
async def create_entry(
    entry: JournalEntryCreate, 
    user=Depends(get_current_user)
):
    """
    Create a new journal entry for the authenticated user.

    The created entry will be associated with the current user only.
    """
    return db_service.create_entry(entry, user.id)

# PUBLIC_INTERFACE
@router.put(
    "/{entry_id}",
    response_model=JournalEntry,
    summary="Update a journal entry (user-specific)",
    description="Update an existing journal entry. Only entries owned by the current user can be updated."
)
async def update_entry(
    entry_id: int, 
    entry_update: JournalEntryUpdate, 
    user=Depends(get_current_user)
):
    """
    Update an existing journal entry for the authenticated user.

    Only entries owned by the current user can be changed; otherwise, a 404 is returned.
    """
    updated_entry = db_service.update_entry(entry_id, entry_update, user.id)
    if updated_entry is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return updated_entry

# PUBLIC_INTERFACE
@router.delete(
    "/{entry_id}",
    status_code=204,
    summary="Delete a journal entry (user-specific)",
    description="Delete a journal entry owned by the current user."
)
async def delete_entry(
    entry_id: int, 
    user=Depends(get_current_user)
):
    """
    Delete a journal entry by ID for the authenticated user.

    Only entries owned by the current user can be deleted; otherwise a 404 is returned.
    """
    success = db_service.delete_entry(entry_id, user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return None
