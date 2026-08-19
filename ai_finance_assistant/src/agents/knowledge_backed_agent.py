from __future__ import annotations

from ai_finance_assistant.src.agents.base import AgentType, FinanceAgent
from ai_finance_assistant.src.core.models import FinanceRequest, FinanceResponse
from ai_finance_assistant.src.data.market_data import MarketDataProvider
from ai_finance_assistant.src.rag.knowledge_base import Article, KnowledgeBase


class KnowledgeBackedAgent(FinanceAgent):
    """Specialized deterministic agent grounded in retrieved education content."""

    STANDARD_DISCLAIMERS = (
        "Educational information only; not personalized investment, tax, or legal advice.",
        "Consider consulting a qualified professional before making financial decisions.",
    )

    def __init__(
        self,
        agent_type: AgentType,
        knowledge_base: KnowledgeBase,
        market_data_provider: MarketDataProvider,
    ) -> None:
        self.agent_type = agent_type
        self._knowledge_base = knowledge_base
        self._market_data_provider = market_data_provider

    def respond(self, request: FinanceRequest) -> FinanceResponse:
        articles = self._knowledge_base.search(request.query, self.agent_type)
        answer = self._answer_for(request, articles)
        return FinanceResponse(
            agent_type=self.agent_type.name,
            answer=answer,
            citations=tuple(article.source for article in articles),
            disclaimers=self.STANDARD_DISCLAIMERS,
        )

    def _answer_for(self, request: FinanceRequest, articles: tuple[Article, ...]) -> str:
        match self.agent_type:
            case AgentType.PORTFOLIO_ANALYSIS:
                return self._portfolio_answer(request, articles[0])
            case AgentType.MARKET_ANALYSIS:
                return self._market_answer(request, articles[0])
            case AgentType.GOAL_PLANNING:
                return self._goal_answer(request, articles[0])
            case AgentType.NEWS_SYNTHESIZER:
                return self._news_answer(articles[0])
            case AgentType.TAX_EDUCATION:
                return self._tax_answer(articles[0])
            case AgentType.FINANCE_QA:
                return self._education_answer(request, articles[0])

    @staticmethod
    def _education_answer(request: FinanceRequest, article: Article) -> str:
        return (
            f"For a {request.user_profile.knowledge_level} investor, start with the core idea: "
            f"{article.summary} Ask follow-up questions until each term is clear."
        )

    @staticmethod
    def _portfolio_answer(request: FinanceRequest, article: Article) -> str:
        if not request.holdings:
            return (
                "Share ticker symbols or fund names to review concentration, diversification, and risk. "
                f"{article.summary}"
            )
        holdings = ", ".join(request.holdings)
        return (
            f"Portfolio review for {holdings}: compare each holding's role, overlap, costs, "
            f"and risk against your {request.user_profile.risk_tolerance} risk tolerance. {article.summary}"
        )

    def _market_answer(self, request: FinanceRequest, article: Article) -> str:
        quote_summary = "No live quote was available, so use cached or external market data before acting."
        for holding in request.holdings:
            quote = self._market_data_provider.quote(holding)
            if quote:
                quote_summary = (
                    f"{quote.symbol} ${quote.price:.2f} ({quote.change_percent}%, {quote.as_of})"
                )
                break
        return f"{quote_summary}. Context: {article.summary}"

    @staticmethod
    def _goal_answer(request: FinanceRequest, article: Article) -> str:
        return (
            f"Goal planning for {request.user_profile.goal}: define the target amount, time horizon, "
            f"contributions, risk capacity, and review cadence. {article.summary}"
        )

    @staticmethod
    def _news_answer(article: Article) -> str:
        return (
            "News summary framework: separate facts from forecasts, identify affected sectors, "
            f"and connect the item to long-term goals. {article.summary}"
        )

    @staticmethod
    def _tax_answer(article: Article) -> str:
        return (
            "Tax education: distinguish taxable brokerage accounts from tax-advantaged retirement "
            f"accounts, contribution rules, withdrawals, and recordkeeping. {article.summary}"
        )
