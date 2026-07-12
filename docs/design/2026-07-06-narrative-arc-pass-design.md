# Design: narrative-arc pass + adherence eval

Date: 2026-07-06
Status: approved design, pre-implementation
Skill: highsignal

## Problem

The skill's review is described as one linear top-down pass (whole-piece → paragraph →
sentence prose → sentence tells), with an "adversarial fan-out" reserved for
product-critical work. Two gaps:

1. **No between-sentence coherence check.** Level 3 grades each sentence in isolation
   (tightness, read-aloud). Nothing asks whether sentence N follows from sentence N-1.
2. **The review isn't measurable per level.** `tests/eval.py` runs one DETECT-mode call
   per case and scores sentence-tell detection only. There is no way to see whether a
   given review lens (arc, adjacency) did its job, because the review is one undifferentiated
   pass.

## Goal

Restructure the review into four independently-checkable lenses run **bottom-up as a
fan-out, in two passes**, and add an eval that runs the same fan-out, captures each lens
agent's trace, and scores both **adherence** (did the agent stay in its lane) and
**outcome** (did the right lens catch a planted issue).

## The review (SKILL.md)

### Four lenses, bottom-up

1. **Tells** — the existing sentence scan (em-dash, throat-clear, value-teaser, parataxis,
   …) plus the avoid-ai-writing detector. Ships at 0 / Clean.
2. **Adjacency** *(new)* — does each sentence follow from the one before it? Flags
   non-sequiturs, missing connectives (because / so / but), dangling or ambiguous
   referents, and local contradictions. Broader than the `parataxis` tell: parataxis stays
   a sentence-level tell in lens 1; adjacency is the general "sentence N ↔ N-1" flow check.
   Some overlap between them is expected and fine.
3. **Paragraph arc** — one job per paragraph, with a shape. Delete any paragraph whose
   removal loses nothing; cut any that restates the one before it.
4. **Whole-piece arc** — spine statable in one sentence; first sentence earns the read (the
   true thing that most updates the reader, never manufactured); last sentence lands; every
   paragraph moves the spine.

### Two passes (verify-and-apply)

- **Pass 1 — find.** Fan the four lenses out concurrently. Each returns findings scoped to
  its lens: the quoted offending text and a proposed fix. Lenses do not edit.
- **Pass 2 — verify and apply.** For each finding, re-check it against the text (is it real?
  does the fix preserve meaning?), drop false flags, apply survivors. Then re-state the
  spine and confirm the arc still holds after the edits.

"Run the lenses at once, then a second pass over the findings" — the two passes are the
find fan-out and the verify-and-apply sweep.

### Tiering

- **Quick edit** — one reviewer runs all four lenses inline, one find + one verify. Cheap;
  the default for throwaway writing.
- **Product-critical** — the real fan-out: one agent per lens for pass 1, then verify-and-apply
  for pass 2. This **replaces** the existing standalone "adversarial fan-out" section (same
  pattern, now the canonical product-critical path).

### Lens taxonomy (not a tell)

`adjacency` is a review **lens**, not a sentence tell — it must NOT go in eval.py's `TELLS`
map. The four lenses live in a separate `ARC_LENSES` taxonomy, each keyed by its allowed
finding categories:

- **tells** — the existing tell ids.
- **adjacency** — `non-sequitur, missing-connective, broken-referent, local-contradiction`.
- **paragraph-arc** — `no-single-job, no-shape, restates-previous, deletable`.
- **whole-arc** — `spine-unclear, weak-opening, weak-landing, paragraph-off-spine`.

`parataxis` stays a sentence tell in lens 1. adjacency is the broader "sentence N ↔ N-1" flow
check; some overlap with parataxis is expected. SKILL.md's prose describes adjacency in the
review/lens section; the machine taxonomy lives in `ARC_LENSES`.

## The eval (tests/)

### Approach

Extend `tests/eval.py` with a fan-out runner and an adherence judge, reusing the existing
backend abstraction (codex / claude-cli / anthropic / openrouter / fireworks). Rejected
alternatives: driving the fan-out through skill-arena or real Claude-Code subagents — both
break the "anyone can run this standalone" requirement. Those remain a documented bridge for
matrix runs, not the core harness.

### Components

- **Fan-out runner.** Given a draft, spawn the four lens-reviewers — one backend call each,
  a lens-specific prompt, structured findings out. Each call's raw output *is* that agent's
  trace.
- **Adherence judge.** Per lens, an LLM-judge scores whether the agent stayed in its lane and
  did its job (e.g. the paragraph-arc agent did not drift into tell-hunting; the adjacency
  agent reported flow breaks, not arc verdicts). This is the "how well each agent follows"
  signal. Scored per-lens.
- **Arc eval cases.** A new `tests/arc_cases.jsonl`: drafts with an issue planted at a
  *specific* level, plus the expected lens that should catch it. Example: a coherence break →
  the adjacency lens flags it and the other lenses stay quiet. Keep the existing
  `tests/cases.jsonl` tell-detection cases unchanged.

### Scoring (deterministic — no LLM judge)

Each lens agent returns structured findings `{category, quote}` where `category` must come
from that lens's allowed set. Both metrics are then computed by set/equality checks, not a
model:

- **Adherence** = set membership. A lens is in-lane iff every emitted `category` is in its
  allowed set. Any out-of-lane category = drift = FAIL. Deterministic, so a drift is a bug
  (zero tolerance), not model noise.
- **Outcome** — planted case: the expected lens emits ≥1 finding with `category ==
  expect_category` AND every other lens emits `[]`. Clean case: every lens emits `[]`.

A case **fully passes only when adherence AND outcome hold** (not "weighted equally" — a plain
AND). Aggregate gate: adherence 100% (deterministic) AND planted-outcome ≥ (P−1)/P (one flap
allowed, documented) AND all clean cases quiet. Full contract in `tests/lens_contract.md`.

This design (adopted after adversarial review by codex + cline) removes the LLM adherence
judge entirely — the only model calls are the four lens agents. It dissolves the rubber-stamp
risk, the undefined "in its lane" boundary, and clean-case ambiguity in one move.

### Frozen fixtures + integrity

To break the "one agent authors cases, labels, prompts, judge, and scorer" loop, the eval set
is **pre-authored and frozen** before dispatch: `tests/arc_cases.jsonl` (5 planted + 2 clean,
each with `expect_lens`/`expect_category`/`why`), `tests/lens_contract.md` (the scoring
contract), and `tests/fixtures/poison_trace.json` (a negative control: a paragraph-arc output
carrying an out-of-lane em-dash finding that the adherence checker MUST fail). The
implementing agent may not edit these; their SHA-256 are pinned in the dispatch rubric.

### Eval scope

Eval v1 scores **pass-1 detection only** (the lens findings). The pass-2 verify-and-apply loop
is exercised by the skill but is out of eval-v1 scope; note this in RESULTS.md rather than
implying it's measured.

### Trace output modes

- `--trace transcript` *(default, self-contained)* — write each agent's transcript to
  `tests/traces/<case>/<lens>.txt`, print the per-lens adherence + outcome table. No external
  dependency; anyone can run it.
- `--trace arize` *(ideal)* — additionally emit OTLP spans: one parent trace per case, one
  span per lens agent, adherence and outcome as span attributes. Uses the hand-rolled
  OTLP/HTTP-over-fetch exporter pattern; viewable in `ax`. Requires the Arize env
  (endpoint + headers).

## Files touched

- `SKILL.md` — rewrite the review section (four lenses bottom-up, two-pass verify-and-apply,
  tiering), fold in the adversarial-fan-out section, add the `adjacency` tell.
- `tests/eval.py` — fan-out runner, adherence judge, `--trace {transcript,arize}` modes,
  keep the existing tell eval path.
- `tests/arc_cases.jsonl` *(new)* — level-planted arc/adjacency cases with expected lens.
- `tests/traces/` *(new, gitignored)* — transcript output.
- `tests/RESULTS.md`, `README.md` — short notes on the new review flow and how to run the
  arc eval in both trace modes.

## Verification

- Existing tell eval (`cases.jsonl`) still passes at its baseline — no regression.
- `arc_cases.jsonl` runs in `--trace transcript` mode with per-lens adherence + outcome
  reported; the planted-issue cases resolve to the expected lens.
- `--trace arize` emits spans that appear in `ax` for at least one case (manual check).

## Out of scope

- skill-arena matrix integration (documented bridge only).
- Auto-tuning lens prompts from eval results.
- Multi-turn lens agents (each lens is a single structured call).
