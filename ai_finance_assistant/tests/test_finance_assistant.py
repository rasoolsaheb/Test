from ai_finance_assistant.src.agents.base import AgentType
from ai_finance_assistant.src.core.models import FinanceRequest, UserProfile
from ai_finance_assistant.src.workflow.orchestrator import FinanceAssistantOrchestrator


def test_routes_queries_to_specialized_agents() -> None:
    assistant = FinanceAssistantOrchestrator.default()

    assert assistant.route("Can you review my portfolio allocation?") == AgentType.PORTFOLIO_ANALYSIS
    assert assistant.route("What is the market trend for this ticker?") == AgentType.MARKET_ANALYSIS
    assert assistant.route("Help me plan for retirement") == AgentType.GOAL_PLANNING
    assert assistant.route("Explain this Fed headline in the news") == AgentType.NEWS_SYNTHESIZER
    assert assistant.route("How are capital gains taxed?") == AgentType.TAX_EDUCATION
    assert assistant.route("What is an index fund?") == AgentType.FINANCE_QA


def test_answers_include_education_citations_and_disclaimers() -> None:
    assistant = FinanceAssistantOrchestrator.default()
    response = assistant.answer(
        FinanceRequest(
            "Can you review my portfolio?",
            UserProfile("Mina", "beginner", "conservative", "buy a home"),
            ("VOO", "BND"),
        )
    )

    assert response.agent_type == AgentType.PORTFOLIO_ANALYSIS.name
    assert "VOO, BND" in response.answer
    assert response.citations
    assert any("Educational information only" in disclaimer for disclaimer in response.disclaimers)


def test_market_agent_uses_available_quote_data() -> None:
    assistant = FinanceAssistantOrchestrator.default()
    response = assistant.answer(
        FinanceRequest("Give me a market price update", holdings=("AAPL",))
    )

    assert response.agent_type == AgentType.MARKET_ANALYSIS.name
    assert "AAPL $225.00" in response.answer
