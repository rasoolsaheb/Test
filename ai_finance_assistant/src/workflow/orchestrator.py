from __future__ import annotations

from ai_finance_assistant.src.agents.base import AgentType, FinanceAgent
from ai_finance_assistant.src.agents.knowledge_backed_agent import KnowledgeBackedAgent
from ai_finance_assistant.src.core.models import FinanceRequest, FinanceResponse
from ai_finance_assistant.src.data.market_data import InMemoryMarketDataProvider, MarketDataProvider
from ai_finance_assistant.src.rag.knowledge_base import KnowledgeBase


class FinanceAssistantOrchestrator:
    """Routes each user query to the most relevant specialized finance agent."""

    def __init__(self, agents: dict[AgentType, FinanceAgent]) -> None:
        self._agents = dict(agents)

    @classmethod
    def default(cls) -> "FinanceAssistantOrchestrator":
        knowledge_base = KnowledgeBase.default()
        market_data_provider: MarketDataProvider = InMemoryMarketDataProvider()
        return cls(
            {
                agent_type: KnowledgeBackedAgent(
                    agent_type, knowledge_base, market_data_provider
                )
                for agent_type in AgentType
            }
        )

    def answer(self, request: FinanceRequest) -> FinanceResponse:
        agent_type = self.route(request.query)
        return self._agents[agent_type].respond(request)

    @staticmethod
    def route(query: str) -> AgentType:
        normalized = query.lower()
        if _contains_any(normalized, ("portfolio", "holdings", "allocation", "diversif")):
            return AgentType.PORTFOLIO_ANALYSIS
        if _contains_any(normalized, ("market", "stock quote", "ticker", "price", "trend")):
            return AgentType.MARKET_ANALYSIS
        if _contains_any(normalized, ("goal", "retire", "college", "save", "plan")):
            return AgentType.GOAL_PLANNING
        if _contains_any(normalized, ("news", "headline", "fed", "earnings")):
            return AgentType.NEWS_SYNTHESIZER
        if _contains_any(normalized, ("tax", "ira", "401k", "roth", "capital gain")):
            return AgentType.TAX_EDUCATION
        return AgentType.FINANCE_QA


def _contains_any(value: str, needles: tuple[str, ...]) -> bool:
    return any(needle in value for needle in needles)
