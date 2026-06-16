import os
import sys

# Add backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select
from backend.database.db import init_db, engine
from backend.database.models import Debate, Argument, Fallacy, Evidence, Rebuttal, Verification
from backend.agents.graph import run_debate_pipeline

def run_test():
    print("Initializing Database...")
    init_db()
    
    topic = "Should AI replace university exams?"
    print(f"Creating debate record for: '{topic}'...")
    
    with Session(engine) as session:
        # Clear previous debates to keep test clean
        session.exec(select(Debate)).all() # Force load / clean if we want, but let's just insert
        db_debate = Debate(
            topic=topic,
            status="pending"
        )
        session.add(db_debate)
        session.commit()
        session.refresh(db_debate)
        debate_id = db_debate.id
        print(f"Created Debate Record with ID: {debate_id}")
    
    print("\nStarting Debate Multi-Agent Pipeline...")
    try:
        final_state = run_debate_pipeline(debate_id, topic)
        print("\nDebate Pipeline Completed Successfully!")
    except Exception as e:
        print(f"\nDebate Pipeline Failed: {e}")
        sys.exit(1)
        
    print("\n--- Verifying Database Persisted Records ---")
    with Session(engine) as session:
        debate = session.get(Debate, debate_id)
        print(f"Debate: ID={debate.id}, Status={debate.status}, Winner={debate.winner}")
        print(f"Pro Opening: {debate.pro_opening[:60] if debate.pro_opening else 'None'}...")
        print(f"Con Opening: {debate.con_opening[:60] if debate.con_opening else 'None'}...")
        
        args = session.exec(select(Argument).where(Argument.debate_id == debate_id)).all()
        print(f"Arguments Saved: {len(args)}")
        for a in args:
            print(f"  [{a.side}] Claim: {a.claim} | Score: {a.score}")
            
        evidences = session.exec(select(Evidence).where(Evidence.debate_id == debate_id)).all()
        print(f"Evidence Saved: {len(evidences)}")
        for e in evidences:
            print(f"  Source: {e.source} | Confidence: {e.confidence}")
            
        rebuttals = session.exec(select(Rebuttal).where(Rebuttal.debate_id == debate_id)).all()
        print(f"Rebuttals Saved: {len(rebuttals)}")
        for r in rebuttals:
            print(f"  Rebuttal Claim: {r.claim}")
            
        fallacies = session.exec(select(Fallacy).where(Fallacy.debate_id == debate_id)).all()
        print(f"Fallacies Saved: {len(fallacies)}")
        for f in fallacies:
            print(f"  Fallacy: {f.type} | Severity: {f.severity} | Expl: {f.explanation[:50]}")
            
        verifications = session.exec(select(Verification).where(Verification.debate_id == debate_id)).all()
        print(f"Verifications Saved: {len(verifications)}")
        for v in verifications:
            print(f"  Verification: Status={v.status} | Claim={v.claim[:40]}")
            
        print("\nReport Preview:")
        print(debate.report[:300] if debate.report else "No Report Generated.")
        print("...")

if __name__ == "__main__":
    run_test()
