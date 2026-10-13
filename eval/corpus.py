"""Long notes for the eval.

The company and topic are in the opening. The identifier is buried in a later
chunk, inside an unrelated closer, so vector search can match the opening and
still miss the identifier.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTES_PATH = ROOT / "eval" / "data" / "long_notes.txt"
QUERIES_PATH = ROOT / "eval" / "agent_queries.json"

TARGETS = [
    ("Helios Retail", "observability rollout", "HERON-4419"),
    ("Northwind Bio", "freezer validation", "FROST-2208"),
    ("Keel Harbor", "gearbox inspection", "KEEL-7731"),
    ("Plover Pay", "checkout latency", "PLOV-1184"),
    ("Bramble Health", "site startup", "BRAM-9055"),
    ("Cinder Logistics", "yard dwell", "CIND-3340"),
    ("Sable Insurance", "claims backlog", "SABL-6627"),
    ("Marrow Foods", "spoilage review", "MARR-2816"),
]

DISTRACTORS = [
    ("Quay North", "warehouse scanning", "QUAY-1001"),
    ("Lumen Field", "badge printers", "LUMN-1002"),
    ("Oak Metric", "invoice capture", "OAKM-1003"),
    ("Pine Relay", "driver roster", "PINR-1004"),
    ("Iris Canal", "dock scheduling", "IRIS-1005"),
    ("Vivid Grain", "silo sensors", "VIVD-1006"),
    ("Nimbus Cart", "return labels", "NMBS-1007"),
    ("Harbor Rye", "cask inventory", "HBRY-1008"),
    ("Kite Postal", "route sheets", "KITE-1009"),
    ("Amber Clinic", "shift boards", "AMBR-1010"),
    ("Cobalt Meter", "pump readings", "COBL-1011"),
    ("Yellow Pier", "berth windows", "YELP-1012"),
    ("Maple Circuit", "board tests", "MPLC-1014"),
    ("Drift Radio", "tower checks", "DRFT-1015"),
    ("Silver Anvil", "press cycles", "SLVR-1016"),
    ("Cedar Loom", "pattern drafts", "CEDR-1017"),
]

_MIDDLE = [
    "The platform team compared oncall load across the last two quarters and found the paging policy still too noisy.",
    "Stakeholders asked for a written plan, a success metric, and a date for the next working session.",
    "Operators walked through dashboard screenshots and marked which panels are still misleading.",
    "Support described three recent incidents and the manual checks they still run by hand.",
    "Finance asked for a cost range before any extra infrastructure is approved.",
    "Security asked that service accounts stay scoped and that logs remain in the home region.",
    "The group listed owners for follow-up notes but did not read those notes in the room.",
    "A pilot timeline was sketched for the next month, with a checkpoint at the end of week two.",
    "Attendees argued about staffing for the handoff and left the roster unchanged.",
    "Someone captured risks around seasonal traffic, vendor delays, and incomplete source data.",
    "The room reviewed a sample ticket and agreed the current queue labels are inconsistent.",
    "Next steps were a diagram, a short risk note, and a second meeting after the diagram exists.",
]

_CLOSERS = [
    "Later, a night janitor tagged a closet shelf. The cardboard tag reads {gold}. Nobody brought that tag back upstairs.",
    "A parking attendant wrote {gold} on a visitor pass and left the pass in a glove box.",
    "Cafeteria staff printed {gold} on a soup-station card and pinned the card inside a drawer.",
    "A loading-dock clipboard gained one extra sticker, {gold}, after the guests had already left.",
    "Mailroom sorting used a rubber stamp that happened to read {gold} on an empty interoffice envelope.",
    "The lobby plant log picked up a line, {gold}, from someone watering after hours.",
    "A bike-cage key fob was labeled {gold} and dropped into a bowl at the security desk.",
    "Housekeeping wrote {gold} on masking tape and stuck the tape under a spare chair.",
]

_MUNDANE = [
    "The closet also held spare bulbs, a coiled extension cord, and a box of unmatched name badges.",
    "Rain left a damp patch near the service door and someone propped it with a rubber wedge.",
    "A vending machine blinked until maintenance unplugged it and plugged it back in.",
    "The freight elevator was reserved for a furniture delivery that slipped to the next morning.",
    "A cracked mug sat in the break-room sink beside a sponge that needed replacing.",
    "Ceiling tiles in the copy room were stained, and a work order was already open for them.",
    "The coat rack by the side entrance collected one forgotten umbrella.",
    "A hallway clock ran four minutes fast and nobody reset it that week.",
]


def _middle(salt: int, width: int = 2400) -> str:
    parts: list[str] = []
    i = 0
    while sum(len(part) for part in parts) < width:
        sentence = _MIDDLE[(i + salt) % len(_MIDDLE)]
        parts.append(f"{sentence} Working note {salt}-{i}.")
        i += 1
    return "\n".join(parts)


def _closer(salt: int, gold: str) -> str:
    scene = _CLOSERS[salt % len(_CLOSERS)].format(gold=gold)
    extra: list[str] = []
    i = 0
    while len(scene) + sum(len(part) for part in extra) < 1600:
        extra.append(f"{_MUNDANE[(i + salt) % len(_MUNDANE)]} Slip {salt}-{i}.")
        i += 1
    return scene + "\n" + "\n".join(extra)


def render_note(company: str, topic: str, gold: str, salt: int) -> str:
    head = (
        "==== NOTE ====\n"
        f"Title: {company}: {topic}\n"
        f"Account: {company}\n"
        "Type: meeting_note\n\n"
        "Context:\n"
        f"{company} held a working session on {topic}. "
        "The identifier was intentionally left off the whiteboard and filed after the session.\n\n"
        "Discussion:\n"
    )
    middle = _middle(salt)
    closer = _closer(salt, gold)
    for word in (company, topic, "identifier"):
        if word in middle or word in closer:
            raise RuntimeError(f"note body leaked {word!r}")
    if closer.count(gold) != 1:
        raise RuntimeError(f"{gold} should appear once in the closer")
    return f"{head}{middle}\n\n{closer}\n"


def build_corpus() -> tuple[str, list[dict], list[dict]]:
    rows = list(TARGETS) + list(DISTRACTORS)
    pages = []
    for index, (company, topic, gold) in enumerate(rows):
        pages.append(
            {
                "title": f"{company}: {topic}",
                "company": company,
                "topic": topic,
                "gold": gold,
                "body": render_note(company, topic, gold, index),
            }
        )
    text = "\n".join(page["body"] for page in pages)
    queries = [
        {
            "id": company.lower().replace(" ", "-"),
            "company": company,
            "topic": topic,
            "query": f"What identifier did {company} record after the {topic} session?",
            "gold": gold,
        }
        for company, topic, gold in TARGETS
    ]
    return text, queries, pages


def write_fixtures(text: str, queries: list[dict]) -> None:
    NOTES_PATH.parent.mkdir(parents=True, exist_ok=True)
    NOTES_PATH.write_text(text)
    QUERIES_PATH.write_text(json.dumps(queries, indent=2) + "\n")


def assert_chunk_design(text: str, queries: list[dict], splitter) -> list[str]:
    chunks = splitter().split_text(text)
    problems = []
    for item in queries:
        gold_at = [i for i, chunk in enumerate(chunks) if item["gold"] in chunk]
        if not gold_at:
            problems.append(f"{item['id']}: gold missing from chunks")
            continue
        for index in gold_at:
            if item["company"] in chunks[index]:
                problems.append(f"{item['id']}: gold shares a chunk with the company name")
        if not any(item["company"] in chunk and item["gold"] not in chunk for chunk in chunks):
            problems.append(f"{item['id']}: no opening chunk without the gold")
    return problems


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
