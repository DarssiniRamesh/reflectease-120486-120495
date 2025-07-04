from datetime import date
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from ..models.journal_entry import JournalEntry, JournalEntryCreate, JournalEntryUpdate
from ..services.database_service import db_service

router = APIRouter(
    prefix="/entries",
    tags=["journal_entries"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[JournalEntry])
async def get_all_entries(
    mood: Optional[str] = Query(None, description="Filter by mood"),
    start_date: Optional[date] = Query(None, description="Start date for date range filter"),
    end_date: Optional[date] = Query(None, description="End date for date range filter")
):
    """
    Get all journal entries with optional filtering.
    
    - **mood**: Filter entries by mood (e.g., happy, sad, excited)
    - **start_date**: Filter entries from this date onwards
    - **end_date**: Filter entries up to this date
    
    Returns entries sorted by date (newest first).
    """
    if mood:
        return db_service.get_entries_by_mood(mood)
    elif start_date and end_date:
        return db_service.get_entries_by_date_range(start_date, end_date)
    elif start_date:
        # If only start_date is provided, get entries from start_date to today
        today = date.today()
        return db_service.get_entries_by_date_range(start_date, today)
    else:
        return db_service.get_all_entries()


@router.get("/{entry_id}", response_model=JournalEntry)
async def get_entry(entry_id: int):
    """
    Get a specific journal entry by ID.
    
    - **entry_id**: The ID of the journal entry to retrieve
    """
    entry = db_service.get_entry_by_id(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return entry


@router.post("/", response_model=JournalEntry, status_code=201)
async def create_entry(entry: JournalEntryCreate):
    """
    Create a new journal entry.
    
    - **title**: Title of the journal entry (required)
    - **notes**: Detailed notes/content (required)
    - **mood**: Mood tag for the entry (required)
    - **date**: Date of the entry (required)
    """
    return db_service.create_entry(entry)


@router.put("/{entry_id}", response_model=JournalEntry)
async def update_entry(entry_id: int, entry_update: JournalEntryUpdate):
    """
    Update an existing journal entry.
    
    - **entry_id**: The ID of the journal entry to update
    - **title**: New title (optional)
    - **notes**: New notes/content (optional)
    - **mood**: New mood tag (optional)
    - **date**: New date (optional)
    """
    updated_entry = db_service.update_entry(entry_id, entry_update)
    if updated_entry is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return updated_entry


@router.delete("/{entry_id}", status_code=204)
async def delete_entry(entry_id: int):
    """
    Delete a journal entry by ID.
    
    - **entry_id**: The ID of the journal entry to delete
    """
    success = db_service.delete_entry(entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return None
