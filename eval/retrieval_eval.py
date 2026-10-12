"""Document retrieval accuracy on the 18-query internal-notes set.

RAG baseline: top-1 TF-IDF over the same 1,000-character chunks
(RecursiveCharacterTextSplitter, overlap 200) used by DocumentSearchAgent.
Memory layer: top-1 TF-IDF over the linked Markdown pages in wiki/.
A hit means the gold span appears in the retrieved text.
"""

import json
import re
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "data" / "rag_conference_prep_agent.txt"
WIKI = ROOT / "wiki"
QUERIES = Path(__file__).with_name("queries.json")


def _split_text_with_regex(text, separator, keep_separator):
    if separator:
        if keep_separator:
            _splits = re.split(f"({re.escape(separator)})", text)
            splits = [_splits[i] + _splits[i + 1] for i in range(0, len(_splits) - 1, 2)]
            if len(_splits) % 2 == 0:
                splits += _splits[-1:]
            return [s for s in splits if s]
        return [s for s in text.split(separator) if s]
    return list(text)


class RecursiveCharSplitter:
    """Same chunk settings as the RAG notebook (chunk_size=1000, overlap=200)."""

    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", " ", ""]

    def split_text(self, text):
        return self._split(text, self.separators)

    def _join(self, docs, sep):
        text = sep.join(docs).strip()
        return text or None

    def _merge(self, splits, separator):
        sep_len = len(separator)
        docs, current, total = [], [], 0
        for piece in splits:
            plen = len(piece)
            if total + plen + (sep_len if current else 0) > self.chunk_size:
                if current:
                    doc = self._join(current, separator)
                    if doc is not None:
                        docs.append(doc)
                    while total > self.chunk_overlap or (
                        total + plen + (sep_len if current else 0) > self.chunk_size and total > 0
                    ):
                        total -= len(current[0]) + (sep_len if len(current) > 1 else 0)
                        current = current[1:]
            current.append(piece)
            total += plen + (sep_len if len(current) > 1 else 0)
        doc = self._join(current, separator)
        if doc is not None:
            docs.append(doc)
        return docs

    def _split(self, text, separators):
        final = []
        separator = separators[-1]
        new_separators = []
        for i, sep in enumerate(separators):
            if sep == "":
                separator = sep
                break
            if sep in text:
                separator = sep
                new_separators = separators[i + 1 :]
                break
        splits = _split_text_with_regex(text, separator, True) if separator else list(text)
        good = []
        for piece in splits:
            if len(piece) < self.chunk_size:
                good.append(piece)
            else:
                if good:
                    final.extend(self._merge(good, ""))
                    good = []
                if not new_separators:
                    final.append(piece)
                else:
                    final.extend(self._split(piece, new_separators))
        if good:
            final.extend(self._merge(good, ""))
        return final


def top1(corpus, query):
    vec = TfidfVectorizer(stop_words="english")
    matrix = vec.fit_transform(corpus)
    scores = cosine_similarity(vec.transform([query]), matrix).ravel()
    return int(scores.argmax())


def pct(hits, total):
    return round(100 * hits / total)


def main():
    notes = NOTES.read_text()
    chunks = RecursiveCharSplitter().split_text(notes)
    pages = [p.read_text() for p in sorted(WIKI.glob("*.md"))]
    queries = json.loads(QUERIES.read_text())

    rag_hits = wiki_hits = 0
    for item in queries:
        gold = item["gold"].lower()
        rag_ok = gold in chunks[top1(chunks, item["query"])].lower()
        wiki_ok = gold in pages[top1(pages, item["query"])].lower()
        rag_hits += rag_ok
        wiki_hits += wiki_ok
        print(
            f"{item['id']:<22} RAG {'hit' if rag_ok else 'miss':<4}  "
            f"memory {'hit' if wiki_ok else 'miss'}"
        )

    n = len(queries)
    print()
    print(f"queries: {n}")
    print(f"RAG chunks: {len(chunks)}")
    print(f"wiki pages: {len(pages)}")
    print(f"RAG-only baseline: {rag_hits}/{n} ({pct(rag_hits, n)}%)")
    print(f"GPT-5 mini memory layer: {wiki_hits}/{n} ({pct(wiki_hits, n)}%)")


if __name__ == "__main__":
    main()
