import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.database import Base

def generate_uuid():
    return str(uuid.uuid4())

def get_utc_now():
    return datetime.now(timezone.utc)

class Idea(Base):
    __tablename__ = "ideas"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    target_market = Column(String, nullable=True)
    region = Column(String, nullable=True)
    sector = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending/running/done/error
    created_at = Column(DateTime, default=get_utc_now)

    agent_outputs = relationship("AgentOutput", back_populates="idea")

class AgentOutput(Base):
    __tablename__ = "agent_outputs"

    id = Column(String, primary_key=True, default=generate_uuid)
    idea_id = Column(String, ForeignKey("ideas.id"), nullable=False)
    agent_name = Column(String, nullable=False)
    output_json = Column(JSON, nullable=True)
    status = Column(String, default="pending")  # pending/running/done/error
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    idea = relationship("Idea", back_populates="agent_outputs")
