from live_canon import (
    DEFAULT_CANON, CANON_TARGET, LEGACY_DIAL_ONLY_71, LEGACY_DIAL_ONLY_9,
    state_hash, canonical_state_hash, legacy_dial_only_state_hash,
    serialize_cell, classify_target_provenance, fnv1a_64_bytes,
)

# 1. Canonical test cell — the cross-substrate contract
test = serialize_cell(1, list(range(1, 17)), [2, 3, 4])
h = fnv1a_64_bytes(test)
assert h == 0xE435D91D6D92A1D8, hex(h)
print("OK test cell 0xe435d91d6d92a1d8")

# 2. The bundled 71-paper corpus hashes to the pinned canon target (computed, then pinned)
sh = canonical_state_hash(DEFAULT_CANON)
assert sh == CANON_TARGET == 0x445185A3A99FD2E7, hex(sh)
assert state_hash(DEFAULT_CANON) == CANON_TARGET
print("OK 71-paper canonical state hash 0x445185a3a99fd2e7 == CANON_TARGET")

# 3. Provenance pins: legacy algorithm reproduces its historical claims
legacy = legacy_dial_only_state_hash(DEFAULT_CANON)
assert legacy == LEGACY_DIAL_ONLY_71 == 0x7F563ED9982496A1, hex(legacy)
print("OK legacy dial-only 0x7f563ed9982496a1 (v0.9.0 claim) reproduced")

# 4. The two algorithms are different surfaces — never silently equal
assert legacy != sh
print("OK canonical != legacy (no accidental agreement)")

# 5. Target classification (drift doctrine)
assert classify_target_provenance(CANON_TARGET) == "live"
assert classify_target_provenance(LEGACY_DIAL_ONLY_71) == "reachable"
assert classify_target_provenance(LEGACY_DIAL_ONLY_9) == "stranded"
assert classify_target_provenance(0xDEADBEEF) == "unknown"
print("OK provenance classification live/reachable/stranded/unknown")

print("ALL HASH CONTRACT TESTS PASS")
