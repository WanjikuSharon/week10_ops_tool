# VitalAsset Equipment Risk Assistant

A Streamlit RAG (Retrieval-Augmented Generation) chatbot that lets
biomedical engineers and hospital administrators ask plain-language
questions about medical equipment utilization and maintenance risk across
Kenyan county hospitals — instead of manually scanning spreadsheets or
waiting on a report.

Built as part of the [VitalAsset / Team Vita Analytics capstone]
(medical equipment utilization & maintenance risk monitoring for Kenyan
county hospitals).

## The problem

Hospital biomedical engineering teams typically track equipment condition
in spreadsheets that grow to hundreds of rows across multiple facilities.
Finding "which dialysis machines are overdue for maintenance in Kisumu"
or "what's our highest-risk equipment this week" means manually filtering
and sorting a spreadsheet — slow, error-prone, and not something you can
hand to a non-technical administrator.

## What this tool does

- Loads an equipment risk dataset (equipment type, hospital, county,
  install/maintenance dates, sensor readings, composite risk score).
- Lets users ask free-text questions in a chat interface.
- Retrieves the most relevant equipment records using a hybrid TF-IDF +
  field-matching + risk-ranking retrieval strategy.
- Sends the retrieved records as grounding context to Claude, which
  answers using only that data (not general knowledge) — reducing
  hallucination risk for an operational safety context.
- Shows the source records behind every answer so users can verify it.
- Displays a live fleet-wide risk snapshot in the sidebar (total
  equipment, Critical/High counts, hospitals, counties).

## Setup

```bash
git clone <this-repo>
cd week10_ops_tool
pip install -r requirements.txt

cp .env.example .env
# then edit .env and add your real ANTHROPIC_API_KEY

python generate_data.py   # generates data/equipment_risk_data.csv
streamlit run app.py
```

The app will refuse to start (with a clear error message) if
`ANTHROPIC_API_KEY` is missing — no secrets are hardcoded anywhere in the
codebase.

## Using your own data

Swap `data/equipment_risk_data.csv` for a real export as long as it has
the same columns (see `generate_data.py` for the schema). Nothing else in
`rag_utils.py` or `app.py` needs to change.

## Project structure

```
week10_ops_tool/
├── app.py                  # Streamlit chat UI
├── rag_utils.py             # Retrieval (TF-IDF hybrid) + generation (Claude API)
├── generate_data.py         # Synthetic dataset generator
├── data/
│   └── equipment_risk_data.csv
├── requirements.txt
├── .env.example
├── .gitignore
├── PROMPTS.md                # Vibe-coding prompt log
└── README.md
```

## Example questions

- "Which equipment at Nakuru Level 5 Hospital is highest risk?"
- "List all Critical risk dialysis machines."
- "What's overdue for maintenance in Kisumu?"
- "Summarize risk across Mombasa county."
- "Which equipment type has the most Critical units?"

## Tech stack

- **Streamlit** — chat UI
- **pandas / scikit-learn** — data handling and TF-IDF retrieval
- **Anthropic Claude API** — grounded answer generation
- **python-dotenv** — secrets management via `.env` (never committed)

## AI-assisted development

This tool was built primarily using Claude as a coding assistant. See
[`PROMPTS.md`](./PROMPTS.md) for the key prompts used at each stage
(scoping, data generation, retrieval, generation, UI, security review,
and testing).
