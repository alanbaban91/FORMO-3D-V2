import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class ExampleSpecs(unittest.TestCase):
    def test_v2_examples(self):
        for filename in ('precision_lens.json','studio_lamp.json'):
            with self.subTest(filename=filename):
                s=json.loads((ROOT/'examples'/filename).read_text())
                self.assertIn(s['type'], ('precision_lens','studio_lamp'))
                self.assertGreaterEqual(s['radius_m'],.025)
                self.assertGreaterEqual(s['height_m'],.025)
                self.assertIn(s['detail_level'],('medium','high','ultra'))
                self.assertGreater(s['render_samples'],0)
    def test_legacy_examples(self):
        for filename in ('stool.json','pedestal.json'):
            with self.subTest(filename=filename):
                s=json.loads((ROOT/'examples'/filename).read_text())
                self.assertIn(s['type'],('stool','table','pedestal'))

if __name__=='__main__': unittest.main()
