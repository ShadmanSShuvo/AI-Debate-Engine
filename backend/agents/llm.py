import os
import json
import re
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

# Determine API keys
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

def get_llm_provider() -> str:
    if OPENAI_KEY:
        return "openai"
    elif GEMINI_KEY:
        return "gemini"
    else:
        return "mock"

def call_openai(prompt: str, json_mode: bool = False) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_KEY)
    
    kwargs = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
    }
    
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
        # Ensure the prompt mentions JSON
        if "json" not in prompt.lower():
            prompt += "\nReturn JSON only."
            kwargs["messages"] = [{"role": "user", "content": prompt}]
            
    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content

def call_gemini(prompt: str, json_mode: bool = False) -> str:
    from google import genai
    from google.genai import types
    
    client = genai.Client(api_key=GEMINI_KEY)
    
    config = types.GenerateContentConfig(
        temperature=0.3,
    )
    
    if json_mode:
        config.response_mime_type = "application/json"
        if "json" not in prompt.lower():
            prompt += "\nReturn JSON only."
            
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=config,
    )
    return response.text

def query_llm(prompt: str, json_mode: bool = False) -> str:
    provider = get_llm_provider()
    try:
        if provider == "openai":
            return call_openai(prompt, json_mode)
        elif provider == "gemini":
            return call_gemini(prompt, json_mode)
        else:
            raise ValueError("No API key provided.")
    except Exception as e:
        # If any API call fails, log and fallback to Mock
        print(f"LLM Provider {provider} failed: {e}. Falling back to Mock Engine.")
        return ""

# ==========================================
# Mock LLM Engine for Offline/Keyless Mode
# ==========================================

MOCK_DEBATES_DATA = {
    "exams": {
        "orchestrator": {
            "scope": ["Education Quality", "Assessment Fairness", "Practical Skills Evaluation", "Mental Health & Stress"],
            "neutral_framing": "The debate centers on whether traditional high-stakes university exams should be fully replaced by artificial intelligence-based adaptive assessments and continuous portfolio reviews."
        },
        "evidence": [
            {
                "source": "Harvard Graduate School of Education (2023)",
                "claim": "Traditional high-stakes exams fail to measure collaborative problem-solving and critical thinking skills required in modern workplaces.",
                "confidence": 0.89
            },
            {
                "source": "Journal of Educational Psychology (2022)",
                "claim": "Test anxiety affects up to 40% of university students, causing a significant disconnect between actual knowledge and exam performance.",
                "confidence": 0.85
            },
            {
                "source": "National Bureau of Economic Research (2024)",
                "claim": "AI-graded standardized assessments exhibit a 12% lower standard deviation in scoring discrepancy compared to human graders, but can inherit racial and socioeconomic grading biases present in training data.",
                "confidence": 0.91
            },
            {
                "source": "Global Education Tech Review (2023)",
                "claim": "Continuous AI-driven diagnostic tests help students address learning gaps in real-time, improving overall course completion rates by 18%.",
                "confidence": 0.82
            }
        ],
        "pro": {
            "arguments": [
                {
                    "claim": "AI assessments provide highly personalized, real-time diagnostic evaluation.",
                    "evidence": "Harvard Graduate School of Education (2023) and Global EdTech Review (2023) show traditional exams fail to measure actual workplace skills, whereas continuous AI diagnostics improve course completion by 18% and adapt to individual pace.",
                    "impact": "Shifting to AI examinations replaces arbitrary high-stakes testing with a continuous learning journey, preparing students for real-world application."
                },
                {
                    "claim": "Replacing exams with continuous AI reviews dramatically reduces test anxiety and increases fairness.",
                    "evidence": "As noted in the Journal of Educational Psychology (2022), test anxiety impairs performance for 40% of students. Continuous assessment neutralizes this single-day stress failure point.",
                    "impact": "Ensures academic credentials reflect true cognitive capability rather than stress tolerance, democratizing higher education."
                }
            ]
        },
        "con": {
            "arguments": [
                {
                    "claim": "Standardized exams maintain rigorous academic integrity and prevent widespread plagiarism.",
                    "evidence": "Traditional controlled exam environments verify authorship directly, which is critical in an era where generative AI allows students to easily fabricate portfolios and papers offline.",
                    "impact": "Exams secure the social credibility of university degrees. Without secure testing environments, credentials lose all market value."
                },
                {
                    "claim": "AI scoring engines inherit and entrench systematic training biases.",
                    "evidence": "The National Bureau of Economic Research (2024) indicates AI grading algorithms reproduce grading disparities present in historical human grading datasets.",
                    "impact": "Deploying AI as the final arbiter of student capability risk institutionalizing systemic discrimination under the guise of technological objectivity."
                }
            ]
        },
        "crossexam": {
            "rebuttals": [
                {
                    "target_argument": "AI assessments provide highly personalized, real-time diagnostic evaluation.",
                    "claim": "Personalization cannot replace rigorous, standardized benchmarks of technical competency.",
                    "question": "How does an adaptive AI prevent students from avoiding difficult but essential core concepts while still scoring highly?"
                },
                {
                    "target_argument": "Replacing exams with continuous AI reviews dramatically reduces test anxiety and increases fairness.",
                    "claim": "Continuous monitoring creates a panopticon effect that increases persistent, daily stress.",
                    "question": "If students know every interaction with the AI is logged and evaluated, won't that replace single-day test anxiety with chronic, term-long surveillance fatigue?"
                },
                {
                    "target_argument": "Standardized exams maintain rigorous academic integrity and prevent widespread plagiarism.",
                    "claim": "In-person controlled exams test rote memorization rather than actual capability.",
                    "question": "If high-stakes exams only prevent plagiarism by testing memory, aren't we valuing easily verified cheating prevention over authentic learning?"
                },
                {
                    "target_argument": "AI scoring engines inherit and entrench systematic training biases.",
                    "claim": "AI models can be audited, corrected, and de-biased far more transparently than human professors.",
                    "question": "While human grading biases remain private and unquantified, isn't code-level auditing of AI grading models a superior way to enforce systemic fairness?"
                }
            ]
        },
        "fallacy": [
            {
                "argument_claim": "AI assessments provide highly personalized, real-time diagnostic evaluation.",
                "fallacy": "Appeal to Authority",
                "severity": 0.45,
                "explanation": "The argument relies heavily on references to 'Harvard Graduate School' without explaining the specific mechanism by which the personalization occurs."
            },
            {
                "argument_claim": "Standardized exams maintain rigorous academic integrity and prevent widespread plagiarism.",
                "fallacy": "False Dilemma",
                "severity": 0.65,
                "explanation": "Presents a binary choice between high-stakes traditional exams and a total loss of credential value, ignoring hybrid options like proctored digital exams or oral presentations."
            }
        ],
        "verifier": [
            {
                "claim": "AI assessments provide personalized evaluations that improve completion rates by 18%.",
                "evidence_used": "Global Education Tech Review (2023) finding of 18% improvement.",
                "status": "supported",
                "reasoning": "The claim matches the source citation precisely."
            },
            {
                "claim": "Standardized exams are the only way to prevent widespread plagiarism in universities.",
                "evidence_used": "Claims about generative AI fabrication.",
                "status": "partially supported",
                "reasoning": "While generative AI makes cheating easier, the claim that traditional exams are the *only* solution is an overstatement not directly verified by empirical studies."
            }
        ],
        "judge": {
            "winner": "Con",
            "scores": {
                "pro": 84,
                "con": 88
            },
            "decision_reasoning": "The CON side successfully argued that AI grading engines inherit historical bias (citing NBER 2024) and that standardized environments are currently irreplaceable for verifying authorship in the generative AI era. While the PRO side presented excellent arguments on reducing test anxiety and improving learning diagnostics, they struggled to address the cross-examination query regarding the 'panopticon surveillance fatigue' of continuous AI tracking. Thus, the CON arguments on academic integrity and algorithmic bias carry more weight in this round."
        }
    }
}

def generate_mock_debate(topic: str, stage: str) -> Dict[str, Any]:
    # Normalize topic key
    topic_lower = topic.lower()
    is_exams = "exam" in topic_lower or "university" in topic_lower or "ai replace" in topic_lower
    
    # Use pre-cooked data for the exam topic
    if is_exams:
        data = MOCK_DEBATES_DATA["exams"]
        if stage in data:
            val = data[stage]
            if stage == "evidence" and isinstance(val, list):
                return {"evidence": val}
            if stage == "fallacy" and isinstance(val, list):
                return {"fallacies": val}
            if stage == "verifier" and isinstance(val, list):
                return {"verifications": val}
            return val
            
    # Dynamic Mock Engine for any other topic
    topic_clean = topic.strip().rstrip("?")
    
    if stage == "orchestrator":
        return {
            "scope": [f"{topic_clean} Feasibility", "Social Impact", "Ethical Implications", "Economic Impact"],
            "neutral_framing": f"This debate examines the multifaceted implications, costs, and benefits of: {topic_clean}."
        }
    elif stage == "evidence":
        return {
            "evidence": [
                {
                    "source": "Global Research Consortium (2024)",
                    "claim": f"Implementing changes regarding '{topic_clean}' yields positive outcomes in 62% of tested environments.",
                    "confidence": 0.87
                },
                {
                    "source": "Statistical Bureau of Analysis (2023)",
                    "claim": f"Over 55% of stakeholders report concerns regarding equity and security in implementation of '{topic_clean}'.",
                    "confidence": 0.81
                },
                {
                    "source": "Academic Journal of Ethics (2024)",
                    "claim": f"Unregulated implementation of '{topic_clean}' may lead to structural biases affecting marginalized groups.",
                    "confidence": 0.90
                }
            ]
        }
    elif stage == "pro":
        return {
            "arguments": [
                {
                    "claim": f"Advocating for {topic_clean} drives innovation and efficiency.",
                    "evidence": "Global Research Consortium (2024) reports 62% positive outcomes in pilot programs.",
                    "impact": "Fosters progress and adapts modern systems to contemporary demands."
                },
                {
                    "claim": f"Embracing this proposition democratizes access and lowers barriers.",
                    "evidence": "Provides flexible solutions that bypass rigid institutional bottlenecks.",
                    "impact": "Creates a more inclusive system for all participants involved."
                }
            ]
        }
    elif stage == "con":
        return {
            "arguments": [
                {
                    "claim": f"The proposed change poses critical security and integrity risks.",
                    "evidence": "Statistical Bureau of Analysis (2023) highlights that 55% of stakeholders report equity and security concerns.",
                    "impact": "Undermines trust and stability, potentially causing systemic failure."
                },
                {
                    "claim": f"Algorithmic and structural biases exacerbate existing inequalities.",
                    "evidence": "The Academic Journal of Ethics (2024) indicates a high risk of structural bias affecting marginalized populations.",
                    "impact": "Excludes vulnerable groups, compounding systemic discrimination under a technical facade."
                }
            ]
        }
    elif stage == "crossexam":
        return {
            "rebuttals": [
                {
                    "target_argument_claim": f"Advocating for {topic_clean} drives innovation and efficiency.",
                    "claim": "Innovation should not come at the expense of safety and security.",
                    "question": "How do we mitigate the 55% security concern rate highlighted by stakeholders?"
                },
                {
                    "target_argument_claim": f"The proposed change poses critical security and integrity risks.",
                    "claim": "Risks can be managed with modern oversight and robust controls.",
                    "question": "Is it reasonable to stall progress entirely due to security concerns that can be systematically patched?"
                }
            ]
        }
    elif stage == "fallacy":
        return {
            "fallacies": [
                {
                    "argument_claim": f"Advocating for {topic_clean} drives innovation and efficiency.",
                    "fallacy": "Hasty Generalization",
                    "severity": 0.55,
                    "explanation": "Assuming pilot program results generalized to all environments without qualification."
                }
            ]
        }
    elif stage == "verifier":
        return {
            "verifications": [
                {
                    "claim": f"Implementing {topic_clean} yields positive outcomes in 62% of environments.",
                    "evidence_used": "Global Research Consortium (2024)",
                    "status": "supported",
                    "reasoning": "The percentage and citation match the source evidence directly."
                }
            ]
        }
    elif stage == "judge":
        return {
            "winner": "Tie",
            "scores": {
                "pro": 85,
                "con": 85
            },
            "decision_reasoning": f"This debate on '{topic_clean}' was highly balanced. The PRO side established compelling points on innovation and democratized access, backed by a 62% positive outcome metric. However, the CON side successfully countered by outlining the 55% security and equity risks. Because both sides failed to fully resolve the core conflict between progress and security in cross-examination, this debate is declared a Tie with equal scores of 85."
        }
    elif stage == "report":
        # Generate a beautiful report based on the topic
        is_exams = "exam" in topic.lower() or "university" in topic.lower() or "replace" in topic.lower()
        if is_exams:
            return {
                "text": """# AI Debate Engine - Comprehensive Report

## Executive Summary & Verdict
This debate analyzed the motion: **"Should AI replace university exams?"**
After reviewing the arguments, cross-examinations, evidence reliability, and logical structure, the Judge has rendered a final decision.

| Dimension | Pro Score | Con Score | Verdict |
| :--- | :---: | :---: | :---: |
| **Argument Strength** | 85 | 88 | Con +3 |
| **Evidence Quality** | 80 | 85 | Con +5 |
| **Logical Consistency** | 82 | 87 | Con +5 |
| **Rebuttal Effectiveness** | 84 | 82 | Pro +2 |
| **Final Score** | **84** | **88** | **CON WINS** |

---

## Debate Scope & Dimensions
1. **Education Quality**: Impact on student learning outcomes and academic rigor.
2. **Assessment Fairness**: Reducing testing anxiety vs. addressing grading bias.
3. **Practical Skills**: Ability to measure real-world workplace preparedness.
4. **Academic Integrity**: Preventing plagiarism in the age of generative AI.

---

## Opening Statements
* **PRO**: "We must move beyond outdated, stress-inducing rote memorization. AI-driven continuous assessments offer a personalized learning path that measures true capabilities and helps students succeed in real-time."
* **CON**: "High-stakes standardized exams are the anchor of academic credibility. In an era where generative AI can write any essay or generate any portfolio code, controlled testing environments are the only way to verify true student authorship and protect the value of a degree."

---

## Pro vs Con Arguments

### Pro Arguments
1. **Personalized Evaluation**: Continuous adaptive testing improves learning outcomes. (Cited Harvard EdTech 2023, Global EdTech 2023).
2. **Fairness & Stress Reduction**: Eliminates high-stakes single-day testing anxiety which affects 40% of students. (Cited J. Ed. Psych 2022).

### Con Arguments
1. **Academic Integrity**: Verify student authorship directly in controlled environments. (Cited Generative AI rise).
2. **Systemic Grading Bias**: AI grading models reproduce historical grading disparities. (Cited NBER 2024).

---

## Cross-Examination & Rebuttals
* **Con Rebuttal to Pro**: Adaptive systems can let students bypass difficult core competencies.
* **Pro Rebuttal to Con**: Auditing AI grading models is far more transparent than auditing private human bias.

---

## Fallacy & Evidence Verification Audit
* **Pro Appeal to Authority** (Severity: 0.45): Relies on 'Harvard Graduate School' name dropping.
* **Con False Dilemma** (Severity: 0.65): Presents a binary choice between high-stakes testing and complete academic failure.
* **Evidence Citation Verification**:
  * Harvard Graduate School (2023): **SUPPORTED**
  * NBER (2024): **SUPPORTED**

---

## Judge's Decision & Analysis
The debate is awarded to the **CON** side. While the Pro side presented powerful arguments on reducing testing anxiety and continuous improvement, they failed to answer the integrity challenge: how can universities protect credentials from generative AI plagiarism without controlled exam conditions? Furthermore, the Con side's warnings about AI grading engines replicating systemic bias are backed by strong empirical evidence.
"""
            }
        else:
            return {
                "text": f"""# AI Debate Engine - Comprehensive Report

## Executive Summary & Verdict
This debate analyzed the motion: **"{topic}"**
After reviewing the arguments, cross-examinations, evidence reliability, and logical structure, the Judge has rendered a final decision.

| Dimension | Pro Score | Con Score | Verdict |
| :--- | :---: | :---: | :---: |
| **Argument Strength** | 85 | 85 | Tie |
| **Evidence Quality** | 85 | 85 | Tie |
| **Logical Consistency** | 85 | 85 | Tie |
| **Final Score** | **85** | **85** | **TIE** |

---

## Debate Scope & Dimensions
- Feasibility & Operational Cost
- Ethical Considerations
- Social and Cultural Impact
- Future Scalability

---

## Opening Statements
* **PRO**: "Embracing this change will drive innovation and lower barriers, creating a more inclusive and efficient system."
* **CON**: "We must approach this change with caution. The security, equity, and stability risks are too significant to ignore."

---

## Judge's Decision & Analysis
This debate on **"{topic}"** ended in a **Tie (85 - 85)**. Both sides demonstrated exceptional reasoning. The Pro side presented compelling benefits regarding innovation, while the Con side successfully raised critical warnings regarding safety, equity, and security risks.
"""
            }
    return {}

def run_agent_prompt(prompt: str, stage: str, topic: str, json_mode: bool = True) -> Dict[str, Any]:
    # Check if we should use Mock LLM
    provider = get_llm_provider()
    
    if provider == "mock":
        return generate_mock_debate(topic, stage)
        
    # Real LLM execution
    raw_response = query_llm(prompt, json_mode)
    
    # In case the real LLM returns empty or fails, fallback to Mock
    if not raw_response:
        print(f"Empty LLM response for {stage}. Using mock fallback.")
        return generate_mock_debate(topic, stage)
        
    if not json_mode:
        return {"text": raw_response}
        
    try:
        # Strip code blocks if any
        cleaned = raw_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        return json.loads(cleaned)
    except Exception as e:
        print(f"Failed to parse JSON for {stage} (Raw: {raw_response[:200]}): {e}. Using mock fallback.")
        return generate_mock_debate(topic, stage)
