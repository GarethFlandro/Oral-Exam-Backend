import io
import zipfile
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient

import api.routes as routes_module
import app.main as main_module


@pytest.fixture
def api_key(monkeypatch):
    # Keep API key checks deterministic and isolated from host env.
    monkeypatch.setenv("ORAL_EXAM_API_KEY", "test-api-key")
    monkeypatch.setattr(routes_module, "ORAL_EXAM_API_KEY", "test-api-key")
    return "test-api-key"


@pytest.fixture
def auth_headers(api_key):
    return {"API_KEY": api_key}


@pytest.fixture
def client():
    main_module.app.dependency_overrides = {}
    routes_module.logged_in_users.clear()
    with TestClient(main_module.app, raise_server_exceptions=False) as test_client:
        yield test_client
    main_module.app.dependency_overrides = {}
    routes_module.logged_in_users.clear()


@pytest.fixture
def mock_supabase_calls(monkeypatch):
    function_names = [
        "p_create_classroom",
        "p_rename_classroom",
        "p_delete_classroom",
        "p_get_classroom_students",
        "p_get_classroom_teachers",
        "p_create_student",
        "p_rename_student",
        "p_delete_student",
        "p_get_student_classrooms",
        "p_add_student_to_classroom",
        "p_remove_student_from_classroom",
        "p_get_teacher_classrooms",
        "p_create_assignment",
        "p_rename_assignment",
        "p_delete_assignment",
        "p_assign_assignment_to_student",
        "p_remove_assignment_from_student",
        "p_get_assigned_students",
        "p_get_student_assignments_by_classroom",
        "p_mark_assignment_as_completed",
        "p_upload_assignment_submission",
        "p_get_student_completed_assignments_by_classroom",
    ]

    mocks = {}
    for function_name in function_names:
        mocked_function = Mock(name=function_name)
        monkeypatch.setattr(main_module, function_name, mocked_function)
        mocks[function_name] = mocked_function
    return mocks


@pytest.mark.parametrize(
    "method,path,json_body,query,mock_name,expected_args",
    [
        (
            "post",
            "/supabase/create_classroom",
            {"classroom_name": "math-1", "teacher_email": "teacher@example.com"},
            None,
            "p_create_classroom",
            ("math-1", "teacher@example.com"),
        ),
        (
            "post",
            "/supabase/rename_classroom",
            {"classroom_name": "math-1", "new_name": "math-2"},
            None,
            "p_rename_classroom",
            ("math-1", "math-2"),
        ),
        (
            "post",
            "/supabase/delete_classroom",
            {"classroom_name": "math-1"},
            None,
            "p_delete_classroom",
            ("math-1",),
        ),
        (
            "get",
            "/supabase/get_classroom_students",
            None,
            {"classroom_name": "math-1"},
            "p_get_classroom_students",
            ("math-1",),
        ),
        (
            "get",
            "/supabase/get_classroom_teachers",
            None,
            {"classroom_name": "math-1"},
            "p_get_classroom_teachers",
            ("math-1",),
        ),
        (
            "post",
            "/supabase/create_student",
            {"student_email": "student@example.com", "student_name": "Alex"},
            None,
            "p_create_student",
            ("student@example.com", "Alex"),
        ),
        (
            "post",
            "/supabase/rename_student",
            {"student_email": "student@example.com", "new_name": "Jordan"},
            None,
            "p_rename_student",
            ("student@example.com", "Jordan"),
        ),
        (
            "post",
            "/supabase/delete_student",
            {"student_email": "student@example.com"},
            None,
            "p_delete_student",
            ("student@example.com",),
        ),
        (
            "get",
            "/supabase/get_student_classrooms",
            None,
            {"student_email": "student@example.com"},
            "p_get_student_classrooms",
            ("student@example.com",),
        ),
        (
            "post",
            "/supabase/add_student_to_classroom",
            {"student_email": "student@example.com", "classroom_name": "math-1"},
            None,
            "p_add_student_to_classroom",
            ("student@example.com", "math-1"),
        ),
        (
            "post",
            "/supabase/remove_student_from_classroom",
            {"student_email": "student@example.com", "classroom_name": "math-1"},
            None,
            "p_remove_student_from_classroom",
            ("student@example.com", "math-1"),
        ),
        (
            "get",
            "/supabase/get_teacher_classrooms",
            None,
            {"teacher_email": "teacher@example.com"},
            "p_get_teacher_classrooms",
            ("teacher@example.com",),
        ),
        (
            "post",
            "/supabase/rename_assignment",
            {"assignment_id": "a-1", "new_title": "Updated"},
            None,
            "p_rename_assignment",
            ("a-1", "Updated"),
        ),
        (
            "post",
            "/supabase/delete_assignment",
            {"assignment_id": "a-1"},
            None,
            "p_delete_assignment",
            ("a-1",),
        ),
        (
            "post",
            "/supabase/assign_assignment_to_student",
            {
                "classroom_name": "math-1",
                "assignment_id": "a-1",
                "student_email": "student@example.com",
            },
            None,
            "p_assign_assignment_to_student",
            ("math-1", "a-1", "student@example.com"),
        ),
        (
            "post",
            "/supabase/remove_assignment_from_student",
            {"assignment_id": "a-1", "student_email": "student@example.com"},
            None,
            "p_remove_assignment_from_student",
            ("a-1", "student@example.com"),
        ),
        (
            "get",
            "/supabase/get_assigned_students",
            None,
            {"assignment_id": "a-1"},
            "p_get_assigned_students",
            ("a-1",),
        ),
        (
            "get",
            "/supabase/get_student_assignments_by_classroom",
            None,
            {"student_email": "student@example.com", "classroom_name": "math-1"},
            "p_get_student_assignments_by_classroom",
            ("student@example.com", "math-1"),
        ),
        (
            "post",
            "/supabase/mark_assignment_as_completed",
            {"student_email": "student@example.com", "assignment_id": "a-1"},
            None,
            "p_mark_assignment_as_completed",
            ("student@example.com", "a-1"),
        ),
        (
            "post",
            "/supabase/upload_assignment_files",
            {
                "student_email": "student@example.com",
                "assignment_id": "a-1",
                "files": ["YXNk"],
                "score": 88,
            },
            None,
            "p_upload_assignment_submission",
            ("student@example.com", "a-1", [b"YXNk"], 88),
        ),
        (
            "get",
            "/supabase/get_student_completed_assignments_by_classroom",
            None,
            {"student_email": "student@example.com", "assignment_id": "a-1"},
            "p_get_student_completed_assignments_by_classroom",
            ("student@example.com", "a-1"),
        ),
    ],
)
def test_should_call_expected_supabase_function_for_each_endpoint(
    client,
    auth_headers,
    mock_supabase_calls,
    method,
    path,
    json_body,
    query,
    mock_name,
    expected_args,
):
    # Arrange
    request = getattr(client, method)
    request_kwargs = {"headers": auth_headers}
    if json_body is not None:
        request_kwargs["json"] = json_body
    if query is not None:
        request_kwargs["params"] = query

    # Act
    response = request(path, **request_kwargs)

    # Assert
    assert response.status_code == 200
    assert response.json() is None
    mock_supabase_calls[mock_name].assert_called_once_with(*expected_args)


def test_should_generate_assignment_id_when_missing(client, auth_headers, mock_supabase_calls, monkeypatch):
    # Arrange
    monkeypatch.setattr(main_module.uuid, "uuid4", Mock(return_value="generated-assignment-id"))

    # Act
    response = client.post(
        "/supabase/create_assignment",
        headers=auth_headers,
        json={
            "classroom_name": "math-1",
            "title": "Final Oral",
            "due_date": "2026-03-27",
            "questions": {"q1": "Explain vectors"},
        },
    )

    # Assert
    assert response.status_code == 200
    assert response.json() is None
    mock_supabase_calls["p_create_assignment"].assert_called_once_with(
        "generated-assignment-id",
        "math-1",
        "Final Oral",
        "2026-03-27",
        {"q1": "Explain vectors"},
    )


def test_should_use_provided_assignment_id_when_present(client, auth_headers, mock_supabase_calls):
    # Arrange / Act
    response = client.post(
        "/supabase/create_assignment",
        headers=auth_headers,
        json={
            "assignment_id": "provided-id",
            "classroom_name": "math-1",
            "title": "Final Oral",
            "due_date": "2026-03-27",
            "questions": {"q1": "Explain vectors"},
        },
    )

    # Assert
    assert response.status_code == 200
    mock_supabase_calls["p_create_assignment"].assert_called_once_with(
        "provided-id",
        "math-1",
        "Final Oral",
        "2026-03-27",
        {"q1": "Explain vectors"},
    )


def test_should_return_403_when_api_key_is_missing_for_protected_endpoints(client):
    # Arrange / Act
    response = client.post(
        "/supabase/create_classroom",
        json={"classroom_name": "math-1", "teacher_email": "teacher@example.com"},
    )

    # Assert
    assert response.status_code in (401, 403)


@pytest.mark.parametrize(
    "method,path,request_kwargs",
    [
        ("post", "/supabase/create_classroom", {"json": {"classroom_name": "math-1", "teacher_email": "teacher@example.com"}}),
        ("post", "/supabase/rename_classroom", {"json": {"classroom_name": "math-1", "new_name": "math-2"}}),
        ("post", "/supabase/delete_classroom", {"json": {"classroom_name": "math-1"}}),
        ("get", "/supabase/get_classroom_students", {"params": {"classroom_name": "math-1"}}),
        ("get", "/supabase/get_classroom_teachers", {"params": {"classroom_name": "math-1"}}),
        ("post", "/supabase/create_student", {"json": {"student_email": "student@example.com", "student_name": "Alex"}}),
        ("post", "/supabase/rename_student", {"json": {"student_email": "student@example.com", "new_name": "Jordan"}}),
        ("post", "/supabase/delete_student", {"json": {"student_email": "student@example.com"}}),
        ("get", "/supabase/get_student_classrooms", {"params": {"student_email": "student@example.com"}}),
        ("post", "/supabase/add_student_to_classroom", {"json": {"student_email": "student@example.com", "classroom_name": "math-1"}}),
        ("post", "/supabase/remove_student_from_classroom", {"json": {"student_email": "student@example.com", "classroom_name": "math-1"}}),
        ("get", "/supabase/get_teacher_classrooms", {"params": {"teacher_email": "teacher@example.com"}}),
        ("post", "/supabase/create_assignment", {"json": {"classroom_name": "math-1", "title": "Final", "due_date": "2026-03-27", "questions": {"q1": "Explain vectors"}}}),
        ("post", "/supabase/rename_assignment", {"json": {"assignment_id": "a-1", "new_title": "Updated"}}),
        ("post", "/supabase/delete_assignment", {"json": {"assignment_id": "a-1"}}),
        ("post", "/supabase/assign_assignment_to_student", {"json": {"classroom_name": "math-1", "assignment_id": "a-1", "student_email": "student@example.com"}}),
        ("post", "/supabase/remove_assignment_from_student", {"json": {"assignment_id": "a-1", "student_email": "student@example.com"}}),
        ("get", "/supabase/get_assigned_students", {"params": {"assignment_id": "a-1"}}),
        ("get", "/supabase/get_student_assignments_by_classroom", {"params": {"student_email": "student@example.com", "classroom_name": "math-1"}}),
        ("post", "/supabase/mark_assignment_as_completed", {"json": {"student_email": "student@example.com", "assignment_id": "a-1"}}),
        ("post", "/supabase/upload_assignment_files", {"json": {"student_email": "student@example.com", "assignment_id": "a-1", "files": ["YXNk"], "score": 88}}),
        ("get", "/supabase/get_student_completed_assignments_by_classroom", {"params": {"student_email": "student@example.com", "assignment_id": "a-1"}}),
        ("post", "/analyze-exam", {"data": {"class_name": "Physics", "question_context": "{}"}, "files": {"audio": ("exam.webm", b"audio", "audio/webm")}}),
        ("post", "/detect-cheating", {"files": {"exam_audio": ("exam.webm", b"audio", "audio/webm"), "student_video": ("video.webm", b"video", "video/webm"), "student_screen": ("screen.webm", b"screen", "video/webm")}}),
        ("post", "/generate-speech", {"params": {"questions": "[]"}}),
        ("post", "/logout", {"params": {"session_token": "session-1"}}),
        ("post", "/is-logged-in", {"params": {"session_token": "session-1"}}),
    ],
)
def test_should_require_api_key_for_all_protected_endpoints(client, method, path, request_kwargs):
    # Arrange
    request = getattr(client, method)

    # Act
    response = request(path, **request_kwargs)

    # Assert
    assert response.status_code in (401, 403)


def test_should_return_403_when_api_key_is_wrong_for_get_api_key_dependency(client, api_key):
    # Arrange
    wrong_headers = {"API_KEY": f"{api_key}-wrong"}

    # Act
    response = client.post(
        "/supabase/create_student",
        headers=wrong_headers,
        json={"student_email": "student@example.com", "student_name": "Alex"},
    )

    # Assert
    assert response.status_code == 403
    assert response.json()["detail"] == "Could not validate API key"


def test_should_accept_any_non_empty_api_key_for_get_teacher_classrooms_header_only_dependency(
    client,
    mock_supabase_calls,
):
    # Arrange
    headers = {"API_KEY": "not-validated-here"}

    # Act
    response = client.get(
        "/supabase/get_teacher_classrooms",
        headers=headers,
        params={"teacher_email": "teacher@example.com"},
    )

    # Assert
    assert response.status_code == 200
    mock_supabase_calls["p_get_teacher_classrooms"].assert_called_once_with("teacher@example.com")


def test_should_return_422_for_invalid_supabase_payload(client, auth_headers):
    # Arrange / Act
    response = client.post(
        "/supabase/create_classroom",
        headers=auth_headers,
        json={"classroom_name": "math-1"},
    )

    # Assert
    assert response.status_code == 422


def test_should_return_404_for_unknown_route(client):
    # Arrange / Act
    response = client.get("/does-not-exist")

    # Assert
    assert response.status_code == 404


def test_should_analyze_exam_successfully(client, auth_headers, monkeypatch):
    # Arrange
    process_exam_mock = AsyncMock(return_value=(91, 88, 90, 92, 94))
    monkeypatch.setattr(routes_module, "process_exam", process_exam_mock)

    # Act
    response = client.post(
        "/analyze-exam",
        headers=auth_headers,
        params={
            "class_name": "Physics",
            "question_context": '{"Q1": "Expect F=ma"}',
        },
        files={"audio": ("exam.webm", b"audio-bytes", "audio/webm")},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "grade": 91,
        "class_name": "Physics",
        "gemini_initial_grade": 88,
        "claude_initial_grade": 90,
        "gemini_review_grade": 92,
        "claude_review_grade": 94,
    }
    process_exam_mock.assert_awaited_once_with(
        b"audio-bytes",
        "Physics",
        "audio/webm",
        {"Q1": "Expect F=ma"},
    )


def test_should_return_422_when_analyze_exam_audio_is_missing(client, auth_headers):
    # Arrange / Act
    response = client.post(
        "/analyze-exam",
        headers=auth_headers,
        params={"class_name": "Physics", "question_context": "{}"},
    )

    # Assert
    assert response.status_code == 422


def test_should_return_500_when_analyze_exam_question_context_is_invalid_json(client, auth_headers):
    # Arrange / Act
    response = client.post(
        "/analyze-exam",
        headers=auth_headers,
        params={"class_name": "Physics", "question_context": "not-json"},
        files={"audio": ("exam.webm", b"audio-bytes", "audio/webm")},
    )

    # Assert
    assert response.status_code == 500


def test_should_detect_cheating_successfully(client, auth_headers, monkeypatch):
    # Arrange
    detect_cheating_mock = AsyncMock(
        return_value=SimpleNamespace(
            is_cheating=False,
            confidence="low",
            summary="No suspicious signals.",
            indicators_found=[],
            recommendation="clear",
            notes="Clean attempt.",
        )
    )
    monkeypatch.setattr(routes_module, "detect_cheating", detect_cheating_mock)

    # Act
    response = client.post(
        "/detect-cheating",
        headers=auth_headers,
        files={
            "exam_audio": ("exam.webm", b"audio", "audio/webm"),
            "student_video": ("video.webm", b"video", "video/webm"),
            "student_screen": ("screen.webm", b"screen", "video/webm"),
        },
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "is_cheating": False,
        "confidence": "low",
        "summary": "No suspicious signals.",
        "indicators_found": [],
        "recommendation": "clear",
        "notes": "Clean attempt.",
    }
    detect_cheating_mock.assert_awaited_once_with(
        exam_audio=b"audio",
        student_video=b"video",
        student_screen=b"screen",
        exam_audio_mime_type="audio/webm",
        student_video_mime_type="video/webm",
        student_screen_mime_type="video/webm",
    )


def test_should_return_422_when_detect_cheating_file_is_missing(client, auth_headers):
    # Arrange / Act
    response = client.post(
        "/detect-cheating",
        headers=auth_headers,
        files={
            "exam_audio": ("exam.webm", b"audio", "audio/webm"),
            "student_video": ("video.webm", b"video", "video/webm"),
        },
    )

    # Assert
    assert response.status_code == 422


def test_should_generate_zip_of_speech_files(client, auth_headers, monkeypatch):
    # Arrange
    generate_speech_mock = Mock(side_effect=[b"audio-q1", b"audio-q2"])
    monkeypatch.setattr(routes_module, "generate_speech", generate_speech_mock)

    # Act
    response = client.post(
        "/generate-speech",
        headers=auth_headers,
        params={"questions": '["What is gravity?", "Define momentum"]'},
    )

    # Assert
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"

    archive = zipfile.ZipFile(io.BytesIO(response.content), "r")
    assert archive.namelist() == ["question_0.mp3", "question_1.mp3"]
    assert archive.read("question_0.mp3") == b"audio-q1"
    assert archive.read("question_1.mp3") == b"audio-q2"


def test_should_return_500_when_generate_speech_questions_is_invalid_json(client, auth_headers):
    # Arrange / Act
    response = client.post(
        "/generate-speech",
        headers=auth_headers,
        params={"questions": "not-json"},
    )

    # Assert
    assert response.status_code == 500


def test_should_login_and_set_session_and_api_key_cookies(client, monkeypatch, api_key):
    # Arrange
    verify_token_mock = Mock(return_value={"email": "teacher@example.com"})
    monkeypatch.setattr(routes_module.id_token, "verify_oauth2_token", verify_token_mock)

    # Act
    response = client.post("/login", params={"oauth_token": "valid-token"})

    # Assert
    assert response.status_code == 200
    assert response.json() is None
    assert "session_token=" in response.headers["set-cookie"]
    assert f"API_KEY={api_key}" in response.headers["set-cookie"]
    assert len(routes_module.logged_in_users) == 1
    assert "teacher@example.com" in routes_module.logged_in_users.values()


def test_should_return_401_when_login_token_is_invalid(client, monkeypatch):
    # Arrange
    verify_token_mock = Mock(side_effect=Exception("bad token"))
    monkeypatch.setattr(routes_module.id_token, "verify_oauth2_token", verify_token_mock)

    # Act
    response = client.post("/login", params={"oauth_token": "invalid-token"})

    # Assert
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid OAuth token"}


def test_should_report_user_as_logged_in_when_session_exists(client, auth_headers):
    # Arrange
    routes_module.logged_in_users["session-1"] = "student@example.com"

    # Act
    response = client.post(
        "/is-logged-in",
        headers=auth_headers,
        params={"session_token": "session-1"},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"logged_in": True, "email": "student@example.com"}


def test_should_report_user_as_logged_out_when_session_missing(client, auth_headers):
    # Arrange / Act
    response = client.post(
        "/is-logged-in",
        headers=auth_headers,
        params={"session_token": "missing-session"},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"logged_in": False}


def test_should_logout_user_and_remove_session(client, auth_headers):
    # Arrange
    routes_module.logged_in_users["session-1"] = "student@example.com"

    # Act
    response = client.post(
        "/logout",
        headers=auth_headers,
        params={"session_token": "session-1"},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "Logged out"}
    assert "session-1" not in routes_module.logged_in_users


def test_should_return_403_when_login_protected_route_missing_api_key(client):
    # Arrange / Act
    response = client.post("/is-logged-in", params={"session_token": "session-1"})

    # Assert
    assert response.status_code in (401, 403)


def test_should_not_call_supabase_when_api_key_is_invalid(client, mock_supabase_calls, api_key):
    # Arrange
    wrong_headers = {"API_KEY": f"{api_key}-wrong"}

    # Act
    response = client.post(
        "/supabase/create_student",
        headers=wrong_headers,
        json={"student_email": "student@example.com", "student_name": "Alex"},
    )

    # Assert
    assert response.status_code == 403
    mock_supabase_calls["p_create_student"].assert_not_called()


def test_should_return_403_for_empty_api_key_header(client):
    # Arrange / Act
    response = client.post(
        "/supabase/create_student",
        headers={"API_KEY": ""},
        json={"student_email": "student@example.com", "student_name": "Alex"},
    )

    # Assert
    assert response.status_code in (401, 403)


@pytest.mark.parametrize(
    "method,path,request_kwargs",
    [
        ("get", "/supabase/get_classroom_students", {}),
        ("get", "/supabase/get_student_classrooms", {}),
        ("post", "/logout", {}),
        ("post", "/is-logged-in", {}),
    ],
)
def test_should_return_422_when_required_query_params_are_missing(client, auth_headers, method, path, request_kwargs):
    # Arrange
    request = getattr(client, method)

    # Act
    response = request(path, headers=auth_headers, **request_kwargs)

    # Assert
    assert response.status_code == 422


def test_should_return_422_when_create_assignment_questions_is_not_a_dict(client, auth_headers):
    # Arrange / Act
    response = client.post(
        "/supabase/create_assignment",
        headers=auth_headers,
        json={
            "classroom_name": "math-1",
            "title": "Final Oral",
            "due_date": "2026-03-27",
            "questions": ["not", "a", "dict"],
        },
    )

    # Assert
    assert response.status_code == 422


def test_should_return_422_when_upload_assignment_files_score_has_wrong_type(client, auth_headers):
    # Arrange / Act
    response = client.post(
        "/supabase/upload_assignment_files",
        headers=auth_headers,
        json={
            "student_email": "student@example.com",
            "assignment_id": "a-1",
            "files": ["YXNk"],
            "score": "eighty-eight",
        },
    )

    # Assert
    assert response.status_code == 422


def test_should_return_500_when_process_exam_raises(client, auth_headers, monkeypatch):
    # Arrange
    process_exam_mock = AsyncMock(side_effect=RuntimeError("service unavailable"))
    monkeypatch.setattr(routes_module, "process_exam", process_exam_mock)

    # Act
    response = client.post(
        "/analyze-exam",
        headers=auth_headers,
        params={"class_name": "Physics", "question_context": "{}"},
        files={"audio": ("exam.webm", b"audio-bytes", "audio/webm")},
    )

    # Assert
    assert response.status_code == 500


def test_should_return_500_when_detect_cheating_raises(client, auth_headers, monkeypatch):
    # Arrange
    detect_cheating_mock = AsyncMock(side_effect=RuntimeError("model crash"))
    monkeypatch.setattr(routes_module, "detect_cheating", detect_cheating_mock)

    # Act
    response = client.post(
        "/detect-cheating",
        headers=auth_headers,
        files={
            "exam_audio": ("exam.webm", b"audio", "audio/webm"),
            "student_video": ("video.webm", b"video", "video/webm"),
            "student_screen": ("screen.webm", b"screen", "video/webm"),
        },
    )

    # Assert
    assert response.status_code == 500


def test_should_return_500_when_generate_speech_raises(client, auth_headers, monkeypatch):
    # Arrange
    generate_speech_mock = Mock(side_effect=RuntimeError("tts backend down"))
    monkeypatch.setattr(routes_module, "generate_speech", generate_speech_mock)

    # Act
    response = client.post(
        "/generate-speech",
        headers=auth_headers,
        params={"questions": '["What is gravity?"]'},
    )

    # Assert
    assert response.status_code == 500


def test_should_return_500_when_supabase_call_raises(client, auth_headers, mock_supabase_calls):
    # Arrange
    mock_supabase_calls["p_create_classroom"].side_effect = RuntimeError("db unavailable")

    # Act
    response = client.post(
        "/supabase/create_classroom",
        headers=auth_headers,
        json={"classroom_name": "math-1", "teacher_email": "teacher@example.com"},
    )

    # Assert
    assert response.status_code == 500
    mock_supabase_calls["p_create_classroom"].assert_called_once_with("math-1", "teacher@example.com")


def test_should_return_expected_key_set_for_analyze_exam_response(client, auth_headers, monkeypatch):
    # Arrange
    monkeypatch.setattr(routes_module, "process_exam", AsyncMock(return_value=(80, 78, 82, 79, 81)))

    # Act
    response = client.post(
        "/analyze-exam",
        headers=auth_headers,
        params={"class_name": "Physics", "question_context": "{}"},
        files={"audio": ("exam.webm", b"audio", "audio/webm")},
    )

    # Assert
    assert response.status_code == 200
    assert set(response.json().keys()) == {
        "grade",
        "class_name",
        "gemini_initial_grade",
        "claude_initial_grade",
        "gemini_review_grade",
        "claude_review_grade",
    }


def test_should_return_expected_key_set_for_detect_cheating_response(client, auth_headers, monkeypatch):
    # Arrange
    monkeypatch.setattr(
        routes_module,
        "detect_cheating",
        AsyncMock(
            return_value=SimpleNamespace(
                is_cheating=True,
                confidence="high",
                summary="Suspicious behavior.",
                indicators_found=["offscreen lookups"],
                recommendation="review",
                notes="Needs manual review.",
            )
        ),
    )

    # Act
    response = client.post(
        "/detect-cheating",
        headers=auth_headers,
        files={
            "exam_audio": ("exam.webm", b"audio", "audio/webm"),
            "student_video": ("video.webm", b"video", "video/webm"),
            "student_screen": ("screen.webm", b"screen", "video/webm"),
        },
    )

    # Assert
    assert response.status_code == 200
    assert set(response.json().keys()) == {
        "is_cheating",
        "confidence",
        "summary",
        "indicators_found",
        "recommendation",
        "notes",
    }


def test_should_set_content_disposition_for_generate_speech_zip(client, auth_headers, monkeypatch):
    # Arrange
    monkeypatch.setattr(routes_module, "generate_speech", Mock(return_value=b"audio-bytes"))

    # Act
    response = client.post(
        "/generate-speech",
        headers=auth_headers,
        params={"questions": '["What is gravity?"]'},
    )

    # Assert
    assert response.status_code == 200
    assert response.headers["content-disposition"] == "attachment; filename=questions_audio.zip"


def test_should_return_empty_zip_when_generate_speech_receives_empty_question_list(client, auth_headers, monkeypatch):
    # Arrange
    generate_speech_mock = Mock()
    monkeypatch.setattr(routes_module, "generate_speech", generate_speech_mock)

    # Act
    response = client.post(
        "/generate-speech",
        headers=auth_headers,
        params={"questions": "[]"},
    )

    # Assert
    assert response.status_code == 200
    archive = zipfile.ZipFile(io.BytesIO(response.content), "r")
    assert archive.namelist() == []
    generate_speech_mock.assert_not_called()


def test_should_fallback_to_default_analyze_exam_mime_type_when_content_type_is_empty(client, auth_headers, monkeypatch):
    # Arrange
    process_exam_mock = AsyncMock(return_value=(75, 74, 76, 75, 75))
    monkeypatch.setattr(routes_module, "process_exam", process_exam_mock)

    # Act
    response = client.post(
        "/analyze-exam",
        headers=auth_headers,
        params={"class_name": "Physics", "question_context": "{}"},
        files={"audio": ("exam.webm", b"audio", "")},
    )

    # Assert
    assert response.status_code == 200
    process_exam_mock.assert_awaited_once_with(b"audio", "Physics", "audio/webm", {})


def test_should_fallback_to_default_detect_cheating_mime_types_when_content_type_is_empty(client, auth_headers, monkeypatch):
    # Arrange
    detect_cheating_mock = AsyncMock(
        return_value=SimpleNamespace(
            is_cheating=False,
            confidence="low",
            summary="No suspicious signals.",
            indicators_found=[],
            recommendation="clear",
            notes="Clean attempt.",
        )
    )
    monkeypatch.setattr(routes_module, "detect_cheating", detect_cheating_mock)

    # Act
    response = client.post(
        "/detect-cheating",
        headers=auth_headers,
        files={
            "exam_audio": ("exam.webm", b"audio", ""),
            "student_video": ("video.webm", b"video", ""),
            "student_screen": ("screen.webm", b"screen", ""),
        },
    )

    # Assert
    assert response.status_code == 200
    detect_cheating_mock.assert_awaited_once_with(
        exam_audio=b"audio",
        student_video=b"video",
        student_screen=b"screen",
        exam_audio_mime_type="audio/webm",
        student_video_mime_type="video/webm",
        student_screen_mime_type="video/webm",
    )


def test_should_not_create_session_when_login_token_is_invalid(client, monkeypatch):
    # Arrange
    monkeypatch.setattr(routes_module.id_token, "verify_oauth2_token", Mock(side_effect=Exception("bad token")))

    # Act
    response = client.post("/login", params={"oauth_token": "invalid-token"})

    # Assert
    assert response.status_code == 401
    assert routes_module.logged_in_users == {}


def test_should_allow_logout_for_nonexistent_session_and_keep_state_empty(client, auth_headers):
    # Arrange / Act
    response = client.post(
        "/logout",
        headers=auth_headers,
        params={"session_token": "does-not-exist"},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "Logged out"}
    assert routes_module.logged_in_users == {}

