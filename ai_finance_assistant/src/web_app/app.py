from __future__ import annotations

from ai_finance_assistant.src.core.models import FinanceRequest
from ai_finance_assistant.src.workflow.orchestrator import FinanceAssistantOrchestrator


def answer_cli_query(query: str) -> str:
    """Small UI-facing adapter that can be reused by Streamlit, Gradio, or a CLI."""
    assistant = FinanceAssistantOrchestrator.default()
    response = assistant.answer(FinanceRequest(query=query))
    disclaimer_text = " ".join(response.disclaimers)
    return f"{response.answer}\n\nSources: {', '.join(response.citations)}\nDisclaimer: {disclaimer_text}"
