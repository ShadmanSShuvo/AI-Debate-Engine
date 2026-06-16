from typing import TypedDict, List, Dict, Any, Optional

class DebateState(TypedDict):
    debate_id: int
    topic: str
    scope: List[str]
    neutral_framing: str
    evidence: List[Dict[str, Any]]
    pro_arguments: List[Dict[str, Any]]
    con_arguments: List[Dict[str, Any]]
    rebuttals: List[Dict[str, Any]]
    fallacies: List[Dict[str, Any]]
    verifications: List[Dict[str, Any]]
    winner: str
    pro_score: float
    con_score: float
    decision_reasoning: str
    report: str
    status: str
    current_step: str
    error_message: Optional[str]
