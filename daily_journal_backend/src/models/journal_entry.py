from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class JournalEntryBase(BaseModel):
    """Base model for journal entries with common fields"""
    title: str = Field(..., min_length=1, max_length=500, description="Title of the journal entry")
    notes: str = Field(..., min_length=1, description="Detailed notes/content of the journal entry")
    mood: str = Field(..., min_length=1, max_length=50, description="Mood tag for the entry")
    date: date = Field(..., description="Date of the journal entry")


class JournalEntryCreate(JournalEntryBase):
    """Model for creating a new journal entry"""
    pass


class JournalEntryUpdate(BaseModel):
    """Model for updating an existing journal entry"""
    title: Optional[str] = Field(None, min_length=1, max_length=500, description="Title of the journal entry")
    notes: Optional[str] = Field(None, min_length=1, description="Detailed notes/content of the journal entry")
    mood: Optional[str] = Field(None, min_length=1, max_length=50, description="Mood tag for the entry")
    date: Optional[date] = Field(None, description="Date of the journal entry")


class JournalEntry(JournalEntryBase):
    """Complete journal entry model with ID"""
    id: int = Field(..., description="Unique identifier for the journal entry")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "First Day of Spring",
                "notes": "Today felt like a fresh start. The weather was perfect...",
                "mood": "content",
                "date": "2024-03-20"
            }
        }
