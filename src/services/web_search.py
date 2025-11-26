"""Web search + OpenAI summarization pipeline with observability."""

from __future__ import annotations

import requests
from openai import OpenAI
from opentelemetry import trace

from config import get_settings
from observability.metrics import (
    LLM_REQUEST_LATENCY,
    TOTAL_PROMPT_TOKENS,
    TOTAL_COMPLETION_TOKENS,
    TOTAL_COST_USD,
    UNANSWERABLE_QUERY_COUNTER,
)

# Model pricing per 1K tokens (USD)
MODEL_PRICING = {
    "gpt-4o-mini": {"prompt": 0.00015, "completion": 0.0006},
}


def estimate_llm_cost_usd(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Estimate LLM cost in USD based on token usage and model pricing."""
    pricing = MODEL_PRICING.get(model, MODEL_PRICING["gpt-4o-mini"])
    return ((prompt_tokens / 1000.0) * pricing["prompt"]) + ((completion_tokens / 1000.0) * pricing["completion"])


def web_search_and_summarize(query: str) -> str:
    """Perform a web search and use an LLM (OpenAI by default) to summarize."""

    tracer = trace.get_tracer(__name__)
    settings = get_settings()
    client = OpenAI(api_key=settings.llm_api_key or None)

    # Wrap the entire operation in a span so downstream calls nest nicely.
    with tracer.start_as_current_span("web_search_and_summarize") as span:
        span.set_attribute("search.query", query)

        # Perform a real web search using a simple API (DuckDuckGo Instant Answer API is free)
        try:
            # Using DuckDuckGo Instant Answer API (no key required)
            resp = requests.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json"},
                timeout=10
            )
            resp.raise_for_status()
            search_data = resp.json()
            
            # Extract relevant info from DuckDuckGo response
            abstract = search_data.get("Abstract", "")
            related_topics = search_data.get("RelatedTopics", [])
            
            # Build context for the LLM
            context_parts = []
            if abstract:
                context_parts.append(f"Overview: {abstract}")
            
            for topic in related_topics[:3]:  # Top 3 related topics
                if isinstance(topic, dict) and "Text" in topic:
                    context_parts.append(f"- {topic['Text']}")
            
            context = "\n".join(context_parts) if context_parts else "No detailed results found."
            
        except requests.RequestException as e:
            context = f"Search failed: {str(e)}"
            span.set_attribute("search.error", str(e))

        span.set_attribute("search.context_length", len(context))

        # Check for unanswerable queries (no useful results found)
        if context.strip() == "No detailed results found.":
            UNANSWERABLE_QUERY_COUNTER.inc()
            # Do NOT return here; allow the LLM summarization step to still run.

        prompt = f"""You are a helpful research assistant. Based on the search results below about "{query}", provide ONLY a brief 2-3 sentence summary. Do not add any extra commentary, questions, or elaborate beyond the summary.

Search Results:
{context}

Provide your summary now (2-3 sentences only):"""

        # Use OpenAI Chat Completions to generate a concise summary
        try:
            with tracer.start_as_current_span("llm.summarize") as llm_span:
                llm_span.set_attribute("llm.provider", settings.llm_provider)
                llm_span.set_attribute("llm.model", settings.llm_model)

                with LLM_REQUEST_LATENCY.time():
                    response = client.chat.completions.create(
                        model=settings.llm_model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a concise research assistant. Provide brief, factual summaries without elaboration.",
                            },
                            {
                                "role": "user",
                                "content": prompt,
                            },
                        ],
                        temperature=0.2,
                        max_tokens=400,
                    )

                summary = response.choices[0].message.content.strip()

                # If summary is too long, truncate it intelligently
                sentences = summary.split(". ")
                if len(sentences) > 3:
                    summary = ". ".join(sentences[:3]) + "."

                llm_span.set_attribute("llm.response_length", len(summary))

                # Extract token usage and update metrics
                usage = getattr(response, "usage", None)
                if usage is not None:
                    prompt_tokens = getattr(usage, "input_tokens", 0) or getattr(usage, "prompt_tokens", 0)
                    completion_tokens = getattr(usage, "output_tokens", 0) or getattr(usage, "completion_tokens", 0)

                    TOTAL_PROMPT_TOKENS.inc(prompt_tokens)
                    TOTAL_COMPLETION_TOKENS.inc(completion_tokens)

                    cost_usd = estimate_llm_cost_usd(settings.llm_model, prompt_tokens, completion_tokens)
                    TOTAL_COST_USD.inc(cost_usd)

        except Exception as e:
            summary = f"LLM summarization failed (OpenAI): {str(e)}. Raw context: {context[:200]}..."
            span.set_attribute("llm.error", str(e))

        span.set_attribute("summary.length", len(summary))
        return summary
