from __future__ import annotations

from enum import StrEnum
from typing import Protocol

from ai_finance_assistant.src.core.models import FinanceRequest, FinanceResponse


class AgentType(StrEnum):
    FINANCE_QA = "education"
    PORTFOLIO_ANALYSIS = "portfolio"
    MARKET_ANALYSIS = "market"
    GOAL_PLANNING = "planning"
    NEWS_SYNTHESIZER = "news"
    TAX_EDUCATION = "tax"


class FinanceAgent(Protocol):
    agent_type: AgentType

    def respond(self, request: FinanceRequest) -> FinanceResponse:
        """Generate a response for a routed request."""
