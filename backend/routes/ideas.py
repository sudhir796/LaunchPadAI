from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db, SessionLocal
from backend import models
from backend import schemas
from backend import orchestrator
from backend import events
import json

router = APIRouter(prefix="/ideas", tags=["ideas"])

async def start_pipeline_task(idea_id: str):
    db = SessionLocal()
    try:
        await orchestrator.run_pipeline(idea_id, db)
    finally:
        db.close()

async def start_retry_task(idea_id: str, agent_name: str):
    db = SessionLocal()
    try:
        await orchestrator.retry_agent(idea_id, agent_name, db)
    finally:
        db.close()

@router.post("/", response_model=schemas.IdeaResponse)
def create_idea(idea: schemas.IdeaCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    db_idea = models.Idea(
        title=idea.title,
        description=idea.description,
        target_market=idea.target_market,
        region=idea.region,
        sector=idea.sector,
        status="pending"
    )
    db.add(db_idea)
    db.commit()
    db.refresh(db_idea)
    
    agents = [
        "idea_validator", "patent_search", "market_research", 
        "competitor_analysis", "business_model", "pitch_deck", "investor_matching"
    ]
    for agent_name in agents:
        agent_output = models.AgentOutput(
            idea_id=db_idea.id,
            agent_name=agent_name,
            status="pending"
        )
        db.add(agent_output)
    db.commit()
    
    background_tasks.add_task(start_pipeline_task, db_idea.id)
    
    return db_idea

@router.get("/", response_model=List[schemas.IdeaResponse])
def get_ideas(
    limit: int = 20,
    offset: int = 0,
    skip: Optional[int] = None,
    db: Session = Depends(get_db)
):
    actual_offset = skip if skip is not None else offset
    ideas = (
        db.query(models.Idea)
        .order_by(models.Idea.created_at.desc())
        .offset(actual_offset)
        .limit(limit)
        .all()
    )
    return ideas

@router.get("/{idea_id}", response_model=schemas.IdeaDetailResponse)
def get_idea(idea_id: str, db: Session = Depends(get_db)):
    idea = db.query(models.Idea).filter(models.Idea.id == idea_id).first()
    if idea is None:
        raise HTTPException(status_code=404, detail="Idea not found")
    return idea

@router.get("/{idea_id}/stream")
async def stream_idea_events(idea_id: str):
    async def event_generator():
        async for event in events.subscribe(idea_id):
            yield f"data: {json.dumps(event)}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/{idea_id}/agents/{agent_name}", response_model=schemas.AgentOutputResponse)
def get_agent_output(idea_id: str, agent_name: str, db: Session = Depends(get_db)):
    agent_output = db.query(models.AgentOutput).filter(
        models.AgentOutput.idea_id == idea_id,
        models.AgentOutput.agent_name == agent_name
    ).first()
    if not agent_output:
        raise HTTPException(status_code=404, detail="Agent output not found")
    return agent_output

@router.post("/{idea_id}/retry/{agent_name}")
def retry_agent(idea_id: str, agent_name: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    idea = db.query(models.Idea).filter(models.Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
        
    agent_record = db.query(models.AgentOutput).filter(
        models.AgentOutput.idea_id == idea_id,
        models.AgentOutput.agent_name == agent_name
    ).first()
    
    if not agent_record:
        raise HTTPException(status_code=404, detail="Agent output not found")
        
    background_tasks.add_task(start_retry_task, idea_id, agent_name)
    return {"status": "retry_started", "idea_id": idea_id, "agent_name": agent_name}


@router.get("/{idea_id}/report")
def download_idea_report(idea_id: str, db: Session = Depends(get_db)):
    idea = db.query(models.Idea).filter(models.Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    agent_records = db.query(models.AgentOutput).filter(models.AgentOutput.idea_id == idea_id).all()
    agent_outputs_map = {}
    for record in agent_records:
        if record.output_json:
            agent_outputs_map[record.agent_name] = record.output_json

    from backend.readiness_calculator import calculate_investor_readiness_score
    readiness = calculate_investor_readiness_score(agent_outputs_map)

    idea_data = {
        "id": idea.id,
        "title": idea.title,
        "description": idea.description,
        "target_market": idea.target_market,
        "region": idea.region,
        "sector": idea.sector,
        "created_at": str(idea.created_at),
        "investor_readiness_score": readiness["investor_readiness_score"],
        "star_rating": readiness["star_rating"]
    }

    try:
        from backend import report_generator
        from fastapi import Response
        pdf_bytes = report_generator.build_pdf_report(idea_data, agent_outputs_map)
        filename = f"LaunchPad_Report_{idea_id[:8]}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {str(e)}")


@router.post("/{idea_id}/export-pdf")
def export_idea_pdf(idea_id: str, db: Session = Depends(get_db)):
    idea = db.query(models.Idea).filter(models.Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    agent_records = db.query(models.AgentOutput).filter(models.AgentOutput.idea_id == idea_id).all()
    agent_outputs_map = {}
    for record in agent_records:
        if record.output_json:
            agent_outputs_map[record.agent_name] = record.output_json

    from backend.readiness_calculator import calculate_investor_readiness_score
    readiness = calculate_investor_readiness_score(agent_outputs_map)

    idea_data = {
        "id": idea.id,
        "title": idea.title,
        "description": idea.description,
        "target_market": idea.target_market,
        "region": idea.region,
        "sector": idea.sector,
        "created_at": str(idea.created_at),
        "investor_readiness_score": readiness["investor_readiness_score"],
        "star_rating": readiness["star_rating"]
    }

    try:
        from backend import report_generator
        from fastapi import Response
        pdf_bytes = report_generator.build_pdf_report(idea_data, agent_outputs_map)
        filename = f"LaunchPad_Report_{idea_id[:8]}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {str(e)}")
