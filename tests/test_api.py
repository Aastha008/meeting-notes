import pytest
from fastapi.testclient import TestClient
from src.api import app, get_processor
from src.core import MeetingProcessor


@pytest.fixture

def client(tmp_path):
    storage = str(tmp_path / "test_storage")
    processor = MeetingProcessor(storage_dir=storage)
    
    app.dependency_overrides[get_processor] = lambda: processor
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_transcribe_and_manage_meetings(client):
    # Upload audio file
    files = {"file": ("meeting.wav", b"dummy audio content", "audio/wav")}
    data = {"title": "Q3 Roadmap Discussion"}
    response = client.post("/meetings/transcribe", files=files, data=data)
    
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json["message"] is not None
    meeting = resp_json["meeting"]
    assert meeting["title"] == "Q3 Roadmap Discussion"
    meeting_id = meeting["id"]

    # List meetings
    list_resp = client.get("/meetings")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    # Get specific meeting
    get_resp = client.get(f"/meetings/{meeting_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == meeting_id

    # Query transcripts
    query_payload = {"query": "FastAPI", "top_k": 2}
    query_resp = client.post("/meetings/query", json=query_payload)
    assert query_resp.status_code == 200
    assert "FastAPI" in query_resp.json()["answer"]

    # Delete meeting
    del_resp = client.delete(f"/meetings/{meeting_id}")
    assert del_resp.status_code == 200

    # Confirm deletion
    get_deleted = client.get(f"/meetings/{meeting_id}")
    assert get_deleted.status_code == 404
