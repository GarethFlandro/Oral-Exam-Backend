from fastapi.testclient import TestClient
from io import BytesIO
from app.main import app

client = TestClient(app)


def test_analyze_endpoint_returns_100():
    """Test that the /analyze endpoint returns hardcoded 100."""
    # Create mock audio and video files
    audio_file = BytesIO(b"mock audio content")
    video_file = BytesIO(b"mock video content")
    
    response = client.post(
        "/analyze",
        files={
            "audio": ("test_audio.mp3", audio_file, "audio/mpeg"),
            "video": ("test_video.mp4", video_file, "video/mp4"),
        },
    )
    
    assert response.status_code == 200
    assert response.json() == 100


def test_analyze_endpoint_requires_files():
    """Test that the /analyze endpoint requires both audio and video files."""
    response = client.post("/analyze")
    assert response.status_code == 422  # Validation error

def test_analyze_endpoint_with_empty_files():
    """Test that the /analyze endpoint handles empty files."""
    audio_file = BytesIO(b"")
    video_file = BytesIO(b"")
    
    response = client.post(
        "/analyze",
        files={
            "audio": ("empty_audio.mp3", audio_file, "audio/mpeg"),
            "video": ("empty_video.mp4", video_file, "video/mp4"),
        },
    )
    
    assert response.status_code == 200
    assert response.json() == 100