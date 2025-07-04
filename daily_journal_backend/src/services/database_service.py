from datetime import date
from typing import List, Optional
from ..models.journal_entry import JournalEntry, JournalEntryCreate, JournalEntryUpdate

class DatabaseService:
    """In-memory database service for journal entries, per-user."""

    def __init__(self):
        self._entries: List[JournalEntry] = []
        self._next_id = 1
        self._init_demo_data()

    def _init_demo_data(self):
        """Initialize with demo data for an initial demo user (user_id=1)"""
        demo_entries = [
            {
                "title": "First Day of Spring",
                "notes": "Today felt like a fresh start. The weather was perfect, and I spent most of the afternoon in the garden. There's something incredibly peaceful about planting new seeds and watching them grow. I'm feeling optimistic about the changes coming in my life.",
                "mood": "content",
                "date": "2024-03-20"
            },
            {
                "title": "Challenging Day at Work",
                "notes": "Had a difficult meeting with the team today. The project deadlines are tight, and everyone seems stressed. I'm trying to stay positive, but it's hard when everything feels overwhelming. Need to remember to take breaks and not let work consume me.",
                "mood": "anxious",
                "date": "2024-03-19"
            },
            {
                "title": "Weekend Adventures",
                "notes": "Went hiking with friends today! The trail was longer than expected, but the views were absolutely breathtaking. We packed a picnic and spent hours just talking and laughing. These are the moments that make life worth living.",
                "mood": "happy",
                "date": "2024-03-18"
            },
            {
                "title": "Quiet Evening Reflection",
                "notes": "Spent tonight reading by the fireplace. Sometimes the best evenings are the quiet ones. I've been thinking about what I want to achieve this year and how to balance ambition with contentment. Grateful for these peaceful moments.",
                "mood": "grateful",
                "date": "2024-03-17"
            },
            {
                "title": "Exciting News!",
                "notes": "Got the call today - I got the promotion! All those late nights and weekend work sessions have finally paid off. I'm so excited about the new responsibilities and the team I'll be working with. This feels like the beginning of something amazing.",
                "mood": "excited",
                "date": "2024-03-16"
            }
        ]

        demo_user_id = 1  # Demo user for initial journal demo

        for entry_data in demo_entries:
            entry = JournalEntry(
                id=self._next_id,
                title=entry_data["title"],
                notes=entry_data["notes"],
                mood=entry_data["mood"],
                date=date.fromisoformat(entry_data["date"]),
                user_id=demo_user_id
            )
            self._entries.append(entry)
            self._next_id += 1

    # PUBLIC_INTERFACE
    def get_all_entries(self, user_id: int) -> List[JournalEntry]:
        """Get all journal entries for a user, sorted by date (newest first)"""
        return sorted(
            [e for e in self._entries if e.user_id == user_id],
            key=lambda x: x.date,
            reverse=True
        )

    # PUBLIC_INTERFACE
    def get_entry_by_id(self, entry_id: int, user_id: int) -> Optional[JournalEntry]:
        """Get a specific journal entry (owned by user) by ID"""
        for entry in self._entries:
            if entry.id == entry_id and entry.user_id == user_id:
                return entry
        return None

    # PUBLIC_INTERFACE
    def create_entry(self, entry_data: JournalEntryCreate, user_id: int) -> JournalEntry:
        """Create a new journal entry for a user"""
        new_entry = JournalEntry(
            id=self._next_id,
            title=entry_data.title,
            notes=entry_data.notes,
            mood=entry_data.mood,
            date=entry_data.date,
            user_id=user_id
        )
        self._entries.append(new_entry)
        self._next_id += 1
        return new_entry

    # PUBLIC_INTERFACE
    def update_entry(self, entry_id: int, update_data: JournalEntryUpdate, user_id: int) -> Optional[JournalEntry]:
        """Update an existing journal entry (must be owned by user)"""
        entry = self.get_entry_by_id(entry_id, user_id)
        if not entry:
            return None

        # Update only provided fields
        if update_data.title is not None:
            entry.title = update_data.title
        if update_data.notes is not None:
            entry.notes = update_data.notes
        if update_data.mood is not None:
            entry.mood = update_data.mood
        if update_data.date is not None:
            entry.date = update_data.date

        return entry

    # PUBLIC_INTERFACE
    def delete_entry(self, entry_id: int, user_id: int) -> bool:
        """Delete a journal entry by ID (must be owned by user)"""
        for i, entry in enumerate(self._entries):
            if entry.id == entry_id and entry.user_id == user_id:
                del self._entries[i]
                return True
        return False

    # PUBLIC_INTERFACE
    def get_entries_by_mood(self, user_id: int, mood: str) -> List[JournalEntry]:
        """Get a user's journal entries filtered by mood"""
        filtered_entries = [entry for entry in self._entries if entry.user_id == user_id and entry.mood.lower() == mood.lower()]
        return sorted(filtered_entries, key=lambda x: x.date, reverse=True)

    # PUBLIC_INTERFACE
    def get_entries_by_date_range(self, user_id: int, start_date: date, end_date: date) -> List[JournalEntry]:
        """Get a user's journal entries within a date range"""
        filtered_entries = [
            entry for entry in self._entries
            if entry.user_id == user_id and start_date <= entry.date <= end_date
        ]
        return sorted(filtered_entries, key=lambda x: x.date, reverse=True)

# Global database instance
db_service = DatabaseService()
