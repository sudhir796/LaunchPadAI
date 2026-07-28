from fastapi import FastAPI
from database import engine, Base
import models
from routes import ideas

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LaunchPad AI Backend")
app.include_router(ideas.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
