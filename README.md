# Oral-Exam-Backend
TODO
- Anticheat model
- Set up billing
- Replace 1.5 temp gemini with another model

<h1>How to set up</h1>
1) Download repository <br>
2) Choose a hosting platform (e.g. Heroku, AWS, etc.) <br>
3) Set up environment variables: <br>
&emsp;&emsp;- Claude API key: CLAUDE_API_KEY <br>
&emsp;&emsp;- Gemini API key: GEMINI_API_KEY <br>
4) Deploy the application <br>

<h1>API Endpoints</h1>
1) POST /analyze <br>
&emsp;&emsp;- Takes `audio` of type `string($binary)` (audio file) <br>
&emsp;&emsp;- Takes `class_name` of type `string`<br>
&emsp;&emsp;- Returns 200 code and `application/json` or 422 code and `application/json` <br><br>
2) POST /detect-cheating <br>
&emsp;&emsp;- Takes `audio` of type `string($binary)` (audio file) <br>
&emsp;&emsp;- Takes `video` of type `string($binary)` (video file) <br>
&emsp;&emsp;- Planning on taking second video for screen recording and camera recording <br>
&emsp;&emsp;- Returns 200 code and `application/json` or 422 code and `application/json`

<h1>Full Return Types</h1>

<h3>`/analyze Endpoint`</h3>
```
{
    "success": True (bool),
    "grade": average_grade (int),
    "class_name": class_name (str),
}
```
<h3>`/detect-cheating`</h3>
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