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
