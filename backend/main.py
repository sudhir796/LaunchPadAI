from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine, Base
from backend import models
from backend.routes import ideas

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LaunchPad AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ideas.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
