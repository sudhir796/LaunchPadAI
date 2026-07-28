import traceback
import asyncio
from sqlalchemy.orm import Session
import models
import events
from agents import (
    idea_validator, patent_search, market_research,
    competitor_analysis, business_model, pitch_deck, investor_matching
)

def get_fallback_data(agent_name: str, idea_id: str) -> dict:
    note = " (fallback data used)"
    fallbacks = {
        "patent_search": {
            "idea_id": idea_id,
            "similar_patents": [
                { "title": f"Automated System{note}", "summary": "Fallback summary", "source_url": "https://example.com" }
            ],
            "risk_level": "medium",
            "notes": f"Search API unavailable{note}"
        },
        "market_research": {
            "idea_id": idea_id,
            "market_size_estimate": f"$1B fallback{note}",
            "growth_trends": f"10% fallback{note}",
            "target_demographics": f"General fallback{note}",
            "sources": []
        },
        "competitor_analysis": {
            "idea_id": idea_id,
            "competitors": [
                { "name": f"Competitor X{note}", "description": "Fallback", "strengths": "N/A", "weaknesses": "N/A", "source_url": "https://example.com" }
            ],
            "differentiation_opportunities": f"Fallback differentiation{note}"
        },
        "investor_matching": {
            "idea_id": idea_id,
            "matched_investors": [
                { "name": f"Fallback Capital{note}", "focus_area": "Tech", "reason": "Fallback reason" }
            ]
        }
    }
    return fallbacks.get(agent_name, {"idea_id": idea_id, "error": f"Fallback not defined{note}"})


def get_stages(idea_id: str):
    return [
        {
            "name": "idea_validator",
            "module": idea_validator,
            "build_input": lambda idea, outputs: {
                "idea_id": idea_id,
                "idea_title": idea.title,
                "idea_description": idea.description,
                "target_market": idea.target_market
            }
        },
        {
            "name": "patent_search",
            "module": patent_search,
            "build_input": lambda idea, outputs: {
                "idea_id": idea_id,
                "idea_description": idea.description,
                "keywords": []
            }
        },
        {
            "name": "market_research",
            "module": market_research,
            "build_input": lambda idea, outputs: {
                "idea_id": idea_id,
                "idea_description": idea.description,
                "target_market": idea.target_market or "General",
                "region": idea.region
            }
        },
        {
            "name": "competitor_analysis",
            "module": competitor_analysis,
            "build_input": lambda idea, outputs: {
                "idea_id": idea_id,
                "idea_description": idea.description,
                "market_research": outputs["market_research"]
            }
        },
        {
            "name": "business_model",
            "module": business_model,
            "build_input": lambda idea, outputs: {
                "idea_id": idea_id,
                "idea_description": idea.description,
                "market_research": outputs["market_research"],
                "competitor_analysis": outputs["competitor_analysis"]
            }
        },
        {
            "name": "pitch_deck",
            "module": pitch_deck,
            "build_input": lambda idea, outputs: {
                "idea_id": idea_id,
                "idea_validation": outputs["idea_validator"],
                "market_research": outputs["market_research"],
                "competitor_analysis": outputs["competitor_analysis"],
                "business_model": outputs["business_model"]
            }
        },
        {
            "name": "investor_matching",
            "module": investor_matching,
            "build_input": lambda idea, outputs: {
                "idea_id": idea_id,
                "sector": idea.sector or "Technology",
                "business_model": outputs["business_model"]
            }
        }
    ]

async def run_pipeline(idea_id: str, db_session: Session):
    idea = db_session.query(models.Idea).filter(models.Idea.id == idea_id).first()
    if not idea:
        return
        
    idea.status = "running"
    db_session.commit()
    
    stages = get_stages(idea_id)
    
    outputs = {}
    
    for stage in stages:
        agent_name = stage["name"]
        agent_record = db_session.query(models.AgentOutput).filter(
            models.AgentOutput.idea_id == idea_id,
            models.AgentOutput.agent_name == agent_name
        ).first()
        
        if agent_record:
            agent_record.status = "running"
            db_session.commit()
            
        try:
            agent_input = stage["build_input"](idea, outputs)
            
            # Wrap real agent calls in a timeout
            if agent_name in ["patent_search", "market_research", "competitor_analysis", "investor_matching"]:
                output_json = await asyncio.wait_for(stage["module"].run(agent_input), timeout=10.0)
            else:
                output_json = await stage["module"].run(agent_input)
            
            outputs[agent_name] = output_json
            
            if agent_record:
                agent_record.output_json = output_json
                agent_record.status = "done"
                db_session.commit()
            
            events.publish(idea_id, {
                "agent_name": agent_name,
                "status": "done",
                "output": output_json
            })
                
        except Exception as e:
            error_msg = str(e) + "\n" + traceback.format_exc()
            
            # Apply fallback for external agents instead of crashing
            if agent_name in ["patent_search", "market_research", "competitor_analysis", "investor_matching"]:
                fallback_json = get_fallback_data(agent_name, idea_id)
                outputs[agent_name] = fallback_json
                
                if agent_record:
                    agent_record.output_json = fallback_json
                    agent_record.status = "done"
                    agent_record.error_message = f"Fallback triggered due to: {str(e)}"
                    db_session.commit()
                
                events.publish(idea_id, {
                    "agent_name": agent_name,
                    "status": "done",
                    "output": fallback_json
                })
                continue # Continue pipeline with fallback
            
            # For non-external agents, stop pipeline on error
            if agent_record:
                agent_record.status = "error"
                agent_record.error_message = error_msg
                db_session.commit()
            
            events.publish(idea_id, {
                "agent_name": agent_name,
                "status": "error",
                "error_message": error_msg
            })
            
            idea.status = "error"
            db_session.commit()
            return  # STOP pipeline on error
            
    idea.status = "done"
    db_session.commit()

async def retry_agent(idea_id: str, agent_name: str, db_session: Session):
    idea = db_session.query(models.Idea).filter(models.Idea.id == idea_id).first()
    if not idea:
        return
        
    stages = get_stages(idea_id)
    target_stage = next((s for s in stages if s["name"] == agent_name), None)
    if not target_stage:
        return

    # Load all prior outputs needed to build input
    outputs = {}
    all_agent_records = db_session.query(models.AgentOutput).filter(models.AgentOutput.idea_id == idea_id).all()
    for record in all_agent_records:
        outputs[record.agent_name] = record.output_json

    agent_record = next((r for r in all_agent_records if r.agent_name == agent_name), None)
    
    if agent_record:
        agent_record.status = "running"
        db_session.commit()
        
    try:
        agent_input = target_stage["build_input"](idea, outputs)
        
        if agent_name in ["patent_search", "market_research", "competitor_analysis", "investor_matching"]:
            output_json = await asyncio.wait_for(target_stage["module"].run(agent_input), timeout=10.0)
        else:
            output_json = await target_stage["module"].run(agent_input)
            
        if agent_record:
            agent_record.output_json = output_json
            agent_record.status = "done"
            agent_record.error_message = None
            db_session.commit()
        
        events.publish(idea_id, {
            "agent_name": agent_name,
            "status": "done",
            "output": output_json
        })
        
    except Exception as e:
        error_msg = str(e) + "\n" + traceback.format_exc()
        if agent_record:
            agent_record.status = "error"
            agent_record.error_message = error_msg
            db_session.commit()
        
        events.publish(idea_id, {
            "agent_name": agent_name,
            "status": "error",
            "error_message": error_msg
        })
