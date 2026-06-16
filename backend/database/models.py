from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class Debate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    topic: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    winner: Optional[str] = None  # "Pro", "Con", or "Tie"
    scope: Optional[str] = None   # Comma-separated list of scopes
    status: str = Field(default="pending")  # "pending", "running", "completed", "failed"
    error_message: Optional[str] = None
    pro_opening: Optional[str] = None
    con_opening: Optional[str] = None
    pro_score: Optional[float] = None
    con_score: Optional[float] = None
    decision_reasoning: Optional[str] = None
    report: Optional[str] = None  # Complete Markdown debate report

    # Relationships
    arguments: List["Argument"] = Relationship(back_populates="debate", cascade_delete=True)
    evidence_items: List["Evidence"] = Relationship(back_populates="debate", cascade_delete=True)
    rebuttals: List["Rebuttal"] = Relationship(back_populates="debate", cascade_delete=True)
    verifications: List["Verification"] = Relationship(back_populates="debate", cascade_delete=True)
    fallacies: List["Fallacy"] = Relationship(back_populates="debate", cascade_delete=True)

class Argument(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    debate_id: int = Field(foreign_key="debate.id", index=True, ondelete="CASCADE")
    side: str  # "Pro" or "Con"
    claim: str
    evidence: str
    impact: str
    score: float = 0.0

    # Relationships
    debate: Debate = Relationship(back_populates="arguments")
    fallacies: List["Fallacy"] = Relationship(back_populates="argument", cascade_delete=True)
    rebuttals: List["Rebuttal"] = Relationship(back_populates="target_argument", cascade_delete=True)

class Fallacy(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    debate_id: int = Field(foreign_key="debate.id", index=True, ondelete="CASCADE")
    argument_id: Optional[int] = Field(default=None, foreign_key="argument.id", index=True, ondelete="CASCADE")
    type: str  # e.g., "False Dilemma", "Slippery Slope", etc.
    severity: float  # 0.0 to 1.0
    explanation: str

    # Relationships
    debate: Debate = Relationship(back_populates="fallacies")
    argument: Optional[Argument] = Relationship(back_populates="fallacies")

class Evidence(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    debate_id: int = Field(foreign_key="debate.id", index=True, ondelete="CASCADE")
    source: str
    claim: str
    confidence: float

    # Relationships
    debate: Debate = Relationship(back_populates="evidence_items")

class Rebuttal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    debate_id: int = Field(foreign_key="debate.id", index=True, ondelete="CASCADE")
    target_argument_id: int = Field(foreign_key="argument.id", index=True, ondelete="CASCADE")
    side: str  # Side making the rebuttal ("Pro" or "Con")
    claim: str
    question: str

    # Relationships
    debate: Debate = Relationship(back_populates="rebuttals")
    target_argument: Argument = Relationship(back_populates="rebuttals")

class Verification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    debate_id: int = Field(foreign_key="debate.id", index=True, ondelete="CASCADE")
    claim: str
    evidence_used: str
    status: str  # "supported", "partially supported", "unsupported"
    reasoning: str

    # Relationships
    debate: Debate = Relationship(back_populates="verifications")
