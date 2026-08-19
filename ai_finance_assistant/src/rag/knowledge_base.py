from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


@dataclass(frozen=True)
class Article:
    title: str
    category: str
    summary: str
    source: str


class KnowledgeBase:
    """Small in-memory retriever that mimics RAG semantics for the prototype."""

    def __init__(self, articles: list[Article]) -> None:
        self._articles = tuple(articles)

    @classmethod
    def default(cls) -> "KnowledgeBase":
        return cls(
            [
                Article("Diversification basics", "portfolio", "Diversification spreads money across assets so one holding has less impact on the whole portfolio.", "Internal education: diversification"),
                Article("Emergency funds before investing", "planning", "Many beginners build a cash buffer before taking market risk so short-term needs are not funded by selling investments.", "Internal education: planning"),
                Article("Index funds", "education", "Broad index funds are pooled investments designed to track a market benchmark at relatively low cost.", "Internal education: funds"),
                Article("Tax-advantaged accounts", "tax", "Retirement accounts may defer or exempt taxes, but rules differ by account type and jurisdiction.", "Internal education: tax"),
                Article("Market volatility", "market", "Prices fluctuate with earnings expectations, interest rates, sentiment, and macroeconomic news.", "Internal education: markets"),
                Article("News context", "news", "Financial headlines should be interpreted alongside long-term goals, valuation, and risk rather than in isolation.", "Internal education: news"),
            ]
        )

    def search(self, query: str, category: StrEnum | str, limit: int = 2) -> tuple[Article, ...]:
        tokens = {token for token in query.lower().split() if token}
        target_category = str(category)
        ranked = sorted(
            self._articles,
            key=lambda article: self._score(article, tokens, target_category),
            reverse=True,
        )
        return tuple(ranked[: max(1, limit)])

    @staticmethod
    def _score(article: Article, tokens: set[str], target_category: str) -> int:
        score = 4 if article.category == target_category else 0
        searchable_text = f"{article.title} {article.summary}".lower()
        return score + sum(1 for token in tokens if token in searchable_text)
