from __future__ import annotations
import json
import logging
import re
from typing import Any, Dict, List, Sequence

from core.llm import llm

logger = logging.getLogger(__name__)


def _safe_truncate(s: str, n: int) -> str:
    return s if len(s) <= n else s[:n] + "..."


def _extract_json(text: str) -> str | None:
    # Try to find the first JSON array in the text
    m = re.search(r"\[\s*\{", text)
    if not m:
        return None
    start = m.start()
    # find matching closing bracket by naive approach
    stack = 0
    for i in range(start, len(text)):
        if text[i] == "[":
            stack += 1
        elif text[i] == "]":
            stack -= 1
            if stack == 0:
                return text[start : i + 1]
    return None


def rerank_docs(query: str, docs: List[Any], top_k: int = 5, max_chars: int = 1000) -> List[Dict[str, Any]]:
    """Rerank `docs` against `query` using the project LLM.

    `docs` may be strings or objects; they will be stringified. The LLM
    is asked to return a JSON array of objects with fields `index` (int)
    and `score` (number between 0 and 100). The returned list contains
    dicts with keys `doc` and `score` (float), sorted by score desc.
    """
    if not docs:
        return []

    snippets = [(_safe_truncate(str(d), max_chars), i) for i, d in enumerate(docs)]

    # Build prompt
    prompt_lines = [
        "You are a relevance scorer.\n",
        f"Query: {query}\n",
        "Score each document for relevance to the query on a scale from 0 (not relevant) to 100 (highly relevant).",
        "Return ONLY a valid JSON array of objects with fields: index (int), score (number), explanation (short string).",
        "Example output: [{\"index\":0, \"score\":87.5, \"explanation\":\"short reason\"}, ...]",
        "\nDocuments:\n",
    ]

    for text, i in snippets:
        # escape newlines to keep prompt compact
        safe_text = text.replace("\n", "\\n")
        prompt_lines.append(f"[{i}] {safe_text}\n")

    prompt = "\n".join(prompt_lines)

    try:
        resp = llm.invoke(prompt)
        content = getattr(resp, "content", str(resp))
    except Exception as e:
        logger.exception("LLM reranker invocation failed: %s", e)
        return []

    try:
        parsed = json.loads(content)
    except Exception:
        block = _extract_json(content)
        if not block:
            logger.warning("Could not parse reranker output as JSON: %s", content)
            return []
        try:
            parsed = json.loads(block)
        except Exception:
            logger.exception("Failed to parse extracted JSON block from reranker output")
            return []

    # Normalize parsed entries
    results = []
    for item in parsed:
        try:
            idx = int(item.get("index"))
            score = float(item.get("score"))
        except Exception:
            continue
        if 0 <= idx < len(docs):
            results.append({"doc": docs[idx], "score": float(score)})

    # sort and return top_k
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


__all__ = ["rerank_docs"]
