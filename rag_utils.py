"""
rag_utils.py
------------
Core RAG (Retrieval-Augmented Generation) logic for the VitalAsset
Equipment Risk Assistant.

Retrieval: TF-IDF + cosine similarity over per-equipment text "documents"
built from the CSV. Lightweight, no external embedding API needed, and
fast enough to rebuild on every Streamlit run for a few hundred rows.

Generation: pluggable between two providers, called with the retrieved
rows as context so answers are grounded in the actual dataset instead of
the model's general knowledge.
  - Groq (free tier, no credit card) via its OpenAI-compatible endpoint
  - Anthropic Claude (paid, requires prepaid credits)
Whichever API key is present in .env is used automatically; Groq is
checked first since it's free.
"""

import os
from dataclasses import dataclass

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class RetrievedDoc:
    row: dict
    score: float
    text: str


def row_to_document(row: dict) -> str:
    """Turn one equipment record into a natural-language chunk for retrieval."""
    return (
        f"Equipment {row['equipment_id']} is a {row['equipment_type']} located at "
        f"{row['hospital_name']} in {row['county']} county. "
        f"Installed on {row['install_date']}. Last maintenance was on "
        f"{row['last_maintenance_date']} ({row['days_since_maintenance']} days ago). "
        f"Utilization is {row['utilization_pct_of_rated_life']}% of rated life "
        f"({row['usage_unit']}). Sensor readings: temperature "
        f"{row['sensor_temp_c']}°C, vibration {row['sensor_vibration_mm_s']} mm/s. "
        f"Current risk score is {row['risk_score']}/100, classified as "
        f"{row['risk_level']} risk, with predicted failure in "
        f"{row['predicted_days_to_failure']} days. "
        f"Maintenance notes: {row['maintenance_notes']}"
    )


class EquipmentRAG:
    def __init__(self, csv_path: str):
        self.df = pd.read_csv(csv_path)
        self.documents = [row_to_document(r) for r in self.df.to_dict("records")]
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.doc_matrix = self.vectorizer.fit_transform(self.documents)

    def retrieve(self, query: str, top_k: int = 6) -> list[RetrievedDoc]:
        """Hybrid retrieval: TF-IDF similarity for topical relevance, boosted
        by exact substring matches on hospital/county/equipment_type/risk_level
        so questions like 'highest risk at Nakuru Level 5' correctly surface
        that hospital's own highest-risk records instead of just anything
        textually similar to the word 'risk'."""
        query_lower = query.lower()
        query_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(query_vec, self.doc_matrix)[0]

        field_boost = []
        for _, row in self.df.iterrows():
            boost = 0.0
            for field in ("hospital_name", "county", "equipment_type", "risk_level", "equipment_id"):
                value = str(row[field]).lower()
                if value and value in query_lower:
                    boost += 0.5
            field_boost.append(boost)

        combined = sims + field_boost
        wants_highest = any(kw in query_lower for kw in ("highest", "worst", "most urgent", "top risk", "most critical"))
        if wants_highest:
            # Among the field-matched rows, prioritize by risk_score too.
            risk_norm = (self.df["risk_score"] / 100.0).to_numpy()
            combined = combined + (risk_norm * (combined > 0))

        top_idx = combined.argsort()[::-1][:top_k]
        return [
            RetrievedDoc(row=self.df.iloc[i].to_dict(), score=float(combined[i]), text=self.documents[i])
            for i in top_idx
            if combined[i] > 0
        ]

    def summary_stats(self) -> dict:
        return {
            "total_equipment": len(self.df),
            "critical_count": int((self.df["risk_level"] == "Critical").sum()),
            "high_count": int((self.df["risk_level"] == "High").sum()),
            "counties": self.df["county"].nunique(),
            "hospitals": self.df["hospital_name"].nunique(),
        }


SYSTEM_PROMPT = """You are the VitalAsset Equipment Risk Assistant, an operational \
support tool for biomedical engineers and hospital administrators managing \
medical equipment across Kenyan county hospitals.

You will be given a user question and a set of retrieved equipment records \
as context. Answer ONLY using the provided context. If the context doesn't \
contain enough information to answer, say so clearly instead of guessing.

Be concise and operational: prioritize what a biomedical engineer or admin \
would need to act on (which equipment, where, how urgent, what to do next). \
When relevant, reference specific equipment IDs, hospitals, and risk scores \
from the context."""


def build_context_block(docs: list[RetrievedDoc]) -> str:
    if not docs:
        return "No matching equipment records were found in the dataset."
    parts = [f"[Record {i+1}] {d.text}" for i, d in enumerate(docs)]
    return "\n\n".join(parts)


def get_active_provider() -> str:
    """Groq checked first (free, no card needed); falls back to Anthropic."""
    if os.environ.get("GROQ_API_KEY"):
        return "groq"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    return "none"


def _ask_groq(question: str, context_block: str, history: list[dict]) -> str:
    # Groq exposes an OpenAI-compatible /v1 endpoint, so the standard
    # openai SDK works here — just pointed at Groq's base_url with a
    # Groq key. No separate SDK needed.
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1",
    )
    user_message = f"Retrieved equipment records:\n\n{context_block}\n\nUser question: {question}"
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history + [
        {"role": "user", "content": user_message}
    ]
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=800,
        messages=messages,
    )
    return response.choices[0].message.content


def _ask_anthropic(question: str, context_block: str, history: list[dict]) -> str:
    from anthropic import Anthropic

    # Some API keys (e.g. ones created outside a specific Workspace in the
    # Console) aren't scoped to a workspace and need the workspace ID sent
    # explicitly as a header. Set ANTHROPIC_WORKSPACE_ID in .env if you hit
    # a "not scoped to a workspace" 400 error and can't regenerate the key.
    workspace_id = os.environ.get("ANTHROPIC_WORKSPACE_ID")
    extra_headers = {"anthropic-workspace-id": workspace_id} if workspace_id else None

    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    user_message = f"Retrieved equipment records:\n\n{context_block}\n\nUser question: {question}"
    messages = history + [{"role": "user", "content": user_message}]
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=800,
        system=SYSTEM_PROMPT,
        messages=messages,
        extra_headers=extra_headers,
    )
    return response.content[0].text


def ask_llm(question: str, context_docs: list[RetrievedDoc], history: list[dict]) -> str:
    provider = get_active_provider()
    if provider == "none":
        raise RuntimeError(
            "No API key found. Copy .env.example to .env and set either "
            "GROQ_API_KEY (free, get one at console.groq.com) or "
            "ANTHROPIC_API_KEY (requires prepaid credits)."
        )
    context_block = build_context_block(context_docs)
    if provider == "groq":
        return _ask_groq(question, context_block, history)
    return _ask_anthropic(question, context_block, history)


# Kept as an alias so existing imports (e.g. `from rag_utils import ask_claude`)
# keep working even though generation is now provider-agnostic.
ask_claude = ask_llm
