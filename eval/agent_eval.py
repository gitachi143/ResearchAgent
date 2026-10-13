"""Score retrieved context on a large notes file. Neither full agent loop runs.

RAG: same chunk size and embedding search as ResearchAgent.ipynb. A hit means
the gold identifier is inside the top 5 chunks the search tool would return.

Wiki: each note is one markdown page. The chat model picks which pages to
read. A hit means the gold identifier is inside those page bodies, which is
the markdown that would be sent back before the answer.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from eval.corpus import (
    NOTES_PATH,
    QUERIES_PATH,
    RecursiveCharSplitter,
    assert_chunk_design,
    build_corpus,
    write_fixtures,
)

RESULTS_PATH = ROOT / "eval" / "agent_results.json"
TOP_K = 5


def _contains(text: str, gold: str) -> bool:
    return gold.lower() in text.lower()


def _message_text(result) -> str:
    output = result.output
    if isinstance(output, list):
        return "\n".join(getattr(message, "text", "") or "" for message in output)
    return getattr(output, "text", "") or str(output)


def _match_titles(reply: str, titles: list[str]) -> list[str]:
    chosen = []
    for line in reply.splitlines():
        folded = line.strip().lstrip("-*0123456789. ").strip().strip('"')
        if not folded:
            continue
        for title in titles:
            if title.lower() == folded.lower() or title.lower() in folded.lower():
                if title not in chosen:
                    chosen.append(title)
        if len(chosen) >= 2:
            break
    return chosen[:2]


async def _choose_pages(llm, question: str, titles: list[str]) -> tuple[list[str], str]:
    from beeai_framework.backend import UserMessage

    catalog = "\n".join(f"- {title}" for title in titles)
    prompt = (
        "Choose which wiki pages to read before answering. "
        "Reply with at most two page titles, one per line, copied from the list. "
        "Do not answer the question.\n\n"
        f"Pages:\n{catalog}\n\n"
        f"Question: {question}"
    )
    result = await llm.run([UserMessage(prompt)])
    reply = _message_text(result)
    return _match_titles(reply, titles), reply


async def main() -> None:
    load_dotenv(ROOT / ".env")
    text, queries, pages = build_corpus()
    problems = assert_chunk_design(text, queries, RecursiveCharSplitter)
    if problems:
        raise SystemExit("\n".join(problems))
    write_fixtures(text, queries)

    chunks = RecursiveCharSplitter().split_text(text)
    by_title = {page["title"]: page["body"] for page in pages}
    titles = [page["title"] for page in pages]
    print(f"notes: {len(pages)}  chars: {len(text)}  chunks: {len(chunks)}  questions: {len(queries)}")
    print(f"wrote {NOTES_PATH}")

    from beeai_framework.backend import ChatModel, ChatModelParameters
    from beeai_framework.backend.embedding import EmbeddingModel
    from beeai_framework.backend.types import Document
    from beeai_framework.backend.vector_store import VectorStore

    model_name = os.environ.get("AZURE_OPENAI_CHAT_MODEL", "gpt-5-mini")
    llm = ChatModel.from_name(f"azure_openai:{model_name}", ChatModelParameters(temperature=1))
    print(f"chat model: {model_name}")

    print("embedding chunks...")
    embedding_model = EmbeddingModel.from_name("ollama:nomic-embed-text")
    vector_store = VectorStore.from_name(name="beeai:TemporalVectorStore", embedding_model=embedding_model)
    await vector_store.add_documents(
        documents=[
            Document(content=chunk, metadata={"source": "long_notes", "chunk": index})
            for index, chunk in enumerate(chunks)
        ]
    )

    rows = []
    for item in queries:
        found = await vector_store.search(item["query"], k=TOP_K)
        rag_chunks = [hit.document.content for hit in found]
        rag_hit = any(_contains(chunk, item["gold"]) for chunk in rag_chunks)

        chosen, reply = await _choose_pages(llm, item["query"], titles)
        passed = "\n".join(by_title[title] for title in chosen)
        wiki_hit = _contains(passed, item["gold"])
        print(
            f"{item['id']:<22} rag {'HIT' if rag_hit else 'MISS'}  "
            f"wiki {'HIT' if wiki_hit else 'MISS'}  pages={chosen or ['(none)']}"
        )
        if not wiki_hit:
            print(f"  model reply: {reply.strip()[:240]}")
        rows.append(
            {
                "id": item["id"],
                "query": item["query"],
                "gold": item["gold"],
                "rag_hit": rag_hit,
                "rag_chunks": len(rag_chunks),
                "wiki_hit": wiki_hit,
                "wiki_pages": chosen,
            }
        )

    n = len(rows)
    rag_hits = sum(row["rag_hit"] for row in rows)
    wiki_hits = sum(row["wiki_hit"] for row in rows)

    def pct(hits: int) -> int:
        return round(100 * hits / n) if n else 0

    summary = {
        "questions": n,
        "notes": len(pages),
        "chunks": len(chunks),
        "rag_top5_chunks": f"{rag_hits}/{n} ({pct(rag_hits)}%)",
        "wiki_pages_passed": f"{wiki_hits}/{n} ({pct(wiki_hits)}%)",
        "rows": rows,
    }
    RESULTS_PATH.write_text(json.dumps(summary, indent=2) + "\n")
    print()
    print(f"RAG, gold in top-{TOP_K} chunks: {summary['rag_top5_chunks']}")
    print(f"wiki, gold in pages the model chose: {summary['wiki_pages_passed']}")
    print(f"wrote {RESULTS_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
