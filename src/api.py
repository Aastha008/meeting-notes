from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends

from src.models import (
    MeetingRecord,
    MeetingCreateResponse,
    QueryRequest,
    QueryResponse
)
from src.core import MeetingProcessor

app = FastAPI(
    title="Meeting Notes AI Service",
    description="Automated audio transcription, summarization, and vector querying for team meetings.",
    version="1.0.0"
)


def get_processor() -> MeetingProcessor:
    return MeetingProcessor()


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "service": "meeting-notes-ai"}


@app.post("/meetings/transcribe", response_model=MeetingCreateResponse, tags=["Meetings"])
async def transcribe_meeting(
    file: UploadFile = File(..., description="Audio recording file (mp3, wav, m4a)"),
    title: Optional[str] = Form(None, description="Custom meeting title"),
    processor: MeetingProcessor = Depends(get_processor)
):
    """
    Ingests an audio recording, executes Whisper transcription with speaker diarization,
    extracts structured decisions, risks, and action items via LLM prompts.
    """
    try:
        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(status_code=400, detail="Uploaded audio file is empty.")

        record = await processor.process_audio_upload(
            file_bytes=file_bytes,
            filename=file.filename or "audio.wav",
            title=title
        )
        return MeetingCreateResponse(
            message="Meeting successfully transcribed and summarized.",
            meeting=record
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/meetings", response_model=List[MeetingRecord], tags=["Meetings"])
async def list_meetings(processor: MeetingProcessor = Depends(get_processor)):
    """Retrieve all archived meeting notes."""
    return processor.list_meetings()


@app.get("/meetings/{meeting_id}", response_model=MeetingRecord, tags=["Meetings"])
async def get_meeting(meeting_id: str, processor: MeetingProcessor = Depends(get_processor)):
    """Retrieve a specific meeting record by ID."""
    record = processor.get_meeting(meeting_id)
    if not record:
        raise HTTPException(status_code=404, detail="Meeting not found.")
    return record


@app.delete("/meetings/{meeting_id}", tags=["Meetings"])
async def delete_meeting(meeting_id: str, processor: MeetingProcessor = Depends(get_processor)):
    """Delete a meeting record from archives."""
    success = processor.delete_meeting(meeting_id)
    if not success:
        raise HTTPException(status_code=404, detail="Meeting not found.")
    return {"status": "success", "message": f"Meeting {meeting_id} deleted."}


@app.post("/meetings/query", response_model=QueryResponse, tags=["Query & Search"])
async def query_meetings(
    payload: QueryRequest,
    processor: MeetingProcessor = Depends(get_processor)
):
    """
    Query past meeting transcripts and summaries using semantic vector search.
    """
    try:
        response = processor.query_transcripts(query=payload.query, top_k=payload.top_k)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
