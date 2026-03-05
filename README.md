# Oral-Exam-Backend

## How to Set Up

1) Download repository
2) Choose a hosting platform (Heroku, AWS, etc.)
3) Set up environment variables:
   - `CLAUDE_API_KEY`
   - `GEMINI_API_KEY`
   - `ORAL_EXAM_API_KEY` (static API key for this server)
4) Deploy the application

---

## Endpoints

All endpoints require the `API_KEY` header for authentication

---

### `POST /analyze-exam`

Accepts an audio file of an oral exam, processes it through Gemini and Claude, and returns the calculated grade.

**Input (multipart form-data):**

| Field              | Type   | Required | Description                                                                                   |
|--------------------|--------|----------|-----------------------------------------------------------------------------------------------|
| `audio`            | File   | Yes      | The audio file from the oral exam (supports `.webm` `.m4a` `.mp4`)                            |
| `class_name`       | string | Yes      | The name of the class being taught (e.g. `"AP Calculus"` `"Intro to Psychology"`)             |
| `question_context` | string | Yes      | A JSON string mapping each exam question to teacher-provided grading notes for that question. |

`question_context` is a JSON object where each key is a question string and each value is the teacher's grading notes for that question:

```json
{
    "What is the capital of France?": "Accept only 'Paris'. Do not accept regions.",
    "Explain Newton's second law.": "Student should mention F=ma and give a real-world example."
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

| Field                  | Type   | Description                                |
|------------------------|--------|--------------------------------------------|
| `grade`                | int    | The final averaged grade (0-100)           |
| `class_name`           | string | The class that was evaluated               |
| `gemini_initial_grade` | int    | Gemini's first-stage grade                 |
| `claude_initial_grade` | int    | Claude's first-stage grade                 |
| `gemini_review_grade`  | int    | Gemini's grade after peer review of Claude |
| `claude_review_grade`  | int    | Claude's grade after peer review of Gemini |

---

### `POST /detect-cheating`

Analyzes audio, video, and screen recording from an oral exam to detect potential cheating.

**Input (multipart form-data):**

| Field            | Type | Required | Description                                        |
|------------------|------|----------|----------------------------------------------------|
| `exam_audio`     | File | Yes      | The audio file from the oral exam                  |
| `student_video`  | File | Yes      | The video recording of the student during the exam |
| `student_screen` | File | Yes      | The screen recording of the student's computer     |

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

| Field              | Type   | Description                                             |
|--------------------|--------|---------------------------------------------------------|
| `is_cheating`      | bool   | Whether cheating was detected                           |
| `confidence`       | string | Confidence level: `"low"` `"medium"` or `"high"`        |
| `summary`          | string | Brief summary of the analysis                           |
| `indicators_found` | list   | List of specific cheating indicators observed           |
| `recommendation`   | string | Action recommendation: `"clear"` `"review"` or `"flag"` |
| `notes`            | string | Additional context or observations                      |

---

### `POST /generate-speech`

Generates speech audio files from a list of question strings using text-to-speech.

**Input (multipart form-data):**

| Field       | Type   | Required | Description                                          |
|-------------|--------|----------|------------------------------------------------------|
| `questions` | string | Yes      | A JSON string containing a list of question strings. |

`questions` format:

```json
[
    "What is the capital of France?",
    "Explain the theory of relativity."
]
```

**Response:**

A ZIP file (`application/zip`) containing MP3 audio files for each question, named `question_0.mp3` `question_1.mp3` etc.

---

### `POST /login`

Logs in a user and sets a session cookie.

**Input (query parameter):**

| Field          | Type   | Required | Description                               |
|----------------|--------|----------|-------------------------------------------|
| `email`        | string | Yes      | The user's email address                  |
| `oauth_token`  | string | Yes      | Token provided by sign-in attempt by user |

**Response:**

```json
{
    "api_key": "ORAL_EXAM_API_KEY" 
}
```
`ORAL_EXAM_API_KEY` is the static key for the entire backend. We give the user the key if we can verify that they have logged in with Google.

A `session_token` cookie is also set on the response.

---

### `POST /logout`

Logs out the current user and clears the session cookie.

**Input:**

| Field           | Type   | Required | Description                         |
|-----------------|--------|----------|-------------------------------------|
| `session_token` | cookie | Yes      | The session cookie set during login |

**Response:**

```json
{
    "message": "Logged out"
}
```
