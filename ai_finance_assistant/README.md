# AI Finance Assistant

A dependency-light Python prototype for a multi-agent financial education assistant. It validates routing, retrieval-grounded responses, market-data abstraction, and compliance messaging before adding production LLM, vector database, and live quote integrations.

## Structure

```text
ai_finance_assistant/
├── src/
│   ├── agents/
│   ├── core/
│   ├── data/
│   ├── rag/
│   ├── web_app/
│   ├── utils/
│   └── workflow/
├── tests/
├── config.yaml
├── requirements.txt
└── README.md
```

## Implemented Components

- `src.workflow.FinanceAssistantOrchestrator` routes user questions to one of six specialized domains.
- `src.agents.KnowledgeBackedAgent` grounds deterministic responses in the in-memory knowledge base and includes source citations.
- `src.data.MarketDataProvider` defines the quote-provider boundary; `InMemoryMarketDataProvider` supplies deterministic sample quotes.
- `src.core` contains immutable request, response, and user profile models.
- `src.web_app` contains an adapter that can be reused by Streamlit, Gradio, or a CLI.

## Run Tests

```bash
python -m pytest ai_finance_assistant/tests
```

## Next Steps

- Replace `KnowledgeBase.default()` with FAISS, Chroma, or Pinecone retrieval.
- Replace the in-memory quote provider with Alpha Vantage or yFinance plus caching and backoff.
- Wrap each agent with LangGraph or CrewAI for production multi-agent orchestration.
- Build a Streamlit, Gradio, or React interface that persists profiles and conversation history.
