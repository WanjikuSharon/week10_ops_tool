"""
app.py
------
VitalAsset Equipment Risk Assistant — a Streamlit RAG chatbot that lets
biomedical engineers and hospital administrators ask natural-language
questions about medical equipment utilization and maintenance risk
across Kenyan county hospitals, instead of manually scanning spreadsheets.

Run: streamlit run app.py
"""

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from rag_utils import EquipmentRAG, ask_llm, get_active_provider

load_dotenv()

DATA_PATH = Path(__file__).parent / "data" / "equipment_risk_data.csv"

st.set_page_config(page_title="VitalAsset Equipment Risk Assistant", page_icon="🩺", layout="wide")


@st.cache_resource
def load_rag(path: str) -> EquipmentRAG:
    return EquipmentRAG(path)


def main():
    st.title("🩺 VitalAsset Equipment Risk Assistant")
    st.caption(
        "Chat with your medical equipment utilization & maintenance-risk data. "
        "Ask about specific hospitals, counties, equipment types, or which units "
        "need attention first."
    )

    provider = get_active_provider()
    if provider == "none":
        st.error(
            "No API key found. Copy `.env.example` to `.env` and set either "
            "`GROQ_API_KEY` (free — no card needed, get one at console.groq.com) "
            "or `ANTHROPIC_API_KEY` (requires prepaid credits), then restart the app."
        )
        st.stop()

    if not DATA_PATH.exists():
        st.error(f"Dataset not found at {DATA_PATH}. Run `python generate_data.py` first.")
        st.stop()

    rag = load_rag(str(DATA_PATH))
    stats = rag.summary_stats()

    with st.sidebar:
        st.caption(f"LLM provider: **{provider.title()}**")
        st.subheader("Fleet Snapshot")
        c1, c2 = st.columns(2)
        c1.metric("Total equipment", stats["total_equipment"])
        c2.metric("Hospitals", stats["hospitals"])
        c1.metric("Critical risk", stats["critical_count"])
        c2.metric("High risk", stats["high_count"])
        st.metric("Counties covered", stats["counties"])

        st.divider()
        st.subheader("Try asking")
        st.markdown(
            "- Which equipment at Nakuru Level 5 Hospital is highest risk?\n"
            "- List all Critical risk dialysis machines.\n"
            "- What's overdue for maintenance in Kisumu?\n"
            "- Summarize risk across Mombasa county.\n"
            "- Which equipment type has the most Critical units?"
        )

        st.divider()
        if st.button("Clear chat"):
            st.session_state.messages = []
            st.rerun()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("sources"):
                with st.expander(f"Sources ({len(msg['sources'])} records)"):
                    for d in msg["sources"]:
                        st.markdown(f"- **{d.row['equipment_id']}** — {d.row['equipment_type']} @ "
                                    f"{d.row['hospital_name']} — risk {d.row['risk_score']} "
                                    f"({d.row['risk_level']})")

    if question := st.chat_input("Ask about equipment risk, e.g. 'What's Critical in Kiambu?'"):
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching equipment records..."):
                docs = rag.retrieve(question, top_k=6)
                history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages[:-1]
                    if m["role"] in ("user", "assistant")
                ]
                try:
                    answer = ask_llm(question, docs, history)
                except Exception:
                    answer = ""

            st.markdown(answer)
            if docs:
                with st.expander(f"Sources ({len(docs)} records)"):
                    for d in docs:
                        st.markdown(f"- **{d.row['equipment_id']}** — {d.row['equipment_type']} @ "
                                    f"{d.row['hospital_name']} — risk {d.row['risk_score']} "
                                    f"({d.row['risk_level']})")

        st.session_state.messages.append({"role": "assistant", "content": answer, "sources": docs})


if __name__ == "__main__":
    main()
