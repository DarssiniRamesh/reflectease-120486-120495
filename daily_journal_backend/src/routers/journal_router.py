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
)

@router.get("/", response_model=List[JournalEntry])
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

@router.get("/{entry_id}", response_model=JournalEntry)
async def get_entry(entry_id: int, user=Depends(get_current_user)):
    """
    Get a specific journal entry for the authenticated user by ID.
    """
    entry = db_service.get_entry_by_id(entry_id, user.id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return entry

@router.post("/", response_model=JournalEntry, status_code=201)
async def create_entry(entry: JournalEntryCreate, user=Depends(get_current_user)):
    """
    Create a new journal entry for the authenticated user.
    """
    return db_service.create_entry(entry, user.id)

@router.put("/{entry_id}", response_model=JournalEntry)
async def update_entry(entry_id: int, entry_update: JournalEntryUpdate, user=Depends(get_current_user)):
    """
    Update an existing journal entry for the authenticated user.
    """
    updated_entry = db_service.update_entry(entry_id, entry_update, user.id)
    if updated_entry is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return updated_entry

@router.delete("/{entry_id}", status_code=204)
async def delete_entry(entry_id: int, user=Depends(get_current_user)):
    """
    Delete a journal entry by ID for the authenticated user.
    """
    success = db_service.delete_entry(entry_id, user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return None
