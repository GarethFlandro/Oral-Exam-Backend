# Oral-Exam-Backend

<h1>How to set up</h1>

1) Download repository <br>
2) Choose a hosting platform (Heroku, AWS, etc.) <br>
3) Set up environment variables: <br>
Claude API key: `CLAUDE_API_KEY` <br>
Gemini API key: `GEMINI_API_KEY` <br>
4) Deploy the application <br>

<h1>API Endpoints</h1>

1) POST /analyze <br>
- Takes `audio` of type `string($binary)` (audio file) <br>
- Takes `class_name` of type `string`<br>
- Returns 200 code and `application/json` or 422 code and `application/json` <br><br>
2) POST /detect-cheating <br>
- Takes `audio` of type `string($binary)` (audio file) <br>
- Takes `video` of type `string($binary)` (video file) <br>
- Planning on taking second video for screen recording and camera recording <br>
- Returns 200 code and `application/json` or 422 code and `application/json`

<h1>Full Return Types</h1>

`/analyze`

```
{
    "success": True (bool),
    "grade": average_grade (int),
    "class_name": class_name (str),
}
```

`/detect-cheating`

```
{
    "success": True (bool),
    "is_cheating": result.is_cheating (bool),
    "confidence": result.confidence (str),
    "summary": result.summary (str),
    "indicators_found": result.indicators_found (list),
    "recommendation": result.recommendation (str),
    "notes": result.notes (str),
}
```
