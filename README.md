# Oral-Exam-Backend

FastAPI backend for oral exam workflows:
- AI grading (`/analyze-exam`) with Gemini + Claude
- Multi-modal cheating detection (`/detect-cheating`)
- Text-to-speech question generation (`/generate-speech`)
- Google OAuth session bootstrap (`/login`, `/logout`, `/is-logged-in`)
- Supabase classroom/student/assignment endpoints (`/supabase/*`)

---

## Install and Run Locally

### 1) Clone repository

```bash
git clone "https://github.com/GarethFlandro/Oral-Exam-Backend/"
cd Oral-Exam-Backend
```

### 2) Create and activate virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Configure environment variables

Create a `.env` file (or export in your shell) with:

| Variable               | Required                                 | Used For                                   |
|------------------------|------------------------------------------|--------------------------------------------|
| `CLAUDE_API_KEY`       | Yes (for grading)                        | Claude calls in `services/exam_service.py` |
| `GEMINI_API_KEY`       | Yes (for grading/cheating/transcription) | Gemini calls in grading + anti-cheat       |
| `ELEVENLABS_API_KEY`   | Yes (for TTS)                            | `POST /generate-speech`                    |
| `ORAL_EXAM_API_KEY`    | Yes                                      | Static `API_KEY` header validation         |
| `OAUTH_CLIENT_ID`      | Yes (for login)                          | Google token verification in `POST /login` |
| `SUPABASE_URL`         | Yes (for Supabase endpoints)             | Supabase client initialization             |
| `SUPABASE_SERVICE_KEY` | Yes (for Supabase endpoints)             | Supabase service-role access               |

### 5) Start the API

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

API docs will be available at:
- `http://localhost:8080/docs`
- `http://localhost:8080/redoc`

---

## Docker

Build and run:

```bash
docker build -t oral-exam-backend .
docker run --env-file .env -p 8080:8080 oral-exam-backend
```

The container starts with `uvicorn app.main:app` on port `8080` (or `PORT` env var if provided).

---

## Authentication

- Most endpoints require an `API_KEY` request header.
- The expected value is `ORAL_EXAM_API_KEY`.
- `POST /login` does **not** require `API_KEY`; it verifies a Google OAuth token and sets cookies.

Example header:

```http
API_KEY: <ORAL_EXAM_API_KEY>
```

---

## Endpoints

### `POST /analyze-exam`

Accepts an oral exam audio file, runs two-stage grading across Gemini and Claude, and returns a final averaged grade.

**Input (multipart form-data):**

| Field              | Type   | Required | Description                                                    |
|--------------------|--------|----------|----------------------------------------------------------------|
| `audio`            | File   | Yes      | Audio file (`.webm`, `.m4a`, `.mp4`, or other valid MIME type) |
| `class_name`       | string | Yes      | Class name (example: `"AP Calculus"`)                          |
| `question_context` | string | Yes      | JSON string mapping question text to grading notes             |

`question_context` example:

```json
{
  "What is the capital of France?": "Accept only 'Paris'.",
  "Explain Newton's second law.": "Must include F=ma and a practical example."
}
```

**Response:**

```json
{
  "grade": 85,
  "class_name": "AP Calculus",
  "gemini_initial_grade": 88,
  "claude_initial_grade": 82,
  "gemini_review_grade": 86,
  "claude_review_grade": 84
}
```

### `POST /detect-cheating`

Analyzes exam audio + student webcam video + student screen recording for cheating indicators.

**Input (multipart form-data):**

| Field            | Type | Required | Description              |
|------------------|------|----------|--------------------------|
| `exam_audio`     | File | Yes      | Oral exam audio          |
| `student_video`  | File | Yes      | Student camera recording |
| `student_screen` | File | Yes      | Student screen recording |

**Response:**

```json
{
  "is_cheating": false,
  "confidence": "low",
  "summary": "No significant indicators of cheating were detected.",
  "indicators_found": [],
  "recommendation": "clear",
  "notes": "Student appeared focused and engaged throughout."
}
```

### `POST /generate-speech`

Generates MP3 audio for each question and returns a ZIP archive.

**Input (multipart form-data):**

| Field       | Type   | Required | Description                       |
|-------------|--------|----------|-----------------------------------|
| `questions` | string | Yes      | JSON string list of question text |

`questions` example:

```json
[
  "What is the capital of France?",
  "Explain the theory of relativity."
]
```

**Response:**
- `application/zip`
- Files named `question_0.mp3`, `question_1.mp3`, etc.

### `POST /login`

Verifies a Google OAuth token, creates an in-memory session, and sets cookies.

**Input (query parameter):**

| Field         | Type   | Required | Description           |
|---------------|--------|----------|-----------------------|
| `oauth_token` | string | Yes      | Google OAuth ID token |

**Current response behavior:**
- Sets `session_token` cookie.
- Sets `API_KEY` cookie.
- Returns HTTP `200` with an empty body.

### `POST /logout`

Removes a session entry and deletes `session_token` cookie.

**Input:**

| Field           | Type            | Required | Description         |
|-----------------|-----------------|----------|---------------------|
| `session_token` | query parameter | Yes      | Session token value |

**Response:**

```json
{
  "message": "Logged out"
}
```

### `POST /is-logged-in`

Checks if a session token is active.

**Input:**

| Field           | Type            | Required | Description         |
|-----------------|-----------------|----------|---------------------|
| `session_token` | query parameter | Yes      | Session token value |

**Response:**

```json
{
  "logged_in": true,
  "email": "teacher@example.com"
}
```

or

```json
{
  "logged_in": false
}
```

---

## Supabase Endpoints (`/supabase/*`)

All require `API_KEY` header. Models are defined in `app/main.py`.

### Classroom

| Method | Path                               | Input                                   |
|--------|------------------------------------|-----------------------------------------|
| `POST` | `/supabase/create_classroom`       | JSON: `classroom_name`, `teacher_email` |
| `POST` | `/supabase/rename_classroom`       | JSON: `classroom_name`, `new_name`      |
| `POST` | `/supabase/delete_classroom`       | JSON: `classroom_name`                  |
| `GET`  | `/supabase/get_classroom_students` | Query: `classroom_name`                 |
| `GET`  | `/supabase/get_classroom_teachers` | Query: `classroom_name`                 |

### Student

| Method | Path                               | Input                                 |
|--------|------------------------------------|---------------------------------------|
| `POST` | `/supabase/create_student`         | JSON: `student_email`, `student_name` |
| `POST` | `/supabase/rename_student`         | JSON: `student_email`, `new_name`     |
| `POST` | `/supabase/delete_student`         | JSON: `student_email`                 |
| `GET`  | `/supabase/get_student_classrooms` | Query: `student_email`                |

### Student-Classroom Membership

| Method | Path                                      | Input                                   |
|--------|-------------------------------------------|-----------------------------------------|
| `POST` | `/supabase/add_student_to_classroom`      | JSON: `student_email`, `classroom_name` |
| `POST` | `/supabase/remove_student_from_classroom` | JSON: `student_email`, `classroom_name` |

### Teacher Query

| Method | Path                               | Input                  |
|--------|------------------------------------|------------------------|
| `GET`  | `/supabase/get_teacher_classrooms` | Query: `teacher_email` |

### Assignment

| Method | Path                                                       | Input                                                                              |
|--------|------------------------------------------------------------|------------------------------------------------------------------------------------|
| `POST` | `/supabase/create_assignment`                              | JSON: `classroom_name`, `title`, `due_date`, `questions`, optional `assignment_id` |
| `POST` | `/supabase/rename_assignment`                              | JSON: `assignment_id`, `new_title`                                                 |
| `POST` | `/supabase/delete_assignment`                              | JSON: `assignment_id`                                                              |
| `POST` | `/supabase/assign_assignment_to_student`                   | JSON: `assignment_id`, `student_email`                                             |
| `POST` | `/supabase/remove_assignment_from_student`                 | JSON: `assignment_id`, `student_email`                                             |
| `GET`  | `/supabase/get_assigned_students`                          | Query: `assignment_id`                                                             |
| `GET`  | `/supabase/get_student_assignments_by_classroom`           | Query: `student_email`, `classroom_name`                                           |
| `POST` | `/supabase/mark_assignment_as_completed`                   | JSON: `student_email`, `assignment_id`                                             |
| `POST` | `/supabase/upload_assignment_files`                        | JSON: `student_email`, `assignment_id`, `files` (list of bytes), `score`           |
| `GET`  | `/supabase/get_student_completed_assignments_by_classroom` | Query: `student_email`, `assignment_id`                                            |

### Important current behavior notes

- Most `/supabase/*` handlers in `app/main.py` call service functions but do not explicitly `return` data, so current response bodies are typically `null` on success.
- `POST /supabase/assign_assignment_to_student` currently forwards arguments that do not match the service function signature, so it may fail at runtime until aligned.
- `GET /supabase/get_student_completed_assignments_by_classroom` uses query key `assignment_id` even though the service function expects a classroom name.

---

## Testing

Automated API tests live in `tests/test_main.py` and use `pytest` + FastAPI `TestClient`.
The suite mocks Supabase/service integrations, so tests will not change the database or make external API calls.

Run the full suite:

```bash
python -m pytest
```

Run with verbose output and stop on first failure:
```bash
python -m pytest -q tests/test_main.py -x --maxfail=1
```


If tests fail, compare expected request/response schemas with `app/main.py` and `api/routes.py`.

