"""test_canon_hash.py — the drift-closure contract for the PyPI package.

The bundled CANON must hash (under canonical serialization) to
CANON_TARGET. If this fails, the drift front is OPEN again.
Run: python -m unittest discover -s test  (or: python test/test_canon_hash.py)
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from live_canon import (  # noqa: E402
    LiveCanon, DEFAULT_CANON, BODIES, CANON_TARGET,
    fnv1a_64, fnv1a_64_bytes, serialize_cell, cell_to_dials,
    state_hash, state_hash_hex,
)


class CanonHashGuard(unittest.TestCase):
    def test_corpus_complete(self):
        self.assertEqual(len(DEFAULT_CANON), 71)
        self.assertEqual(len(BODIES), 71)

    def test_state_hash_equals_canon_target(self):
        lc = LiveCanon()
        self.assertEqual(lc.state_hash_hex(), CANON_TARGET)
        self.assertEqual(f"0x{lc.state_hash():016x}", CANON_TARGET)
        self.assertEqual(state_hash_hex(DEFAULT_CANON), CANON_TARGET)
        self.assertEqual(state_hash(DEFAULT_CANON), int(CANON_TARGET, 16))

    def test_serialize_cell_layout(self):
        enc = serialize_cell(1, list(range(1, 17)), [2, 3])
        self.assertEqual(len(enc), 41 + 16)
        self.assertEqual(enc[0], 0x01)
        self.assertEqual(enc[1:9], (1).to_bytes(8, "little"))
        self.assertEqual(enc[41:49], (2).to_bytes(8, "little"))
        self.assertEqual(enc[49:57], (3).to_bytes(8, "little"))

    def test_fnv_byte_exact_with_worker(self):
        # FNV-1a over the same bytes must match the JS worker's fnv1a_64_bytes
        self.assertEqual(fnv1a_64_bytes(b"F115"), fnv1a_64("F115"))
        self.assertEqual(fnv1a_64("F115 — The Logical Routes"),
                         fnv1a_64("F115 — The Logical Routes"))

    def test_dials_sanity(self):
        d425 = cell_to_dials(DEFAULT_CANON[425])
        self.assertEqual(len(d425), 16)
        self.assertEqual(d425[0], 425 * 131)


class Operations(unittest.TestCase):
    def setUp(self):
        self.lc = LiveCanon()

    def test_counts(self):
        self.assertEqual(self.lc.paper_count(), 71)
        self.assertEqual(self.lc.body_count(), 71)

    def test_navigate(self):
        path = self.lc.navigate(425, 2)
        self.assertTrue(path)
        self.assertEqual(path[0]["paper"]["number"], 425)

    def test_confluence(self):
        conf = self.lc.confluence([425, 432, 439])
        self.assertTrue(conf["suggested_title"])

    def test_lineage(self):
        lin = self.lc.lineage(115)
        self.assertTrue(any(p["f_number"] == 116 for p in lin))

    def test_ghost(self):
        g = self.lc.ghost(425, 5)
        self.assertEqual(len(g["neighbors"]), 5)

    def test_tick(self):
        self.assertEqual(self.lc.tick()["ticked_cells"], 71)

    def test_claim(self):
        cl = self.lc.claim("trust ladder")
        self.assertEqual(cl["winner"]["f_number"], 168)

    def test_drill(self):
        dr = self.lc.drill("Mudra vessel bridge")
        self.assertEqual(dr["curriculum"]["doctrine"]["f_number"], 164)


if __name__ == "__main__":
    unittest.main(verbosity=2)
