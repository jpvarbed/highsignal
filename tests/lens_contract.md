# Lens contract — deterministic adherence + outcome scoring

Frozen dispatch fixture. The dispatched agent implements the runner/scorer AGAINST this
contract and the frozen `arc_cases.jsonl`; it MUST NOT edit this file, the cases, or the
expected labels. This exists to break the "author + examiner + grader in one agent" loop.

## Lens output shape

Each lens agent returns a JSON array of findings. Each finding:
```
{ "category": "<one of the lens's allowed categories>", "quote": "<offending span, verbatim>" }
```
An empty array `[]` means "this lens found nothing." A lens MUST only use categories from its
own allowed set below.

## Allowed categories per lens (the "lane")

- **tells** — the existing tell ids only:
  `throat-clear, value-teaser, vision-abstraction, claimed-emotion, manufactured-drama,
   manufactured-quotability, parataxis, not-just-x, filler, abstract-over-number,
   business-speak, label-colon, em-dash, real-actual`
- **adjacency** — `non-sequitur, missing-connective, broken-referent, local-contradiction`
- **paragraph-arc** — `no-single-job, no-shape, restates-previous, deletable`
- **whole-arc** — `spine-unclear, weak-opening, weak-landing, paragraph-off-spine`

## Adherence (deterministic — NO LLM judge)

For a given case, a lens is **in-lane (adherence PASS)** iff every finding it emitted has a
`category` in that lens's allowed set. A single out-of-lane category = **drift = adherence
FAIL** for that lens on that case. Adherence is pure set-membership; do not use a model to
judge it.

Case-level adherence PASS iff all four lenses are in-lane.

Clean cases: adherence is still just set-membership. An empty array is trivially in-lane, so
clean-case adherence is decided the same way (it does NOT collapse into outcome, because a
lens that emits an out-of-lane category on a clean draft still fails adherence).

## Outcome (deterministic over the structured categories)

- **Planted case** (expect_lens set): outcome PASS iff
  (a) the expected lens emitted >=1 finding whose `category == expect_category`, AND
  (b) every OTHER lens emitted `[]` (zero findings). The frozen planted cases are authored so
      the ONLY issue is the planted one — any other lens firing is a false positive.
- **Clean case** (expect_lens null): outcome PASS iff every lens emitted `[]`.

Note: `adjacency` is an ARC lens category defined here, NOT a member of eval.py's `TELLS`
map. Keep `TELLS` as sentence-tells only; the four lenses live in a separate `ARC_LENSES`
taxonomy keyed by the allowed-category sets above. (`parataxis` stays in `TELLS` / lens 1.)

## Case fully passes

`fully_pass = adherence_PASS AND outcome_PASS` (per case).

## Aggregate gate (DONE)

- **Adherence rate MUST be 100%** across all lenses x all cases. Adherence is deterministic,
  so a drift is a real bug, not model noise — zero tolerance.
- **Outcome rate MUST be >= (P-1)/P** over the P planted cases (allow at most one flap,
  documented like case-8), AND **all clean cases MUST be quiet** (100%).
- The exit-0 predicate for `--arc`: exit 0 iff (adherence_rate == 100%) AND
  (planted_outcome_rate >= (P-1)/P) AND (all clean cases quiet). Else exit 1.
- Report the adherence rate and the outcome rate as two separate numbers; the GATE is the
  conjunction above (not the outcome rate alone).

## Poison control (unit test of the adherence checker)

Fixture `tests/fixtures/poison_trace.json`: a synthetic lens-output map where the
**paragraph-arc** lens emitted a finding with `category: "em-dash"` (out of its lane). The
adherence checker MUST classify this as drift (adherence FAIL) for paragraph-arc. A test
asserts this; if the checker passes the poison trace, the build fails. This is what stops a
rubber-stamp adherence implementation.
