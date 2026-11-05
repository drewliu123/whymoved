import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from research_plan import validate_plan


def plan():
    return {
        "schema_version": 2, "question": "Why did revenue change?", "type": "asset",
        "task": "change explanation", "entity": "example", "as_of": "2026-10-31T18:00:00Z",
        "historical": False, "decision_needed": "Separate volume from price",
        "prior_judgment": "First investigation", "comparison": {"period": "quarterly", "unit": "USD", "scope": "same segment"},
        "hypotheses": [{"explanation": "Volume increased", "discriminating_observation": "Units shipped"}],
        "queries": [{"question": "How many units?", "query": "example quarter shipments", "source": "official", "purpose": "Test volume"}],
        "budget": {"max_queries": 4, "max_followups": 1}, "stop_condition": "Bridge obtained or budget exhausted"
    }


class PlanTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate_plan(plan()), [])

    def test_no_discriminating_observation(self):
        item = plan()
        del item["hypotheses"][0]["discriminating_observation"]
        self.assertTrue(any("discriminating_observation" in x for x in validate_plan(item)))

    def test_malformed_and_budget(self):
        self.assertTrue(validate_plan([]))
        for key, value in (("schema_version", 2.0), ("type", []), ("type", {}), ("as_of", "2026-10-31"), ("historical", "false"), ("queries", []), ("comparison", {}), ("budget", {"max_queries": True, "max_followups": -1})):
            item = copy.deepcopy(plan())
            item[key] = value
            self.assertTrue(validate_plan(item), key)


if __name__ == "__main__":
    unittest.main()
