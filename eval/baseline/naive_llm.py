"""Naive baseline — dump logs/metrics into LLM with no agent pipeline."""

from sentinel_core.adapters.llm.llm_factory import build_llm_provider


class NaiveLLMBaseline:
    def __init__(self) -> None:
        self._llm = build_llm_provider()

    async def diagnose(self, *, logs: list[str], metrics: dict) -> str:
        return await self._llm.complete_text(
            system_prompt="You are an SRE.",
            user_prompt=f"What's wrong and why?\nLogs: {logs}\nMetrics: {metrics}",
        )
