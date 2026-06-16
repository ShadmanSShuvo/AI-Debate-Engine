# AI Debate Engine: Multi-Agent Reasoning System

An agentic AI multi-agent debate platform built to demonstrate advanced LLM orchestration, live web retrieval (RAG), fallacy detection, citation audits, and automated judging. 

Unlike standard linear chatbots, this application deploys a network of 9 collaborating agents managed via a state graph machine to research, debate, audit, and judge complex topics.

---

## 🏛️ System Architecture

```text
               User Topic
                   │
                   ▼
         [Debate Orchestrator] (Agent 1)
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
[Research Agent] [Pro Agent] [Con Agent]
(Agent 2 - RAG)   (Agent 3)   (Agent 4)
       │           │           │
       ▼           ▼           ▼
   Evidence    Arguments   Arguments
   Database
       │
       ▼
[Cross-Examination Agent] (Agent 5)
       │
       ▼
 [Fallacy Detection Agent] (Agent 6)
       │
       ▼
   [Evidence Verifier] (Agent 7)
       │
       ▼
     [Judge Agent] (Agent 8)
       │
       ▼
[Debate Report Generator] (Agent 9)
```

1. **Debate Orchestrator**: Analyzes the topic, generates neutral framing, and identifies 3-5 key dimensions.
2. **Research Agent**: Utilizes DuckDuckGo web search to scrape live studies, statistics, and expert opinions (RAG).
3. **Pro Agent**: Formulates a persuasive opening statement and structured arguments defending the motion.
4. **Con Agent**: Opposes the motion with contrasting arguments and citations.
5. **Cross-Examination Agent**: Audits arguments from both sides, identifying weak assertions, and generates rebuttals.
6. **Fallacy Detector**: Evaluates the debate transcript for 6 logical fallacies (Strawman, Ad Hominem, Slippery Slope, False Dilemma, Appeal to Authority, Hasty Generalization) and computes severity scores.
7. **Evidence Verifier**: Checks whether cited arguments align with retrieved facts, labeling them as *Supported*, *Partially Supported*, or *Unsupported*.
8. **Judge Agent**: Scores both sides out of 100 on argument strength, evidence quality, logical consistency, and rebuttal success. Declares a winner.
9. **Debate Report Generator**: Compiles an executive Markdown report detailing the verdict and summaries.

---

## 💻 Tech Stack

* **Backend**: FastAPI, SQLModel (SQLAlchemy-based ORM), LangGraph (State Graph Engine).
* **Database**: SQLite (default, zero-configuration) or PostgreSQL.
* **LLMs**: OpenAI API (`gpt-4o-mini`), Google Gemini API (`gemini-2.5-flash`), or **Offline Mock Engine** (automatically activates if no API keys are provided to ensure immediate local testing).
* **Retrieval**: DuckDuckGo search integration.
* **Frontend**: Next.js (App Router), TypeScript, Vanilla CSS (Premium space-dark theme with glassmorphic cards, timelines, and dynamic widgets).

---

## 📂 Project Structure

```text
├── backend/
│   ├── agents/
│   │   ├── state.py            # TypedDict state structure
│   │   ├── llm.py              # LLM wrapper (OpenAI / Gemini / Mock)
│   │   ├── debate_agents.py    # The 9 agent node definitions & DB saves
│   │   └── graph.py            # LangGraph pipeline wiring
│   ├── database/
│   │   ├── models.py           # SQLModel database tables
│   │   └── db.py               # Database manager (SQLite foreign keys)
│   ├── main.py                 # FastAPI router and endpoints
│   ├── requirements.txt        # Backend dependencies
│   ├── test_debate.py          # Standalone verification script
│   └── .env.example            # Environment template
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── globals.css     # Dark mode CSS token styling
│   │   │   ├── layout.tsx      # Global frame shell
│   │   │   └── page.tsx        # Dashboard and debate dashboard
│   ├── package.json
│   └── tsconfig.json
```

---

## 🚀 How to Run

### 1. Prerequisites
- Python 3.10+
- Node.js 18+

---

### 2. Run the Backend (FastAPI)

1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. (Optional) Configure environment variables:
   Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```
   Add your API keys (`OPENAI_API_KEY` or `GEMINI_API_KEY`) to run real LLM queries. **If left blank, the system will run in offline Mock mode, allowing you to test the entire visual dashboard immediately without any API cost.**
5. Run the API server:
   ```bash
   uvicorn main:app --port 8000 --reload
   ```
   The backend API will be available at `http://localhost:8000`.

---

### 3. Run the Frontend (Next.js)

1. Navigate to the `frontend/` directory:
   ```bash
   cd ../frontend
   ```
2. Install Node packages:
   ```bash
   npm install
   ```
3. Run the Next.js development server:
   ```bash
   npm run dev
   ```
4. Open [http://localhost:3000](http://localhost:3000) in your web browser.

---

## ⚖️ Database Management
The application manages 6 linked tables:
- **`debates`**: Logs debate details, winner status, scores, neutral framing, and the final Markdown report.
- **`arguments`**: Holds the structured Pro/Con claims, citations, and impact statements.
- **`evidence_items`**: Stores fetched RAG facts, sources, and confidence scores.
- **`rebuttals`**: Captures cross-examination objections and challenging questions.
- **`fallacies`**: Houses logic professor ratings and explanations.
- **`verifications`**: Archives citation validity checks (supported/partially/unsupported).

---

## 🔍 Running Standalone Tests
You can run a local test script in the backend directory to check database insertion and LangGraph node transit:
```bash
cd backend
source .venv/bin/activate
python test_debate.py
```
This initializes the SQLite database (`debate.db`), executes a synchronous debate round for *"Should AI replace university exams?"*, and displays a summary printout of all persisted database tables.
