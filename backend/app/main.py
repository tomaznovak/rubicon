from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Dict, List
import backend.agency as agency
from . import schemas
from backend.db import database, models
from backend.db.database import get_db
from sqlalchemy.orm import Session
from .routers import func, auth
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

origins = [
    "https://www.google.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(func.router)
app.include_router(auth.router)

templates = Jinja2Templates(directory="frontend")

@app.get('/', response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse("land.html", {"request": request})

@app.post('/run/',status_code=status.HTTP_200_OK, response_model=schemas.Response)
async def run(prompt: schemas.Prompt, db: Session = Depends(get_db)) -> Dict:
    try:
        response = agency.agency.get_completion(prompt.prompt)
        return {'response': response}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/files', response_model=List[schemas.FileInfo])
async def api(db: Session = Depends(get_db)):
    try:
        pdf_files = db.query(models.PDF).all()
        md_files = db.query(models.MD).all()

        files = []
        for p in pdf_files:
            files.append(schemas.FileInfo(
                id=p.id,
                name=p.name,
                type="pdf",
                size=f"{len(p.data) / 1024:.2f}KB",
                url=f"http://127.0.0.1:8000/agent/download/pdf/{p.id}"
            ))

        for m in md_files:
            files.append(schemas.FileInfo(
                id=m.id,
                name=m.name,
                type="md",
                size=f"{len(m.data) / 1024:.2f}KB",
                url=f"http://127.0.0.1:8000/agent/download/md/{m.id}"
            ))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return files

@app.get('/login', response_class=HTMLResponse)
async def log(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=8080
    )