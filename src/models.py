from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ActionItem(BaseModel):
    task: str = Field(..., description="Description of the action item")
    assignee: Optional[str] = Field(None, description="Person assigned to the task")
    due_date: Optional[str] = Field(None, description="Due date if specified")


class MeetingSummary(BaseModel):
    overview: str = Field(..., description="High-level summary of the meeting")
    key_decisions: List[str] = Field(default_factory=list, description="Key decisions made")
    risks: List[str] = Field(default_factory=list, description="Identified risks or blockers")
    action_items: List[ActionItem] = Field(default_factory=list, description="Extracted action items")


class TranscriptSegment(BaseModel):
    speaker: str = Field(..., description="Speaker identifier/name")
    text: str = Field(..., description="Spoken text")
    start: float = Field(0.0, description="Start timestamp in seconds")
    end: float = Field(0.0, description="End timestamp in seconds")


class MeetingRecord(BaseModel):
    id: str = Field(..., description="Unique meeting UUID")
    title: str = Field(..., description="Meeting title")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    transcript_segments: List[TranscriptSegment] = Field(default_factory=list)
    summary: MeetingSummary
    audio_filename: Optional[str] = None


class MeetingCreateResponse(BaseModel):
    message: str
    meeting: MeetingRecord


class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query about past meetings")
    top_k: int = Field(3, description="Number of relevant contexts to return")


class QueryResponse(BaseModel):
    query: str
    answer: str
    relevant_meetings: List[str] = Field(default_factory=list, description="Meeting IDs or titles used")
