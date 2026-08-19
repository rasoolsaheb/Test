from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class UserProfile:
    """Minimal session profile used to personalize education level and risk framing."""

    name: str = "Investor"
    knowledge_level: str = "beginner"
    risk_tolerance: str = "moderate"
    goal: str = "learn investing fundamentals"


@dataclass(frozen=True)
class FinanceRequest:
    """User query plus optional profile and portfolio context."""

    query: str
    user_profile: UserProfile = field(default_factory=UserProfile)
    holdings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.query or not self.query.strip():
            raise ValueError("query is required")
        object.__setattr__(self, "holdings", tuple(self.holdings))


@dataclass(frozen=True)
class FinanceResponse:
    """Standard response contract returned by all finance agents."""

    agent_type: str
    answer: str
    citations: tuple[str, ...]
    disclaimers: tuple[str, ...]
