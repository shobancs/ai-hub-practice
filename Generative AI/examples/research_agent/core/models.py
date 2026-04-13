"""
Data models for the Research Assistant Agent.

Uses dataclasses for structured data throughout the agent.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class SearchResult:
    """A single search result from the web search tool."""
    title: str
    url: str
    snippet: str
    source: str = "web"


@dataclass
class Note:
    """A research note stored by the agent."""
    id: int
    content: str
    tags: list[str] = field(default_factory=list)
    source: Optional[str] = None
    created_at: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


@dataclass
class ResearchSession:
    """Tracks the state of a research session."""
    topic: str
    notes: list[Note] = field(default_factory=list)
    searches_performed: list[str] = field(default_factory=list)
    sources_consulted: list[str] = field(default_factory=list)
    started_at: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    _note_counter: int = field(default=0, repr=False)

    def add_note(self, content: str, tags: list[str] | None = None,
                 source: str | None = None) -> Note:
        """Create and store a new note, returning it."""
        self._note_counter += 1
        note = Note(
            id=self._note_counter,
            content=content,
            tags=tags or [],
            source=source,
        )
        self.notes.append(note)
        return note

    def get_notes_summary(self) -> str:
        """Return a numbered summary of all notes."""
        if not self.notes:
            return "No notes taken yet."
        lines = []
        for n in self.notes:
            tags = f" [{', '.join(n.tags)}]" if n.tags else ""
            lines.append(f"  {n.id}. {n.content}{tags}")
        return "\n".join(lines)
