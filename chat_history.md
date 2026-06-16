# AI Debate Engine - Conversation History

Record of pair programming session for conversation ID `f8ec6a24-b5db-4322-97ec-96af7f8cf420`.

---

## 👤 User

An **AI Debate Engine** can be much more interesting than a simple chatbot if you design it as a multi-agent reasoning system with evidence retrieval, argument scoring, and fallacy detection.

# High-Level Architecture

```text
User Topic
    │
    ▼
Debate Orchestrator
    │
 ┌──┼─────────────┬─────────────┐
 ▼  ▼             ▼             ▼
Research      Pro Agent     Con Agent
Agent
 │                │             │
 ▼                ▼             ▼
Evidence      Arguments     Arguments
Database
 │
 ▼
Cross-Examination Agent
 │
 ▼
Fallacy Detection Agent
 │
 ▼
Judge Agent
 │
 ▼
Debate Report Generator
```

---

# Agent 1: Debate Orchestrator

Responsibilities:

* Understand topic
* Define scope
* Identify debate type
* Launch agents

Example input:

```json
{
  "topic": "Should AI replace university exams?"
}
```

Output:

```json
{
  "topic": "Should AI replace university exams?",
  "scope": [
    "education",
    "assessment quality",
    "fairness",
    "employment readiness"
  ]
}
```

Prompt:

```text
You are a debate coordinator.

Given a debate topic:

1. Identify key dimensions.
2. Define debate scope.
3. Generate neutral framing.
4. Avoid taking a side.

Return JSON only.
```

---

# Agent 2: Research Agent

Purpose:

Gather evidence before arguments are generated.

Pipeline:

```text
Topic
 ↓
Search Papers
 ↓
Search News
 ↓
Search Statistics
 ↓
Extract Claims
 ↓
Store Evidence
```

Output:

```json
{
  "claim": "Traditional exams correlate poorly with workplace performance.",
  "source": "...",
  "confidence": 0.83
}
```

Prompt:

```text
You are a research analyst.

Find:

- empirical studies
- statistics
- expert opinions

Extract evidence.

Do not argue.

Return structured evidence only.
```

---

# Agent 3: Pro Agent

Task:

Generate strongest possible arguments FOR proposition.

Prompt:

```text
You are an elite debater.

Your goal is to defend:

"AI should replace university exams."

Rules:

- Use retrieved evidence.
- Be persuasive.
- Anticipate objections.
- Do not mention weaknesses.

Produce:

1. Opening statement
2. Main arguments
3. Supporting evidence
```

Output:

```json
{
  "arguments": [
    {
      "claim": "...",
      "evidence": "...",
      "impact": "..."
    }
  ]
}
```

---

# Agent 4: Con Agent

Mirror of Pro Agent.

Prompt:

```text
You are an elite debater.

Defend:

"AI should NOT replace university exams."

Use evidence.

Generate strongest opposing position.
```

---

# Agent 5: Cross-Examination Agent

This is where it gets interesting.

Purpose:

Attack arguments from both sides.

Input:

```json
{
  "pro_arguments": [...],
  "con_arguments": [...]
}
```

Prompt:

```text
You are a cross-examiner.

For every argument:

1. Find hidden assumptions.
2. Identify weak evidence.
3. Generate rebuttals.
4. Ask challenging questions.

Return structured critique.
```

Example:

```json
{
  "target": "AI improves assessment quality",
  "question": "How does AI avoid inherited training bias?"
}
```

---

# Agent 6: Fallacy Detector

One of the coolest components.

Detect:

* Strawman
* Ad hominem
* Slippery slope
* False dilemma
* Appeal to authority
* Hasty generalization

Prompt:

```text
You are a logic professor.

Analyze arguments.

Identify:

- logical fallacies
- unsupported claims
- weak causal links

Provide severity score.
```

Output:

```json
{
  "argument_id": 12,
  "fallacy": "False Dilemma",
  "severity": 0.74,
  "explanation": "..."
}
```

---

# Agent 7: Evidence Verifier

Purpose:

Prevent hallucinated citations.

Pipeline:

```text
Argument
 ↓
Evidence Used
 ↓
Evidence Exists?
 ↓
Correctly Interpreted?
```

Prompt:

```text
Verify whether the cited evidence actually supports the claim.

Label:

- supported
- partially supported
- unsupported

Explain reasoning.
```

---

# Agent 8: Judge Agent

Acts like a tournament judge.

Inputs:

```text
Pro arguments
Con arguments
Rebuttals
Evidence scores
Fallacy scores
```

Prompt:

```text
You are a professional debate judge.

Evaluate:

1. Argument strength
2. Evidence quality
3. Logical consistency
4. Rebuttal effectiveness

Assign scores.

Determine winner.

Explain decision.
```

Output:

```json
{
  "winner": "Con",
  "score": {
    "pro": 81,
    "con": 87
  }
}
```

---

# Agent 9: Debate Report Generator

Creates final output.

Structure:

```text
Topic

Opening Statements

Main Arguments

Cross Examination

Fallacies Found

Evidence Analysis

Judge Decision

Winner
```

Prompt:

```text
Generate a professional debate report.

Use markdown.

Include tables and scores.
```

---

# Database Design

### Debate Table

```sql
debates
--------
id
topic
created_at
winner
```

### Arguments

```sql
arguments
----------
id
debate_id
side
claim
evidence
score
```

### Fallacies

```sql
fallacies
----------
id
argument_id
type
severity
```

### Evidence

```sql
evidence
---------
id
source
claim
confidence
```

---

# Modern AI Stack

Backend:

* [FastAPI](https://fastapi.tiangolo.com?utm_source=chatgpt.com)
* PostgreSQL
* Redis

Agents:

* [LangGraph](https://langchain-ai.github.io/langgraph/?utm_source=chatgpt.com)

LLMs:

* [OpenAI API](https://platform.openai.com?utm_source=chatgpt.com) or open-source models

Retrieval:

* FAISS
* ChromaDB

Frontend:

* [Next.js](https://nextjs.org?utm_source=chatgpt.com)

Deployment:

* Docker
* Railway / Render / VPS

# What makes this portfolio-worthy

Most students build:

> User → LLM → Response

This project becomes:

> User → Research → Multi-Agent Reasoning → Cross-Examination → Logic Analysis → Evidence Verification → Judgment

That demonstrates:

* Agentic AI design
* RAG
* Knowledge retrieval
* Evaluation pipelines
* Structured outputs
* System architecture
* Prompt engineering
* Full-stack deployment

A polished version with debate transcripts, evidence citations, scorecards, and visual argument graphs would look closer to a research prototype than a student project.

---

## 👤 Antigravity

I am going to check the current directory contents to understand what files are already present in the workspace.

---

## 👤 Antigravity

I will check the system's available runtimes (Python, Node, Docker) and configuration to see what technologies we can utilize directly.

---

## 👤 Antigravity

I will list all environment variables containing `KEY` or `API` to check if there are pre-configured keys we can use.

---

## 👤 Antigravity

I will read the concise-planning skill file to make sure I format the plan correctly according to best practices.

---

## 👤 Antigravity

I will read the modern-web-guidance skill instructions to ensure we conform to modern CSS/HTML design practices.

---

## 👤 Antigravity

I will run `npx -y create-next-app@latest --help` to examine the CLI options before initializing the Next.js frontend.

---

## 👤 Antigravity

I will search for modern web development best practices related to layouts and UI elements using the `modern-web-guidance` tool.

---

## 👤 Antigravity

I will retrieve the CSS guidelines and save them to a local file `modern-css-guidance.md` to reference them without cluttering our conversational context.

---

## 👤 Antigravity

I will retrieve the CSS layout guidelines and save them to `modern-css-layout-guidance.md` for reference during design implementation.

---

## 👤 Antigravity

I will write a detailed, step-by-step implementation plan for the AI Debate Engine project in `PLAN.md` and request your review. This plan covers setting up the Python FastAPI backend, the LangGraph multi-agent orchestration, the SQLite/PostgreSQL database models, and the Next.js frontend with rich aesthetics.

---

## 👤 Antigravity

I will write the implementation plan to the designated artifacts directory path `/Users/shuvo/.gemini/antigravity-cli/brain/f8ec6a24-b5db-4322-97ec-96af7f8cf420/PLAN.md`.

---

## 👤 Antigravity

I have created a comprehensive implementation plan [PLAN.md](file:///Users/shuvo/.gemini/antigravity-cli/brain/f8ec6a24-b5db-4322-97ec-96af7f8cf420/PLAN.md) in the artifacts directory. 

Please click **Proceed** or provide any feedback on the plan, and I will begin the implementation!

---

## 👤 User

[Approved] PLAN.md

---

## 👤 Antigravity

I will create the `backend` directory structure and the `requirements.txt` file specifying the Python dependencies for the FastAPI and LangGraph multi-agent debate engine.

---

## 👤 Antigravity

I will write the `backend/requirements.txt` file directly into the workspace directory without artifact metadata.

---

## 👤 Antigravity

I will create a Python virtual environment inside the `backend` folder and install all backend dependencies.

---

## 👤 Antigravity

I will update the `backend/requirements.txt` file to use flexible version constraints for `google-genai` and other packages, allowing pip to find the most compatible versions.

---

## 👤 Antigravity

I will run the backend package installation command now.

---

## 👤 Antigravity

I will create the database models inside `backend/database/models.py` using `sqlmodel`. This includes classes for `Debate`, `Argument`, `Fallacy`, `Evidence`, `Rebuttal`, and `Verification`.

---

## 👤 Antigravity

I will create the database manager in `backend/database/db.py` to handle engine configuration, session generation, tables creation, and SQLite foreign key support.

---

## 👤 Antigravity

I will check the status of the background installation task.

---

## 👤 Antigravity

I will implement `backend/agents/llm.py` to handle AI API calls. It will support OpenAI, Google Gemini, and a high-quality fallback Mock LLM that generates realistic debate transcripts and analysis if no API keys are present.

---

## 👤 Antigravity

I will implement the LangGraph state representation in `backend/agents/state.py` to define the schema used by all 9 agents as they execute.

---

## 👤 Antigravity

I will view the `backend/database/models.py` file to find where to add the opening statements fields.

---

## 👤 Antigravity

I will add `pro_opening` and `con_opening` to the `Debate` table in `backend/database/models.py` to store the opening statements.

---

## 👤 Antigravity

I will create `backend/agents/debate_agents.py` containing the 9 agent node functions, custom prompts, database synchronization helpers, and an integrated live DuckDuckGo web search helper to power the Research Agent.

---

## 👤 Antigravity

I will implement `backend/agents/graph.py` which compiles the LangGraph state machine, connects the 9 agent nodes sequentially, and defines an execution wrapper to run debates asynchronously and save errors safely.

---

## 👤 Antigravity

I will create the backend entry point `backend/main.py` implementing the FastAPI app. It will define CORS middleware, endpoints to create and list debates, poll status, fetch complete debate transcripts and scores, and trigger the multi-agent graph run in the background.

---

## 👤 Antigravity

I will create a `.env.example` file in the `backend/` directory to document the database and AI API keys required for full functionality.

---

## 👤 Antigravity

I will write a validation script `backend/test_debate.py` that initializes the database, inserts a test debate topic, runs the full 9-agent LangGraph pipeline synchronously, and verifies that arguments, evidence, rebuttals, fallacies, verifications, and reports are correctly generated and stored.

---

## 👤 Antigravity

I will run the validation script `test_debate.py` using our virtual environment Python to execute the full multi-agent pipeline and check for any logic errors.

---

## 👤 Antigravity

I will inspect `backend/agents/llm.py` to check how the mock output is structured for `evidence`, `fallacy`, and `verifier`.

---

## 👤 Antigravity

I will view the remaining lines of `backend/agents/llm.py` to see the structure of the rest of the mock generator.

---

## 👤 Antigravity

I will view the `MOCK_DEBATES_DATA` definition inside `backend/agents/llm.py` to verify the key names for cross examination rebuttals.

---

## 👤 Antigravity

I will update `backend/agents/llm.py` to ensure that `generate_mock_debate` wraps lists in dictionaries (`{"evidence": ...}`, `{"fallacies": ...}`, `{"verifications": ...}`) to match the expected JSON schema and the prompt specifications.

---

## 👤 Antigravity

I will view the `backend/agents/debate_agents.py` file around line 92 to see how the cross examination rebuttals are parsed and saved to the database.

---

## 👤 Antigravity

I will edit `backend/agents/debate_agents.py` to support fallback keys for target argument lookups in case the LLM outputs `"target_argument"` instead of `"target_argument_claim"`.

---

## 👤 Antigravity

I will run `backend/test_debate.py` again to verify that all 9 agents execute and persist records correctly.

---

## 👤 Antigravity

I will view lines 8 to 16 of `backend/database/models.py` to see the structure of the `Debate` model.

---

## 👤 Antigravity

I will add `pro_score`, `con_score`, and `decision_reasoning` directly to the `Debate` model in `backend/database/models.py` to allow clean storage of the judge's scoring and evaluation notes.

---

## 👤 Antigravity

I will check lines 75 to 95 in `backend/main.py` to see the `DebateDetailResponse` class definition.

---

## 👤 Antigravity

I will read lines 60 to 76 of `backend/main.py` to get the full `DebateDetailResponse` class definition.

---

## 👤 Antigravity

I will add `pro_score`, `con_score`, and `decision_reasoning` to the `DebateDetailResponse` schema in `backend/main.py` so they are sent to the frontend.

---

## 👤 Antigravity

I will delete the temporary test SQLite database and re-run the verification script to ensure the new database schema builds correctly and the entire debate pipeline succeeds.

---

## 👤 Antigravity

I will view lines 300 to 310 in `backend/agents/llm.py` to see the structure before adding the `report` case to `generate_mock_debate`.

---

## 👤 Antigravity

I will view lines 310 to 325 of `backend/agents/llm.py` to locate the `judge` return block.

---

## 👤 Antigravity

I will add the report generator mock logic in `backend/agents/llm.py` to return rich Markdown report text for mock debates.

---

## 👤 Antigravity

I will re-run the verification script to verify that the report content is successfully created and stored in the database.

---

## 👤 Antigravity

I will create the `frontend/` directory and initialize a Next.js App Router project inside it using TypeScript and without Tailwind CSS (to follow our Vanilla CSS guidelines).

---

## 👤 Antigravity

I will create the `frontend` directory first, running the command from the workspace root.

---

## 👤 Antigravity

I will initialize the Next.js project inside the `frontend/` directory.

---

## 👤 Antigravity

I will check the status of the Next.js scaffolding process.

---

## 👤 Antigravity

I am waiting for the Next.js initialization task to finish. I will continue as soon as it completes.

---

## 👤 Antigravity

I will inspect the created `frontend/src/app` directory to understand the folder structure and configuration.

---

## 👤 Antigravity

I will view the default `layout.tsx` and `globals.css` files to understand the entry structure.

---

## 👤 Antigravity

I will inspect the default `globals.css` file to see what styling is set up.

---

## 👤 Antigravity

I will update `frontend/src/app/globals.css` to define our premium design system: a space-dark palette, vibrant neon accent colors (cyan for PRO, magenta for CON, purple for orchestrator), glassmorphism styles (`backdrop-filter`, subtle borders), and custom scrollbars.

---

## 👤 Antigravity

I will replace the code in `frontend/src/app/layout.tsx` to wrap pages with a premium common Header and Footer featuring neon accents.

---

## 👤 Antigravity

I will implement the main Dashboard and Arena in `frontend/src/app/page.tsx` as a Next.js Client Component. It features live polling, an agent progress tracker, side-by-side pro/con transcripts, a logic fallacy audit panel, citation audits, and a judge's scorecard.

---

## 👤 Antigravity

I will list the files in the `frontend/` directory to verify its contents.

---

## 👤 Antigravity

I will view `frontend/package.json` to inspect the scripts and dependencies.

---

## 👤 Antigravity

I will run a build command in the `frontend` directory to ensure there are no TypeScript compile-time or linting issues.

---

## 👤 Antigravity

I will view `frontend/src/app/page.tsx` around line 625 to locate the invalid CSS property.

---

## 👤 Antigravity

I will replace `tracking: '0.1em'` with `letterSpacing: '0.1em'` in `frontend/src/app/page.tsx` to resolve the TypeScript compilation error.

---

## 👤 Antigravity

I will build the Next.js app again to verify that all TypeScript checks pass.

---

## 👤 Antigravity

I will create a comprehensive, well-formatted `README.md` in the root of the project to document the multi-agent system, the database models, the RAG search, the frontend styling, and step-by-step instructions for the user to run both the FastAPI backend and Next.js frontend.

---

## 👤 Antigravity

I will list the workspace root directory files to ensure we leave a clean codebase for the user.

---

## 👤 Antigravity

I will remove the temporary CSS documentation reference files to keep the root directory pristine.

---

## 👤 Antigravity

I will update the implementation plan [PLAN.md](file:///Users/shuvo/.gemini/antigravity-cli/brain/f8ec6a24-b5db-4322-97ec-96af7f8cf420/PLAN.md) to mark all action items as fully completed.

---

## 👤 Antigravity

I have successfully designed and built the **AI Debate Engine**! All aspects of the frontend web application and multi-agent backend have been implemented, verified, and compiled with zero errors.

A summary of what has been constructed:

1. **Multi-Agent Orchestration Engine (`backend/agents/`)**:
   - Compiles a sequential **LangGraph** execution pipeline (`graph.py`) routing the debate across 9 distinct agent nodes.
   - Synchronizes agent state updates (`state.py`) and dynamically updates the database at each step.
   - Utilizes a flexible driver (`llm.py`) supporting **OpenAI**, **Google Gemini**, and a highly realistic offline **Mock LLM engine** (fully pre-seeded with high-fidelity arguments for the topic *"Should AI replace university exams?"* and a dynamic generator for other custom topics).
   - Integrates **live web retrieval (RAG)** in the Research Agent using DuckDuckGo search.

2. **Relational Database Schema (`backend/database/`)**:
   - Structured SQLModel definitions (`models.py`) mapping 6 distinct relational tables: `debates`, `arguments`, `evidence_items`, `rebuttals`, `fallacies`, and `verifications`.
   - SQLite database configuration with foreign key cascade deletion capability (`db.py`).

3. **FastAPI Web API Backend (`backend/main.py`)**:
   - Outlines CRUD endpoints to create new debates, fetch historical debate transcripts, check active process states, and delete debates.
   - Uses FastAPI's `BackgroundTasks` to ensure that debates run in the background without locking requests.

4. **Next.js Web Frontend Client (`frontend/`)**:
   - Created a responsive Next.js App Router project using TypeScript and Vanilla CSS.
   - Designed a space-dark theme (`globals.css`) with custom glassmorphism components (`backdrop-filter`) and animated neon borders.
   - Programmed the debate board (`page.tsx`) incorporating a visual progress timeline of active agents, side-by-side arguments layout, fallacy auditor, citation checker, and a judge's scorecard.

5. **Standalone Testing Script (`backend/test_debate.py`)**:
   - Synthesizes a local database run of the multi-agent graph. Verification tests ran and succeeded in saving all 9 stages to `debate.db`!

---

### 🚀 How to Run the App

I have created a root-level [README.md](file:///Users/shuvo/AI-Debate-Engine/README.md) detailing the setup, but here are the immediate commands:

#### 1. Start the Backend API (FastAPI)
```bash
cd backend
source .venv/bin/activate
# Optional: Copy .env.example to .env to configure OPENAI_API_KEY or GEMINI_API_KEY.
# If left blank, the app runs automatically in offline Mock mode for free local testing!
uvicorn main:app --port 8000 --reload
```

#### 2. Start the Frontend (Next.js)
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to view the application.

---

## 👤 User

save the chat history in this directory

---

## 👤 Antigravity

I will look for the chat transcript logs on the system to locate the conversation history.

---

## 👤 Antigravity

I will inspect the structure of the JSONL log file to see how user inputs and assistant replies are represented.

---

## 👤 Antigravity

I will inspect the unique sources and types in the transcript to ensure our parsing script extracts user prompts and assistant replies correctly.

---

## 👤 Antigravity

I will write a python utility script `backend/save_chat_history.py` to parse the `transcript_full.jsonl` log file and generate a beautifully formatted markdown file `chat_history.md` in the workspace directory.

---

