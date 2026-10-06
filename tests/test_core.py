import os
import pytest
from src.core import MeetingProcessor
from src.models import QueryRequest


@pytest.fixture
def temp_processor(tmp_path):
    storage = str(tmp_path / "storage")
    return MeetingProcessor(storage_dir=storage)


@pytest.mark.asyncio
async def test_audio_processing_and_storage(temp_processor):
    fake_audio = b"RIFF....WAVEfmt ....data...."
    filename = "test_meeting.wav"
    title = "Sprint Planning"

    record = await temp_processor.process_audio_upload(
        file_bytes=fake_audio,
        filename=filename,
        title=title
    )

    assert record.id is not None
    assert record.title == "Sprint Planning"
    assert len(record.transcript_segments) > 0
    assert record.summary.overview is not None
    assert len(record.summary.action_items) > 0

    # Test retrieval
    fetched = temp_processor.get_meeting(record.id)
    assert fetched is not None
    assert fetched.id == record.id

    # Test listing
    all_recs = temp_processor.list_meetings()
    assert len(all_recs) == 1

    # Test deletion
    deleted = temp_processor.delete_meeting(record.id)
    assert deleted is True
    assert len(temp_processor.list_meetings()) == 0


@pytest.mark.asyncio
async def test_semantic_querying(temp_processor):
    fake_audio = b"audio_bytes"
    await temp_processor.process_audio_upload(
        file_bytes=fake_audio,
        filename="arch.wav",
        title="Architecture Review"
    )

    query_res = temp_processor.query_transcripts(query="FastAPI microservices")
    assert query_res is not None
    assert "Architecture Review" in query_res.relevant_meetings
    assert "FastAPI" in query_res.answer
