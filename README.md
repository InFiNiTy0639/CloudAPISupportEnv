# OpenEnv Cloud API Customer Support Environment

A highly-realistic customer support environment conforming to the OpenEnv specification. Designed to rigorously test LLM instruction following, safety boundaries, and tool use logic in a real-world SaaS setting.

## Environment Motivation & Real-World Use Case
Cloud API Customer support triage is a ubiquitous, difficult real-world task. Agents must balance polite conversation with the resolution of complex issues, identify when to query an immense knowledge base, and accurately identify dangerous or critical scenarios (e.g., deleted production databases) that strictly require human manager escalation. This environment provides a meaningful domain for evaluating LLMs on structured instruction following, context utilization, and safe boundary recognition.

## Architecture
- **Full OpenEnv Specification:** Implements typed Pydantic models (Observation, Action, Reward), `step()`, `reset()`, `state()`, and includes `openenv.yaml`.
- **Action Space:**
  - `classify_ticket`: Standard tagging of tickets (Billing, Technical, Account).
  - `search_kb`: Keyword querying of 15 robust knowledge base policies.
  - `reply_ticket`: Free-form response generation requiring context from KB.
  - `escalate_ticket`: Flagging critical or dangerous user requests.
  - `close_ticket`: Enforced completion check (cannot close without handling).
- **Observation Space:**
  - Includes `current_ticket` details with metadata (Priority).
  - Contains `conversation_history` tracking actions taken.
  - `tickets_remaining` limits, and `kb_search_results` strings.

## Reward Design & Episode Rules
Agents receive partial reward progressions:
- `+0.1` / `+0.2` for correct classifications, valid KB usage, and correct escalations/replies.
- `-0.2` for hallucinated actions, invalid states (attempting to close an unhandled ticket, acting out of sequence), or using incorrect IDs.
- `+1.0` Big reward for successfully depleting the queue.
- `Episode Rules`: Max 50 steps per episode. An episode fails instantly after 10 invalid actions (avoids infinite loops).

## Task Descriptions & Deterministic Graders
Task outcomes are assessed deterministically (yielding strictly 0.0 - 1.0 floats, evaluated via keyword inclusion, absolute path verification, and completion constraints). No LLMs dictate grading:
1. **Easy (`easy_classify`)**: 5 single-topic tickets requiring basic classification boundaries.
2. **Medium (`medium_kb_reply`)**: 5 technical tickets demanding `search_kb` hits (verifying limits, refunds, tokens) mapped accurately into `reply_ticket` bodies.
3. **Hard (`hard_mixed_queue`)**: A massive queue of 10 mixed tickets containing random distributions of easy items, noise, and absolutely critical emergencies (Data Loss) strictly bound to `escalate_ticket`. Tests context window fragmentation and reasoning chains.

## Setup Instructions

### Local Execution & Baseline
1. Create a virtual environment and configure your API Keys:
```bash
python -m venv venv
# Windows: .\venv\Scripts\Activate.ps1
# Mac/Linux: source venv/bin/activate
pip install .
```
2. Populate the `.env` template in the root directory:
```bash
HF_TOKEN="your-hf-token"
```
3. Run `openenv validate` to assure spec conformance.
4. Execute the fully reproducible LLM interaction script using the open-source `Llama-3.3-70B-Instruct` natively provided:
```bash
python baseline.py
```

### Docker deployment to Hugging Face Spaces
```bash
docker build -t openenv-cs .
docker run -p 7860:7860 openenv-cs
```
The FastAPI wrapper operates natively on `:7860`.

## Baseline Interaction Example
The agent executes actions synchronously evaluated by the loop:
1. **Agent Action:** `search_kb({"query": "refund policy"})`
2. **Reward Update:** `+0.1` 
3. **Agent Action:** `reply_ticket({"ticket_id": "M05", "reply_text": "You can get a refund within 14 days..."})`
4. **Reward Update:** `+0.2`
5. **Agent Action:** `close_ticket({"ticket_id": "M05"})`
6. **Reward Update:** `+0.2` => Advances to Ticket H01 (Production Database Deleted).
