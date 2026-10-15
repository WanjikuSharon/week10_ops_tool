# PROMPTS.md — Vibe Coding Workflow

This tool was built primarily using Claude (Anthropic) as the AI coding
assistant. Below are the key prompts used to generate and refine the code,
in the order they were used, with a short note on what each produced or
fixed.

## 1. Scoping the tool

> "I need to build a week10_ops_tool for a course assignment. Options are
> an automation script, a Streamlit chatbot/RAG app over operational data,
> or an enhanced dashboard. I'm a Data Engineer on a capstone project
> called VitalAsset — an AI-based medical equipment utilization and
> maintenance risk monitoring system for Kenyan county hospitals. Help me
> pick a direction and scope it."

→ Landed on a Streamlit RAG chatbot over equipment risk data, since it
doubles as a demo-able artifact for the capstone pitch.

## 2. Synthetic dataset generation

> "I don't have my real dataset ready yet. Generate a realistic synthetic
> equipment risk dataset in Python that mirrors what a Kenya Health
> Facility Census + C-MAPSS-style degradation dataset would look like:
> multiple equipment types (dialysis, ventilators, monitors, etc.), Kenyan
> counties/hospitals, install and maintenance dates, sensor readings
> (temperature, vibration), a composite risk score, and a risk level
> (Low/Medium/High/Critical). Write it as a standalone generate_data.py
> script so I can swap in my real data later without touching the app."

→ Produced `generate_data.py`, which writes `data/equipment_risk_data.csv`.

## 3. RAG retrieval layer

> "Build the retrieval half of a RAG pipeline in Python over this CSV.
> Turn each row into a natural-language document, use TF-IDF + cosine
> similarity for retrieval (no external embedding API needed — keep it
> lightweight), and return the top-k matching rows with their similarity
> scores. Put this in a separate rag_utils.py module."

→ Produced the initial `EquipmentRAG` class and `row_to_document()`.

## 4. Fixing retrieval quality

> "I tested it with 'Which equipment at Nakuru Level 5 Hospital is highest
> risk?' and it returned Low/Medium risk items instead of the actual
> highest-risk ones at that hospital — pure TF-IDF doesn't understand
> 'highest'. Improve retrieve() with a hybrid approach: boost rows that
> exactly match hospital/county/equipment_type/risk_level mentioned in the
> query, and when the query implies ranking ('highest', 'most critical',
> 'worst'), factor in the actual risk_score too."

→ Produced the hybrid scoring logic in `retrieve()`. Re-tested and
confirmed it now correctly surfaces the hospital's own highest-risk
equipment first.

## 5. Generation layer (Claude API call)

> "Now write the generation half: a function that takes the user's
> question, the retrieved records, and the chat history, and calls the
> Anthropic API with a system prompt that tells it to answer only from the
> provided context and to be concise and operational — this is for
> biomedical engineers and hospital admins deciding what to act on."

→ Produced `ask_claude()` and the `SYSTEM_PROMPT` in `rag_utils.py`.

## 6. Streamlit chat UI

> "Build the Streamlit app: a chat interface using st.chat_message and
> st.chat_input, a sidebar with fleet-wide risk stats (total equipment,
> critical/high counts, counties, hospitals) and example questions, source
> records shown in an expander under each answer, and a clear-chat button.
> Load the API key from a .env file via python-dotenv and fail gracefully
> with a clear error if it's missing, instead of crashing."

→ Produced `app.py`.

## 7. Security pass

> "Review this project for hardcoded secrets or anything that shouldn't be
> committed, and set up proper .env handling with a .env.example template
> and a .gitignore."

→ Produced `.env.example` and `.gitignore`; confirmed no API keys or
credentials appear anywhere in `app.py` or `rag_utils.py`.

## 8. Testing

> "Help me smoke-test the retrieval pipeline without needing a live API
> key, so I can confirm the dataset loads, stats are correct, and
> retrieval returns sensible results before I wire up the LLM call."

→ Ran a standalone script importing `EquipmentRAG` directly, confirmed
250 rows loaded, summary stats were correct, and retrieval (before and
after the hybrid fix) returned the expected rows.

---

**Note on workflow:** every module (data generation, retrieval, generation,
UI, security) was scoped, generated, tested, and iterated on individually
rather than generating the whole app in one shot — this made it much
easier to catch and fix the retrieval-ranking bug in step 4 before it was
buried inside a larger file.
