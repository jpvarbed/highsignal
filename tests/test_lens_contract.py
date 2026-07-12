#!/usr/bin/env python3
"""Unit tests for the deterministic lens scorer in eval.py, run against the frozen fixtures.

No network calls, no LLM in the loop — pure logic over tests/lens_contract.md's rules. Plain
asserts (no pytest dependency, matching eval.py's stdlib-only ethos). Run:

    python3 tests/test_lens_contract.py
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval import ARC_LENSES, LENS_ORDER, lens_adherence, case_adherence, case_outcome

HERE = os.path.dirname(os.path.abspath(__file__))


def test_poison_control():
    """tests/fixtures/poison_trace.json: paragraph-arc emits an out-of-lane 'em-dash' finding.

    The adherence checker MUST classify this as drift (adherence FAIL) for paragraph-arc, and
    FAIL at the case level. If this test ever passes the poison trace, the checker is a
    rubber stamp and the build must fail.
    """
    fixture = json.load(open(os.path.join(HERE, "fixtures", "poison_trace.json")))
    lens_outputs = fixture["lens_outputs"]
    expected = fixture["expected_adherence"]

    got = {lens: ("PASS" if lens_adherence(lens, lens_outputs.get(lens)) else "FAIL")
           for lens in LENS_ORDER}
    assert got == expected, f"per-lens adherence mismatch: got {got} expected {expected}"

    got_case = "PASS" if case_adherence(lens_outputs) else "FAIL"
    assert got_case == fixture["expected_case_adherence"], (
        f"case adherence mismatch: got {got_case} expected {fixture['expected_case_adherence']}")

    assert got["paragraph-arc"] == "FAIL", "poison control must fail paragraph-arc (out-of-lane em-dash)"
    print(f"  test_poison_control: PASS — per-lens {got}, case={got_case}")


def test_all_flagging_synthetic_against_clean_case_fails_outcome():
    """An all-lenses-flagging (but in-lane) output against a real clean case must FAIL outcome.

    This isolates the OUTCOME check from ADHERENCE: every finding below uses a category that
    is valid for its own lens, so adherence would PASS on all four; outcome must still FAIL
    because a clean case requires every lens to emit [].
    """
    cases = [json.loads(l) for l in open(os.path.join(HERE, "arc_cases.jsonl")) if l.strip()]
    clean_case = next(c for c in cases if c["kind"] == "clean")

    synthetic = {
        "tells": [{"category": "em-dash", "quote": "x — y"}],
        "adjacency": [{"category": "non-sequitur", "quote": "x. y."}],
        "paragraph-arc": [{"category": "deletable", "quote": "paragraph"}],
        "whole-arc": [{"category": "weak-opening", "quote": "first sentence"}],
    }
    assert case_adherence(synthetic) is True, (
        "synthetic fixture must be in-lane on all four lenses so this test isolates outcome, "
        "not adherence")

    outcome = case_outcome(clean_case, synthetic)
    assert outcome is False, "an all-flagging synthetic output against a clean case must FAIL outcome"
    print(f"  test_all_flagging_synthetic_against_clean_case_fails_outcome: PASS — "
          f"case={clean_case['id']} outcome={outcome}")


def main():
    print("tests/test_lens_contract.py — deterministic scorer unit tests\n")
    test_poison_control()
    test_all_flagging_synthetic_against_clean_case_fails_outcome()
    print("\nAll lens_contract unit tests PASSED.")


if __name__ == "__main__":
    main()
