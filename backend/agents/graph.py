from langgraph.graph import StateGraph, START, END
from typing import Dict, Any

from backend.agents.state import DebateState
from backend.agents.debate_agents import (
    debate_orchestrator_node,
    research_agent_node,
    pro_agent_node,
    con_agent_node,
    crossexam_agent_node,
    fallacy_detector_node,
    evidence_verifier_node,
    judge_agent_node,
    report_generator_node,
    update_debate_status
)

def build_debate_graph():
    # Initialize the workflow state graph
    workflow = StateGraph(DebateState)
    
    # Add nodes
    workflow.add_node("orchestrator", debate_orchestrator_node)
    workflow.add_node("research", research_agent_node)
    workflow.add_node("pro", pro_agent_node)
    workflow.add_node("con", con_agent_node)
    workflow.add_node("crossexam", crossexam_agent_node)
    workflow.add_node("fallacy", fallacy_detector_node)
    workflow.add_node("verifier", evidence_verifier_node)
    workflow.add_node("judge", judge_agent_node)
    workflow.add_node("report", report_generator_node)
    
    # Connect nodes
    workflow.add_edge(START, "orchestrator")
    workflow.add_edge("orchestrator", "research")
    workflow.add_edge("research", "pro")
    workflow.add_edge("pro", "con")
    workflow.add_edge("con", "crossexam")
    workflow.add_edge("crossexam", "fallacy")
    workflow.add_edge("fallacy", "verifier")
    workflow.add_edge("verifier", "judge")
    workflow.add_edge("judge", "report")
    workflow.add_edge("report", END)
    
    return workflow.compile()

# Compile the graph
debate_app = build_debate_graph()

def run_debate_pipeline(debate_id: int, topic: str):
    """
    Executes the multi-agent debate pipeline for a specific debate_id and topic.
    Catches errors and updates status to failed.
    """
    initial_state: DebateState = {
        "debate_id": debate_id,
        "topic": topic,
        "scope": [],
        "neutral_framing": "",
        "evidence": [],
        "pro_arguments": [],
        "con_arguments": [],
        "rebuttals": [],
        "fallacies": [],
        "verifications": [],
        "winner": "",
        "pro_score": 0.0,
        "con_score": 0.0,
        "decision_reasoning": "",
        "report": "",
        "status": "pending",
        "current_step": "orchestrating",
        "error_message": None
    }
    
    try:
        print(f"=== Starting Debate Pipeline for Debate ID {debate_id} ===")
        # Run graph execution
        final_state = debate_app.invoke(initial_state)
        print(f"=== Debate Pipeline Completed for Debate ID {debate_id}. Winner: {final_state.get('winner')} ===")
        return final_state
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"=== ERROR in Debate Pipeline for Debate ID {debate_id}: {e} ===\n{error_details}")
        update_debate_status(debate_id, "failed", error_message=f"{str(e)}\n{error_details}")
        raise e
