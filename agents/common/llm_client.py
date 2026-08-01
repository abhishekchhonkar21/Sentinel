# Shared LLM client for Narrator, Critic, and eval baseline.
# Groq primary, Gemini fallback; cache responses in MongoDB keyed by prompt hash (rate-limit mitigation).
# Optional Ollama offline fallback for local iteration.
