# @superinstance/live-canon

**Live Canon — read the AI-Writings canon as a navigable cell fabric.**

[![npm](https://img.shields.io/npm/v/@superinstance/live-canon)](https://www.npmjs.com/package/@superinstance/live-canon)
[![State hash](https://img.shields.io/badge/state_hash-0x7f563ed9982496a1-brightgreen)](https://live-canon.superinstance.dev)
[![Polyformalism](https://img.shields.io/badge/polyformal-7_substrates-blueviolet)](https://github.com/SuperInstance/quilt-rust)
[![Papers](https://img.shields.io/badge/papers-71-orange)](https://live-canon.superinstance.dev)
[![Ops](https://img.shields.io/badge/operations-7-yellow)](https://live-canon.superinstance.dev)

## What it does

Live Canon reads the AI-Writings canon (1700+ papers, 71 in the bundled
release) as a navigable cell fabric. Each paper = 1 cell. Each citation
= 1 edge. The canon exposes 7 novel operations:

1. **NAVIGATE** — BFS through citations
2. **CONFLUENCE** — join 2+ papers, suggest a synthesis
3. **LINEAGE** — trace a concept (F-number) through time
4. **GHOST** — find a paper that should exist by shape proximity
5. **TICK** — re-balance the canon
6. **CLAIM** — find the most-authoritative paper for a topic (with body excerpt) — F169
7. **DRILL** — 3-paper training curriculum (DOCTRINE/IMPLEMENTATION/VERIFICATION) — F169

## Install

```bash
npm install @superinstance/live-canon      # npm
pip install quilt-live-canon                # PyPI
cargo add live-canon                        # Rust (quilt-rust)
```

## Usage

```js
const { LiveCanon } = require('@superinstance/live-canon');

const lc = new LiveCanon();
console.log(lc.paperCount, 'papers, hash', lc.stateHash().toString(16));
// 71 papers, hash 7f563ed9982496a1

// CLAIM
const claim = lc.claim('trust ladder');
console.log(claim.winner.title);  // F168 — The Trust Ladder...

// DRILL
const drill = lc.drill('Mudra vessel bridge');
console.log(drill.curriculum.doctrine.title);  // F164 — cocapn-marine...

// NAVIGATE
const nav = lc.navigate(470, 2);
console.log(nav.length, 'reachable papers from paper-470');
```

## Related packages

| Package | Description |
|---|---|
| `@superinstance/canon-claim` | Thin client for `/api/canon/claim` + `/api/canon/drill` |
| `@superinstance/canon-graph` | BFS graph renderer from `/api/canon` |
| `@superinstance/canon-hash` | State hash fetcher |
| `@superinstance/canon-paper` | Single paper + body |
| `@superinstance/canon-recs` | Related-paper recommender (topic + paper) |
| `@superinstance/canon-suite` | Meta-package: re-exports claim, drill, hash, graph |
| `@superinstance/quilt-canon-cli` | CLI: `canon claim/drill/hash/graph/paper/count` |
| `@superinstance/quilt-cell` | The 16-dial cell as a TS lib, byte-exact with Python |
| `@superinstance/mudra-bridge-core` | Mudra vessel bridge gesture vocabulary + voice synonyms |
| `quilt-live-canon` (PyPI) | The Python port, FNV-1a byte-exact |
| `live-canon` (crates.io) | The Rust no_std port |
| `agent-priming-toolkit` (PyPI) | The 4-layer agent onboarding toolkit (F165) |

## Endpoints (live)

```
GET /api/canon                  list all 71 papers
GET /api/canon/navigate         BFS from paper N
GET /api/canon/confluence       join 2+ papers
GET /api/canon/lineage          papers that cite F{N}
GET /api/canon/ghost            k nearest neighbors
GET /api/canon/tick             re-balance
GET /api/canon/hash             state hash
GET /api/canon/claim            ?topic=X
GET /api/canon/drill            ?topic=X
GET /api/agent/{manifest,tools,doctrine,context,identify,schema,jobs/{NIL,MAK,RUN}}
```

## State hash

`0x7f563ed9982496a1` (71 papers as of 2026-09-04, F98-F169)

## Polyformalism

Byte-exact across 7 substrates: Python, JavaScript, C99, Rust no_std,
Verilog-2005, VHDL-2008, GDScript. The 16-dial cell + FNV-1a 64-bit
state hash is the contract.

## Source

- Worker: https://github.com/SuperInstance/quilt-live-canon
- PyPI source: https://github.com/SuperInstance/quilt-live-canon-pypi
- npm source: https://github.com/SuperInstance/quilt-live-canon-npm
- Rust: https://github.com/SuperInstance/quilt-rust
- Live: https://live-canon.superinstance.dev

## License

MIT © Casey Digennaro
