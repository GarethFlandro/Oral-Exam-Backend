import uvicorn
from fastapi import FastAPI, Depends

from api.routes import router
from api.routes import get_api_key


app = FastAPI(title="Oral Exam Backend")

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)


