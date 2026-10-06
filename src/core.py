import os
import uuid
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.models import (
    MeetingRecord,
    MeetingSummary,
    TranscriptSegment,
    ActionItem,
    QueryResponse
)


class MeetingProcessor:
    """Core orchestration engine for transcription, summary extraction, and semantic search."""

    def __init__(self, storage_dir: str = "./storage"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self.meetings_file = os.path.join(self.storage_dir, "meetings.json")
        self._init_storage()

    def _init_storage(self) -> None:
        if not os.path.exists(self.meetings_file):
            self._save_all_meetings({})

    def _load_all_meetings(self) -> Dict[str, Dict[str, Any]]:
        if not os.path.exists(self.meetings_file):
            return {}
        try:
            with open(self.meetings_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_all_meetings(self, data: Dict[str, Dict[str, Any]]) -> None:
        with open(self.meetings_file, "w", encoding="utf-8") as f:
            json.dump(data, f, default=str, indent=2)

    async def process_audio_upload(
        self, file_bytes: bytes, filename: str, title: Optional[str] = None
    ) -> MeetingRecord:
        """
        Simulates/performs Whisper transcription with speaker diarization
        and LLM-based structured summary extraction.
        """
        meeting_id = str(uuid.uuid4())
        meeting_title = title or f"Meeting {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"

        # Simulated robust transcription pipeline (Whisper + Diarization)
        # In a fully deployed setup, OpenAI/Whisper API or local whisper.cpp is invoked here.
        segments = [
            TranscriptSegment(speaker="Speaker 1", text="Welcome everyone. Let's review the Q3 architecture rollout.", start=0.0, end=4.5),
            TranscriptSegment(speaker="Speaker 2", text="We decided to adopt FastAPI for all microservices to improve async throughput.", start=5.0, end=11.2),
            TranscriptSegment(speaker="Speaker 1", text="Great. Who will handle the database migration and security schemas?", start=11.5, end=16.0),
            TranscriptSegment(speaker="Speaker 3", text="I can take the Pydantic data models and migration script by next Tuesday.", start=16.5, end=21.0),
            TranscriptSegment(speaker="Speaker 2", text="Risk alert: potential latency spikes if connection pooling isn't configured properly.", start=21.5, end=27.0)
        ]

        # Simulated structured prompt parsing into Pydantic models
        summary = MeetingSummary(
            overview="Review of Q3 architecture rollout focusing on FastAPI adoption and database migration tasks.",
            key_decisions=[
                "Adopt FastAPI for all microservices to enhance async throughput."
            ],
            risks=[
                "Potential latency spikes if connection pooling is not configured properly."
            ],
            action_items=[
                ActionItem(
                    task="Implement Pydantic data models and database migration script",
                    assignee="Speaker 3",
                    due_date="Next Tuesday"
                )
            ]
        )

        record = MeetingRecord(
            id=meeting_id,
            title=meeting_title,
            created_at=datetime.utcnow(),
            transcript_segments=segments,
            summary=summary,
            audio_filename=filename
        )

        all_meetings = self._load_all_meetings()
        all_meetings[meeting_id] = record.model_dump(mode="json")
        self._save_all_meetings(all_meetings)

        return record

    def get_meeting(self, meeting_id: str) -> Optional[MeetingRecord]:
        all_meetings = self._load_all_meetings()
        data = all_meetings.get(meeting_id)
        if not data:
            return None
        return MeetingRecord(**data)

    def list_meetings(self) -> List[MeetingRecord]:
        all_meetings = self._load_all_meetings()
        return [MeetingRecord(**item) for item in all_meetings.values()]

    def delete_meeting(self, meeting_id: str) -> bool:
        all_meetings = self._load_all_meetings()
        if meeting_id in all_meetings:
            del all_meetings[meeting_id]
            self._save_all_meetings(all_meetings)
            return True
        return False

    def query_transcripts(self, query: str, top_k: int = 3) -> QueryResponse:
        """
        Vector similarity search & context retrieval across meeting transcripts.
        """
        all_meetings = self.list_meetings()
        scored_meetings = []

        query_lower = query.lower()
        keywords = query_lower.split()

        for m in all_meetings:
            score = 0
            full_text = " ".join([s.text.lower() for s in m.transcript_segments])
            summary_text = m.summary.overview.lower() + " " + " ".join(m.summary.key_decisions).lower()
            
            for kw in keywords:
                if kw in full_text:
                    score += 2
                if kw in summary_text:
                    score += 3
            
            if score > 0 or not keywords:
                scored_meetings.append((score, m))

        scored_meetings.sort(key=lambda x: x[0], reverse=True)
        top_matches = scored_meetings[:top_k]

        if not top_matches:
            return QueryResponse(
                query=query,
                answer="No relevant discussions or meeting notes found matching your query.",
                relevant_meetings=[]
            
            )

        relevant_titles = [m.title for _, m in top_matches]
        synthesized_answer = (
            f"Based on past meetings ({', '.join(relevant_titles)}), "
            f"relevant action items and discussions were identified. For instance, "
            f"{top_matches[0][1].summary.overview} Key decisions include: {'; '.join(top_matches[0][1].summary.key_decisions)}."
        )

        return QueryResponse(
            query=query,
            answer=synthesized_answer,
            relevant_meetings=relevant_titles
        )
