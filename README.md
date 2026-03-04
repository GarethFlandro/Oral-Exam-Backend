# Oral-Exam-Backend

<h1>How to set up</h1>

1) Download repository <br>
2) Choose a hosting platform (Heroku, AWS, etc.) <br>
3) Set up environment variables: <br>
Claude API key: `CLAUDE_API_KEY` <br>
Gemini API key: `GEMINI_API_KEY` <br>
4) Deploy the application <br>


<h1>Endpoint Return Types</h1>

`/analyze`

```
{
        "grade": average_grade,
        "class_name": class_name,
        "gemini_initial_grade": gemini1_grade,
        "claude_initial_grade": claude1_grade,
        "gemini_review_grade": gemini2_grade,
        "claude_review_grade": claude2_grade,
    }
```

`/detect-cheating`

```
{
    "is_cheating": result.is_cheating (bool),
    "confidence": result.confidence (str),
    "summary": result.summary (str),
    "indicators_found": result.indicators_found (list),
    "recommendation": result.recommendation (str),
    "notes": result.notes (str),
}
```

`/generate-speech`

```
"string"
```

`/login`

```
"string"
```

`/logout`

```
"string"
```
