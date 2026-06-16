import json
from typing import Dict, Any, List
from sqlmodel import Session, select
from duckduckgo_search import DDGS

from backend.database.db import engine
from backend.database.models import Debate, Argument, Fallacy, Evidence, Rebuttal, Verification
from backend.agents.llm import run_agent_prompt
from backend.agents.state import DebateState

# ==========================================
# Database Persistence Helpers
# ==========================================

def update_debate_status(debate_id: int, status: str, error_message: str = None):
    with Session(engine) as session:
        db_debate = session.get(Debate, debate_id)
        if db_debate:
            db_debate.status = status
            if error_message:
                db_debate.error_message = error_message
            session.add(db_debate)
            session.commit()

def db_update_orchestrator(debate_id: int, scope: List[str], neutral_framing: str):
    with Session(engine) as session:
        db_debate = session.get(Debate, debate_id)
        if db_debate:
            db_debate.scope = ",".join(scope)
            db_debate.status = "researching"
            session.add(db_debate)
            session.commit()

def db_update_evidence(debate_id: int, evidence_list: List[Dict[str, Any]]):
    with Session(engine) as session:
        # Clear existing evidence just in case
        statement = select(Evidence).where(Evidence.debate_id == debate_id)
        existing = session.exec(statement).all()
        for e in existing:
            session.delete(e)
            
        for item in evidence_list:
            ev = Evidence(
                debate_id=debate_id,
                source=item.get("source", "Unknown Source"),
                claim=item.get("claim", ""),
                confidence=float(item.get("confidence", 0.8))
            )
            session.add(ev)
            
        db_debate = session.get(Debate, debate_id)
        if db_debate:
            db_debate.status = "pro_arguing"
        session.commit()

def db_update_arguments(debate_id: int, side: str, opening_statement: str, arguments_list: List[Dict[str, Any]]):
    with Session(engine) as session:
        # Clear existing arguments for this side
        statement = select(Argument).where(Argument.debate_id == debate_id, Argument.side == side)
        existing = session.exec(statement).all()
        for a in existing:
            session.delete(a)
            
        for item in arguments_list:
            arg = Argument(
                debate_id=debate_id,
                side=side,
                claim=item.get("claim", ""),
                evidence=item.get("evidence", ""),
                impact=item.get("impact", ""),
                score=0.0
            )
            session.add(arg)
            
        db_debate = session.get(Debate, debate_id)
        if db_debate:
            if side == "Pro":
                db_debate.pro_opening = opening_statement
                db_debate.status = "con_arguing"
            else:
                db_debate.con_opening = opening_statement
                db_debate.status = "cross_examining"
        session.commit()

def db_update_rebuttals(debate_id: int, rebuttals_list: List[Dict[str, Any]]):
    with Session(engine) as session:
        # Clear existing rebuttals
        statement = select(Rebuttal).where(Rebuttal.debate_id == debate_id)
        existing = session.exec(statement).all()
        for r in existing:
            session.delete(r)
            
        for item in rebuttals_list:
            # Find target argument
            target_claim = item.get("target_argument_claim", item.get("target_argument", ""))
            arg_stmt = select(Argument).where(Argument.debate_id == debate_id, Argument.claim == target_claim)
            target_arg = session.exec(arg_stmt).first()
            
            if target_arg:
                reb_side = "Con" if target_arg.side == "Pro" else "Pro"
                reb = Rebuttal(
                    debate_id=debate_id,
                    target_argument_id=target_arg.id,
                    side=reb_side,
                    claim=item.get("claim", ""),
                    question=item.get("question", "")
                )
                session.add(reb)
                
        db_debate = session.get(Debate, debate_id)
        if db_debate:
            db_debate.status = "detecting_fallacies"
        session.commit()

def db_update_fallacies(debate_id: int, fallacies_list: List[Dict[str, Any]]):
    with Session(engine) as session:
        # Clear existing fallacies
        statement = select(Fallacy).where(Fallacy.debate_id == debate_id)
        existing = session.exec(statement).all()
        for f in existing:
            session.delete(f)
            
        for item in fallacies_list:
            target_claim = item.get("argument_claim", "")
            arg_stmt = select(Argument).where(Argument.debate_id == debate_id, Argument.claim == target_claim)
            target_arg = session.exec(arg_stmt).first()
            
            f = Fallacy(
                debate_id=debate_id,
                argument_id=target_arg.id if target_arg else None,
                type=item.get("fallacy", "Logical Fallacy"),
                severity=float(item.get("severity", 0.5)),
                explanation=item.get("explanation", "")
            )
            session.add(f)
            
        db_debate = session.get(Debate, debate_id)
        if db_debate:
            db_debate.status = "verifying_evidence"
        session.commit()

def db_update_verifications(debate_id: int, verifications_list: List[Dict[str, Any]]):
    with Session(engine) as session:
        # Clear existing verifications
        statement = select(Verification).where(Verification.debate_id == debate_id)
        existing = session.exec(statement).all()
        for v in existing:
            session.delete(v)
            
        for item in verifications_list:
            v = Verification(
                debate_id=debate_id,
                claim=item.get("claim", ""),
                evidence_used=item.get("evidence_used", ""),
                status=item.get("status", "partially supported"),
                reasoning=item.get("reasoning", "")
            )
            session.add(v)
            
        db_debate = session.get(Debate, debate_id)
        if db_debate:
            db_debate.status = "judging"
        session.commit()

def db_update_judge(debate_id: int, winner: str, pro_score: float, con_score: float, decision_reasoning: str):
    with Session(engine) as session:
        db_debate = session.get(Debate, debate_id)
        if db_debate:
            db_debate.winner = winner
            db_debate.status = "generating_report"
            db_debate.decision_reasoning = decision_reasoning  # We'll save this in report generation or temporary
            # Since the Debate table doesn't have score/reasoning fields, let's store them in the report or we can update argument scores
            # Let's set the scores on the argument table or store in report.
            # We can also add pro_score, con_score, and decision_reasoning to the debate table!
            # Wait, let's write it in the report, or let's add them to the Debate model later if needed. For now we will update Argument scores!
            # Let's assign individual argument scores or just general debate winner.
            
            # Let's distribute score: update arguments
            args = session.exec(select(Argument).where(Argument.debate_id == debate_id)).all()
            for arg in args:
                if arg.side == "Pro":
                    arg.score = pro_score
                else:
                    arg.score = con_score
                session.add(arg)
            session.add(db_debate)
            session.commit()

def db_update_report(debate_id: int, winner: str, report_markdown: str):
    with Session(engine) as session:
        db_debate = session.get(Debate, debate_id)
        if db_debate:
            db_debate.report = report_markdown
            db_debate.winner = winner
            db_debate.status = "completed"
            session.add(db_debate)
            session.commit()


# ==========================================
# DuckDuckGo Search Helper
# ==========================================

def search_web_evidence(topic: str) -> str:
    try:
        with DDGS() as ddgs:
            # Query for the topic + statistics or evidence
            query = f"{topic} empirical studies evidence statistics"
            results = list(ddgs.text(query, max_results=5))
            snippets = []
            for r in results:
                snippets.append(f"Source: {r.get('title', 'Web Article')} ({r.get('href', 'unknown')})\nContent: {r.get('body', '')}")
            if snippets:
                return "\n\n".join(snippets)
    except Exception as e:
        print(f"Web search failed: {e}")
    return ""


# ==========================================
# Agent Nodes
# ==========================================

# 1. Orchestrator Agent
def debate_orchestrator_node(state: DebateState) -> DebateState:
    print(f"--- [Agent 1: Debate Orchestrator] topic: {state['topic']} ---")
    update_debate_status(state["debate_id"], "orchestrating")
    
    prompt = f"""You are a debate coordinator.

Given a debate topic: "{state['topic']}"

1. Identify key dimensions.
2. Define debate scope (3-5 items).
3. Generate neutral framing (a short paragraph).
4. Avoid taking a side.

Return JSON only in this format:
{{
  "scope": ["dimension 1", "dimension 2", ...],
  "neutral_framing": "neutral statement..."
}}"""
    
    result = run_agent_prompt(prompt, "orchestrator", state["topic"])
    scope = result.get("scope", ["General feasibility", "Social impact", "Policy options"])
    neutral_framing = result.get("neutral_framing", f"Examining the topic: {state['topic']}")
    
    db_update_orchestrator(state["debate_id"], scope, neutral_framing)
    
    state["scope"] = scope
    state["neutral_framing"] = neutral_framing
    state["current_step"] = "orchestrated"
    return state


# 2. Research Agent
def research_agent_node(state: DebateState) -> DebateState:
    print(f"--- [Agent 2: Research Agent] ---")
    update_debate_status(state["debate_id"], "researching")
    
    # Run a quick DuckDuckGo search to provide context for RAG
    search_context = search_web_evidence(state["topic"])
    search_text = f"\n\nHere is live web search content for context:\n{search_context}" if search_context else ""
    
    prompt = f"""You are a research analyst.

Topic: "{state['topic']}"
Scope: {state['scope']}
{search_text}

Task:
Find:
- empirical studies
- statistics
- expert opinions
Extract evidence. Do not argue.
Ensure that confidence score is between 0.0 and 1.0.

Return JSON only in this format:
{{
  "evidence": [
    {{
      "claim": "Continuous assessments improve learning rates by 15%...",
      "source": "Journal of Education (2023)",
      "confidence": 0.85
    }}
  ]
}}"""
    
    result = run_agent_prompt(prompt, "evidence", state["topic"])
    evidence = result.get("evidence", [])
    
    db_update_evidence(state["debate_id"], evidence)
    
    state["evidence"] = evidence
    state["current_step"] = "researched"
    return state


# 3. Pro Agent
def pro_agent_node(state: DebateState) -> DebateState:
    print(f"--- [Agent 3: Pro Agent] ---")
    update_debate_status(state["debate_id"], "pro_arguing")
    
    prompt = f"""You are an elite debater.

Your goal is to defend the PRO position for: "{state['topic']}".

Rules:
- Use this retrieved evidence: {state['evidence']}
- Be extremely persuasive.
- Anticipate objections.
- Do not mention weaknesses of your own side.

Produce:
1. Opening statement (under "opening_statement")
2. Main arguments (under "arguments", list of objects: claim, evidence, impact)

Return JSON only in this format:
{{
  "opening_statement": "Your opening speech...",
  "arguments": [
    {{
      "claim": "AI grading improves consistency...",
      "evidence": "According to Smith (2024)...",
      "impact": "Eliminates grading disparity and frees up professors' time."
    }}
  ]
}}"""
    
    result = run_agent_prompt(prompt, "pro", state["topic"])
    opening_statement = result.get("opening_statement", "PRO Opening Statement.")
    arguments = result.get("arguments", [])
    
    db_update_arguments(state["debate_id"], "Pro", opening_statement, arguments)
    
    state["pro_arguments"] = arguments
    state["current_step"] = "pro_done"
    return state


# 4. Con Agent
def con_agent_node(state: DebateState) -> DebateState:
    print(f"--- [Agent 4: Con Agent] ---")
    update_debate_status(state["debate_id"], "con_arguing")
    
    prompt = f"""You are an elite debater.

Your goal is to defend the CON (opposing) position for: "{state['topic']}".

Rules:
- Use this retrieved evidence: {state['evidence']}
- Be extremely persuasive.
- Anticipate objections.
- Do not mention weaknesses of your own side.

Produce:
1. Opening statement (under "opening_statement")
2. Main arguments (under "arguments", list of objects: claim, evidence, impact)

Return JSON only in this format:
{{
  "opening_statement": "Your opening speech...",
  "arguments": [
    {{
      "claim": "AI grading inherits systematic bias...",
      "evidence": "According to NBER (2024)...",
      "impact": "Entrenches discrimination and lacks human nuanced grading."
    }}
  ]
}}"""
    
    result = run_agent_prompt(prompt, "con", state["topic"])
    opening_statement = result.get("opening_statement", "CON Opening Statement.")
    arguments = result.get("arguments", [])
    
    db_update_arguments(state["debate_id"], "Con", opening_statement, arguments)
    
    state["con_arguments"] = arguments
    state["current_step"] = "con_done"
    return state


# 5. Cross-Examination Agent
def crossexam_agent_node(state: DebateState) -> DebateState:
    print(f"--- [Agent 5: Cross-Examination Agent] ---")
    update_debate_status(state["debate_id"], "cross_examining")
    
    prompt = f"""You are a cross-examiner.

For every argument from both Pro and Con:
Pro arguments: {state['pro_arguments']}
Con arguments: {state['con_arguments']}

Task:
1. Find hidden assumptions.
2. Identify weak evidence.
3. Generate rebuttals.
4. Ask challenging questions.

Return JSON only in this format:
{{
  "rebuttals": [
    {{
      "target_argument_claim": "The exact claim of the argument you are rebutting",
      "claim": "Rebuttal counter-claim...",
      "question": "Challenging question for cross-examination..."
    }}
  ]
}}"""
    
    result = run_agent_prompt(prompt, "crossexam", state["topic"])
    rebuttals = result.get("rebuttals", [])
    
    db_update_rebuttals(state["debate_id"], rebuttals)
    
    state["rebuttals"] = rebuttals
    state["current_step"] = "crossexam_done"
    return state


# 6. Fallacy Detector Agent
def fallacy_detector_node(state: DebateState) -> DebateState:
    print(f"--- [Agent 6: Fallacy Detector] ---")
    update_debate_status(state["debate_id"], "detecting_fallacies")
    
    prompt = f"""You are a logic professor.

Analyze these debate arguments for logical fallacies:
Pro Arguments: {state['pro_arguments']}
Con Arguments: {state['con_arguments']}

Identify:
- logical fallacies (e.g. Strawman, Ad hominem, Slippery slope, False dilemma, Appeal to authority, Hasty generalization)
- unsupported claims
- weak causal links
- severity score (float between 0.0 and 1.0)

Return JSON only in this format:
{{
  "fallacies": [
    {{
      "argument_claim": "The exact claim containing the fallacy",
      "fallacy": "False Dilemma",
      "severity": 0.75,
      "explanation": "Presents a false binary..."
    }}
  ]
}}"""
    
    result = run_agent_prompt(prompt, "fallacy", state["topic"])
    fallacies = result.get("fallacies", [])
    
    db_update_fallacies(state["debate_id"], fallacies)
    
    state["fallacies"] = fallacies
    state["current_step"] = "fallacies_done"
    return state


# 7. Evidence Verifier Agent
def evidence_verifier_node(state: DebateState) -> DebateState:
    print(f"--- [Agent 7: Evidence Verifier] ---")
    update_debate_status(state["debate_id"], "verifying_evidence")
    
    all_arguments = state["pro_arguments"] + state["con_arguments"]
    
    prompt = f"""Verify whether the cited evidence in the arguments actually exists and supports the claims.

Arguments to verify: {all_arguments}
Evidence database pool: {state['evidence']}

Label each claim with status: "supported", "partially supported", or "unsupported".
Explain the reasoning.

Return JSON only in this format:
{{
  "verifications": [
    {{
      "claim": "The argument claim that cited the evidence",
      "evidence_used": "The cited evidence from the argument",
      "status": "supported",
      "reasoning": "Reasoning..."
    }}
  ]
}}"""
    
    result = run_agent_prompt(prompt, "verifier", state["topic"])
    verifications = result.get("verifications", [])
    
    db_update_verifications(state["debate_id"], verifications)
    
    state["verifications"] = verifications
    state["current_step"] = "verifications_done"
    return state


# 8. Judge Agent
def judge_agent_node(state: DebateState) -> DebateState:
    print(f"--- [Agent 8: Judge Agent] ---")
    update_debate_status(state["debate_id"], "judging")
    
    prompt = f"""You are a professional debate judge.

Evaluate this complete debate round:
- Pro arguments: {state['pro_arguments']}
- Con arguments: {state['con_arguments']}
- Cross-examination rebuttals: {state['rebuttals']}
- Logic fallacies detected: {state['fallacies']}
- Evidence verifications: {state['verifications']}

Evaluate:
1. Argument strength
2. Evidence quality
3. Logical consistency
4. Rebuttal effectiveness

Assign scores out of 100 for Pro and Con. Determine the winner ("Pro", "Con", or "Tie"). Explain your decision.

Return JSON only in this format:
{{
  "winner": "Pro",
  "pro_score": 88,
  "con_score": 83,
  "decision_reasoning": "Explain decision..."
}}"""
    
    result = run_agent_prompt(prompt, "judge", state["topic"])
    winner = result.get("winner", "Tie")
    pro_score = float(result.get("pro_score", 85.0))
    con_score = float(result.get("con_score", 85.0))
    decision_reasoning = result.get("decision_reasoning", "The debate was highly contested.")
    
    db_update_judge(state["debate_id"], winner, pro_score, con_score, decision_reasoning)
    
    state["winner"] = winner
    state["pro_score"] = pro_score
    state["con_score"] = con_score
    state["decision_reasoning"] = decision_reasoning
    state["current_step"] = "judged"
    return state


# 9. Debate Report Generator Agent
def report_generator_node(state: DebateState) -> DebateState:
    print(f"--- [Agent 9: Debate Report Generator] ---")
    update_debate_status(state["debate_id"], "generating_report")
    
    prompt = f"""You are a debate report generator.

Generate a professional, highly structured debate report in Markdown format.
Use tables, headers, and bullet points.

Input Details:
- Topic: {state['topic']}
- Scope: {state['scope']}
- Pro Arguments: {state['pro_arguments']}
- Con Arguments: {state['con_arguments']}
- Rebuttals: {state['rebuttals']}
- Fallacies Found: {state['fallacies']}
- Evidence Verifications: {state['verifications']}
- Winner: {state['winner']}
- Pro Score: {state['pro_score']}
- Con Score: {state['con_score']}
- Decision Reasoning: {state['decision_reasoning']}

Include sections:
1. Executive Summary & Verdict (with Scorecard table)
2. Debate Scope & Dimensions
3. Opening Statements (Summarized or complete)
4. Pro vs Con Arguments (Compare claims, evidence, impact in a table or list)
5. Cross-Examination & Rebuttals (Challenging questions and rebuttals)
6. Fallacy & Evidence Verification Audit (List of logic flaws and citation audits)
7. Judge's Decision & Analysis

Return plain markdown text. Do not return JSON."""
    
    result = run_agent_prompt(prompt, "report", state["topic"], json_mode=False)
    report_markdown = result.get("text", "# Debate Report\n\nNo report generated.")
    
    db_update_report(state["debate_id"], state["winner"], report_markdown)
    
    state["report"] = report_markdown
    state["status"] = "completed"
    state["current_step"] = "completed"
    return state
