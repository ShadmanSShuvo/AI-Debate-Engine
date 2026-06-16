import os
from typing import List, Optional
from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from datetime import datetime

from backend.database.db import init_db, get_session, engine
from backend.database.models import Debate, Argument, Fallacy, Evidence, Rebuttal, Verification
from backend.agents.graph import run_debate_pipeline

app = FastAPI(title="AI Debate Engine API", version="1.0.0")

# Enable CORS for Next.js frontend (local development on port 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development ease, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

# Request Model
from pydantic import BaseModel
class DebateRequest(BaseModel):
    topic: str

# Response Models (Nested schemas)
class EvidenceResponse(BaseModel):
    id: int
    source: str
    claim: str
    confidence: float

class ArgumentResponse(BaseModel):
    id: int
    side: str
    claim: str
    evidence: str
    impact: str
    score: float

class RebuttalResponse(BaseModel):
    id: int
    target_argument_id: int
    side: str
    claim: str
    question: str

class FallacyResponse(BaseModel):
    id: int
    argument_id: Optional[int]
    type: str
    severity: float
    explanation: str

class VerificationResponse(BaseModel):
    id: int
    claim: str
    evidence_used: str
    status: str
    reasoning: str

class DebateDetailResponse(BaseModel):
    id: int
    topic: str
    created_at: datetime
    winner: Optional[str]
    scope: Optional[str]
    status: str
    error_message: Optional[str]
    pro_opening: Optional[str]
    con_opening: Optional[str]
    pro_score: Optional[float] = None
    con_score: Optional[float] = None
    decision_reasoning: Optional[str] = None
    report: Optional[str]
    evidence_items: List[EvidenceResponse] = []
    arguments: List[ArgumentResponse] = []
    rebuttals: List[RebuttalResponse] = []
    fallacies: List[FallacyResponse] = []
    verifications: List[VerificationResponse] = []

@app.post("/api/debates", response_model=DebateDetailResponse, status_code=status.HTTP_201_CREATED)
def create_debate(request: DebateRequest, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    topic = request.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
        
    # Create DB entry
    db_debate = Debate(
        topic=topic,
        status="pending",
        created_at=datetime.utcnow()
    )
    session.add(db_debate)
    session.commit()
    session.refresh(db_debate)
    
    # Run the debate pipeline asynchronously in the background
    background_tasks.add_task(run_debate_pipeline, db_debate.id, topic)
    
    return db_debate

@app.get("/api/debates", response_model=List[DebateDetailResponse])
def list_debates(session: Session = Depends(get_session)):
    statement = select(Debate).order_by(Debate.created_at.desc())
    debates = session.exec(statement).all()
    return debates

@app.get("/api/debates/{debate_id}", response_model=DebateDetailResponse)
def get_debate_details(debate_id: int, session: Session = Depends(get_session)):
    db_debate = session.get(Debate, debate_id)
    if not db_debate:
        raise HTTPException(status_code=404, detail="Debate not found")
    return db_debate

@app.get("/api/debates/{debate_id}/status")
def get_debate_status(debate_id: int, session: Session = Depends(get_session)):
    db_debate = session.get(Debate, debate_id)
    if not db_debate:
        raise HTTPException(status_code=404, detail="Debate not found")
    return {
        "id": db_debate.id,
        "status": db_debate.status,
        "error_message": db_debate.error_message,
        "winner": db_debate.winner
    }

@app.delete("/api/debates/{debate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_debate(debate_id: int, session: Session = Depends(get_session)):
    db_debate = session.get(Debate, debate_id)
    if not db_debate:
        raise HTTPException(status_code=404, detail="Debate not found")
    session.delete(db_debate)
    session.commit()
    return None
