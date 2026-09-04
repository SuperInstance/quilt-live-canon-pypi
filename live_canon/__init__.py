"""live_canon — The Live Canon as a Python package.

This is the PyPI distribution of the AI-Writings seed canon, served as
a navigable cell fabric. The package is the byte-exact Python port of
the Cloudflare Worker at https://live-canon.superinstance.dev — same
canon, same operations, same FNV-1a 64-bit state hash.

The 7 operations are:
  1. NAVIGATE  — BFS through citations from a paper
  2. CONFLUENCE — join 2+ papers, find shared F-numbers, suggest synthesis
  3. LINEAGE   — trace a concept (F-number) through time
  4. GHOST     — k nearest neighbors by dial-vector cosine similarity
  5. TICK      — re-balance the canon
  6. CLAIM     — find the most-authoritative paper for a topic (with excerpt)
  7. DRILL     — 3-paper training curriculum (DOCTRINE, IMPLEMENTATION, VERIFICATION)

Polyformal: byte-exact with JavaScript, C99, Rust, Verilog, VHDL.
State hash: 0x7f563ed9982496a1 (71 papers as of 2026-09-04).
"""
from __future__ import annotations

import math
import re
from typing import Any, Dict, List, Optional, Set, Tuple
import json
import os

__version__ = "0.9.0"
__all__ = [
    "LiveCanon", "DEFAULT_CANON", "BODIES",
    "fnv1a_64", "cell_to_dials", "state_hash",
    "navigate", "confluence", "lineage", "ghost", "tick",
    "claim", "drill",
]


# FNV-1a 64-bit hash (UTF-8, byte-exact with JS/C/Rust/Verilog/VHDL)
FNV_OFFSET = 0xCBF29CE484222325
FNV_PRIME = 0x00000100000001B3


def fnv1a_64(s: str) -> int:
    """FNV-1a 64-bit hash of a string. Byte-exact across all 6 substrates."""
    h = FNV_OFFSET
    for byte in s.encode("utf-8"):
        h ^= byte
        h = (h * FNV_PRIME) & 0xFFFFFFFFFFFFFFFF
    return h


def cell_to_dials(paper: Dict[str, Any]) -> List[int]:
    """Map a paper to its 16-dial cell. Matches cellToDials() in the Worker."""
    date_str = paper.get("date", "") or "1970-01-01"
    try:
        year = int(date_str[:4])
    except (ValueError, TypeError):
        year = 1970
    year_q = (year - 1970) * 546
    phase_q = paper.get("phase", 0) * 218
    f_q = paper.get("f_number", 0) * 218
    n_refs = len(paper.get("ref_papers", [])) + len(paper.get("ref_f_numbers", []))
    n_refs_q = min(0x7FFF, n_refs * 256)
    th = fnv1a_64(paper.get("title", ""))
    title_lo = th & 0xFFFF
    title_hi = (th >> 16) & 0xFFFF
    num = min(paper.get("number", 0), 500)
    num_q = num * 131
    return [num_q, title_lo, f_q, phase_q, year_q, n_refs_q, title_hi, 0,
            0, 0, 0, 0, 0, 0, 0, 0]


def cosine_sim(a: List[int], b: List[int]) -> float:
    """Cosine similarity between two 16-dial vectors."""
    dot = sum(ai * bi for ai, bi in zip(a, b))
    na = math.sqrt(sum(ai * ai for ai in a))
    nb = math.sqrt(sum(bi * bi for bi in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def state_hash(papers: Dict[int, Dict[str, Any]]) -> int:
    """FNV-1a 64-bit state hash over the sorted concatenation of all dials.
    Byte-exact with the Cloudflare Worker.
    """
    all_dials = [cell_to_dials(p) for p in papers.values()]
    all_dials.sort(key=lambda d: d[0])  # sort by paper number
    h = FNV_OFFSET
    for dials in all_dials:
        for v in dials:
            lo = v & 0xFF
            hi = (v >> 8) & 0xFF
            h ^= lo
            h = (h * FNV_PRIME) & 0xFFFFFFFFFFFFFFFF
            h ^= hi
            h = (h * FNV_PRIME) & 0xFFFFFFFFFFFFFFFF
    return h


# ----- The 5 cite-graph operations (F129) -----

def navigate(canon: Dict[int, dict], start: int, depth: int = 1) -> List[dict]:
    """BFS through citations from a paper."""
    visited = {start}
    result = []
    queue = [(start, 0)]
    while queue:
        num, d = queue.pop(0)
        paper = canon.get(num)
        if paper:
            result.append({"depth": d, "paper": paper})
            if d < depth:
                for ref in (paper.get("ref_papers") or []):
                    if ref in canon and ref not in visited:
                        visited.add(ref)
                        queue.append((ref, d + 1))
    return result


def confluence(canon: Dict[int, dict], paper_nums: List[int]) -> dict:
    """Join 2+ papers, find shared F-numbers, suggest synthesis."""
    if not paper_nums:
        return {"error": "no papers"}
    shared_refs: Optional[Set[int]] = None
    shared_f: Optional[Set[int]] = None
    titles = []
    for num in paper_nums:
        p = canon.get(num)
        if not p:
            continue
        titles.append(p["title"])
        refs = set(p.get("ref_papers") or [])
        shared_refs = refs if shared_refs is None else (shared_refs & refs)
        fs = set(p.get("ref_f_numbers") or [])
        shared_f = fs if shared_f is None else (shared_f & fs)
    suggested = f"Composition of {len(paper_nums)} papers"
    if shared_f:
        first = sorted(shared_f)[0]
        suggested = f"F{first} Synthesis: {', '.join(titles)}"
    max_n = max(canon.keys()) if canon else 0
    return {
        "input_papers": paper_nums,
        "input_titles": titles,
        "shared_refs": sorted(shared_refs) if shared_refs else [],
        "shared_f_numbers": sorted(shared_f) if shared_f else [],
        "suggested_title": suggested,
        "ghost_paper": f"paper-{max_n + 1}.md",
    }


def lineage(canon: Dict[int, dict], f_number: int) -> List[dict]:
    """Papers that cite F{N}."""
    result = []
    for p in canon.values():
        if f_number in (p.get("ref_f_numbers") or []):
            result.append(p)
    result.sort(key=lambda p: (p.get("phase", 0), p.get("number", 0)))
    return result


def ghost(canon: Dict[int, dict], paper_num: int, k: int = 5) -> dict:
    """k nearest neighbors by dial-vector cosine similarity."""
    target = canon.get(paper_num)
    if not target:
        return {"error": "missing paper"}
    target_dials = cell_to_dials(target)
    scored = []
    for n, p in canon.items():
        if n == paper_num:
            continue
        score = cosine_sim(target_dials, cell_to_dials(p))
        scored.append({"id": f"p{str(n).zfill(4)}", "score": round(score, 4)})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return {
        "source_paper": f"paper-{paper_num}.md",
        "neighbors": scored[:k],
        "suggested_title": f"A Bridge between F{target.get('f_number')} and its neighbors",
    }


def tick(canon: Dict[int, dict]) -> dict:
    """Re-balance the canon (no-op for read-only, returns cell count)."""
    return {"ticked_cells": len(canon)}


# ----- Operations 6 and 7: CLAIM and DRILL (F169) -----

def _score_paper(canon: Dict[int, dict], bodies: Dict[int, dict],
                 paper_num: int, paper: dict, q_tokens: List[str],
                 query_fns: List[int]) -> Tuple[float, dict]:
    """Score one paper against a query. Returns (score, breakdown)."""
    title = (paper.get("title") or "").lower()
    body_data = bodies.get(paper_num) or {}
    body = (body_data.get("excerpt") or "").lower()
    h1 = (body_data.get("h1") or "").lower()

    title_matches = sum(1 for t in q_tokens if t in title)
    h1_matches = sum(1 for t in q_tokens if t in h1)
    body_matches = sum(1 for t in q_tokens if t in body)
    fn_matches = sum(1 for f in query_fns if f in (paper.get("ref_f_numbers") or []))
    recency = (paper.get("f_number") or 0) * 0.1

    score = title_matches * 100 + h1_matches * 50 + body_matches * 25 + fn_matches * 200 + recency
    breakdown = {
        "title": title_matches, "h1": h1_matches, "body": body_matches,
        "fn": fn_matches, "recency": round(recency, 1)
    }
    return score, breakdown


def claim(canon: Dict[int, dict], bodies: Dict[int, dict], query: str) -> dict:
    """Find the most-authoritative paper for a topic.

    Returns the winner, 3 runners-up, and a match_breakdown that shows
    why the winner won. If no paper directly addresses the topic, returns
    the most-recent paper (recency-tied) — this is honest, not a hallucination.
    """
    q = (query or "").lower().strip()
    if not q:
        return {"error": "empty query"}
    q_tokens = [t for t in q.split() if len(t) >= 2]
    if not q_tokens:
        return {"error": "query too short"}
    query_fns = [int(m) for m in re.findall(r"f\s*(\d+)", q, flags=re.IGNORECASE)]

    scored = []
    for n, paper in canon.items():
        score, breakdown = _score_paper(canon, bodies, n, paper, q_tokens, query_fns)
        if score > 0:
            body_data = bodies.get(n) or {}
            scored.append({
                "number": n,
                "title": paper["title"],
                "f_number": paper.get("f_number"),
                "phase": paper.get("phase"),
                "date": paper.get("date"),
                "ref_f_numbers": paper.get("ref_f_numbers") or [],
                "score": round(score, 1),
                "match_breakdown": breakdown,
                "excerpt": body_data.get("excerpt") or "",
            })
    scored.sort(key=lambda x: (
        -x["score"],
        -(x.get("f_number") or 0),
        -len(x.get("ref_f_numbers") or [])
    ))
    return {
        "query": query,
        "tokens": q_tokens,
        "winner": scored[0] if scored else None,
        "runners_up": scored[1:4],
        "total_candidates": len(scored),
    }


def drill(canon: Dict[int, dict], bodies: Dict[int, dict], query: str) -> dict:
    """A 3-paper training curriculum for a topic.

    Returns DOCTRINE (the paper cited by the most other candidates),
    IMPLEMENTATION (the paper that cites the doctrine), and VERIFICATION
    (the third). Heuristic-based role assignment.
    """
    result = claim(canon, bodies, query)
    if result.get("error"):
        return result
    if not result.get("winner"):
        return {"error": "no matching paper", "query": query}
    top = [result["winner"]] + list(result.get("runners_up") or [])
    top = top[:3]
    while len(top) < 3:
        top.append(None)

    if all(top):
        ref_sets = [set(t["ref_f_numbers"]) for t in top]
        cited_by = [
            sum(1 for j, s in enumerate(ref_sets) if j != i and s and s & {t["f_number"]})
            for i, t in enumerate(top)
        ]
        if cited_by:
            max_idx = cited_by.index(max(cited_by))
            if max_idx != 0:
                top[0], top[max_idx] = top[max_idx], top[0]

    def card(t, role, color):
        if not t:
            return None
        return {
            "number": t["number"],
            "title": t["title"],
            "f_number": t["f_number"],
            "phase": t["phase"],
            "date": t["date"],
            "role": role,
            "color": color,
            "score": t["score"],
            "excerpt": (t.get("excerpt") or "")[:500],
        }

    return {
        "query": query,
        "curriculum": {
            "doctrine": card(top[0], "DOCTRINE — the paper that defines the concept", "#8bcf6e"),
            "implementation": card(top[1], "IMPLEMENTATION — the paper that builds the thing", "#f4b942"),
            "verification": card(top[2], "VERIFICATION — the paper that audits the result", "#cf6e8b"),
        },
    }


# ----- The bundled canon and bodies -----

def _load_data() -> dict:
    """Load the bundled canon + bodies from the package data file."""
    here = os.path.dirname(__file__)
    data_path = os.path.join(here, "_data.json")
    if not os.path.exists(data_path):
        # Fall back to a minimal canon (F115, F129) if the data file is missing
        return {
            "canon": {
                425: {"number": 425, "title": "F115 — The Logical Routes: VHDL × Verilog × the QUF bit-exactness",
                      "f_number": 115, "phase": 237, "date": "2026-09-03", "ref_papers": [426, 427], "ref_f_numbers": []},
                439: {"number": 439, "title": "F129 — The Live Canon: Papers as Cells, Reading as Navigation",
                      "f_number": 129, "phase": 251, "date": "2026-09-03", "ref_papers": [], "ref_f_numbers": [115, 120, 122, 125]},
            },
            "bodies": {}
        }
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


_data = _load_data()
DEFAULT_CANON: Dict[int, dict] = {int(k): v for k, v in _data.get("canon", {}).items()}
BODIES: Dict[int, dict] = {int(k): v for k, v in _data.get("bodies", {}).items()}


class LiveCanon:
    """The Live Canon as a Python object. 71 papers bundled (F98-F169).

    Example:
        >>> lc = LiveCanon()
        >>> hex(lc.state_hash())
        '0x7f563ed9982496a1'
        >>> lc.claim("trust ladder")["winner"]["f_number"]
        168
        >>> lc.drill("Mudra vessel bridge")["curriculum"]["doctrine"]["f_number"]
        164
    """

    def __init__(self, canon: Optional[Dict[int, dict]] = None,
                 bodies: Optional[Dict[int, dict]] = None):
        self.canon = canon if canon is not None else DEFAULT_CANON
        self.bodies = bodies if bodies is not None else BODIES

    def state_hash(self) -> int:
        return state_hash(self.canon)

    def paper_count(self) -> int:
        return len(self.canon)

    def body_count(self) -> int:
        return len(self.bodies)

    def navigate(self, start: int, depth: int = 1) -> List[dict]:
        return navigate(self.canon, start, depth)

    def confluence(self, paper_nums: List[int]) -> dict:
        return confluence(self.canon, paper_nums)

    def lineage(self, f_number: int) -> List[dict]:
        return lineage(self.canon, f_number)

    def ghost(self, paper_num: int, k: int = 5) -> dict:
        return ghost(self.canon, paper_num, k)

    def tick(self) -> dict:
        return tick(self.canon)

    def claim(self, query: str) -> dict:
        return claim(self.canon, self.bodies, query)

    def drill(self, query: str) -> dict:
        return drill(self.canon, self.bodies, query)
