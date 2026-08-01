# Narrator agent FastAPI app entry point.
# Expose: POST /narrate { ranked_hypotheses, evidence_bundle } → IncidentReport.
# Thin LLM layer (Groq Llama 3.1 / Gemini Flash): structured prompt → JSON matching IncidentReport schema.
# Validate output with Pydantic; reject and retry on malformed responses.
