# highsignal — cross-model eval results

## Narrative-arc lens eval (July 2026)

The review's four lenses (`tells` → `adjacency` → `paragraph-arc` → `whole-arc`) run as a
fan-out over [`arc_cases.jsonl`](./arc_cases.jsonl) (5 planted + 2 clean, frozen) and are
scored deterministically against [`lens_contract.md`](./lens_contract.md): adherence is pure
set-membership over each lens's allowed categories, outcome is category-match plus
cross-lens-quiet. No LLM judge anywhere in scoring; the only model calls are the four lens
agents. One structured `codex exec` call per lens per case; each call's raw output is that
agent's trace at `traces/<case>/<lens>.txt` (gitignored).

Result, backend `codex` (codex-cli 0.142.4, default model):

| Metric | Result | Gate |
|---|---|---|
| Adherence rate (lens stayed in its lane) | 28/28 = 100% | must be 100% |
| Planted outcome rate (right lens caught it, others quiet) | 5/5 = 100% | ≥ 4/5 |
| Clean cases quiet | 2/2 | must be 100% |
| **Gate** | **PASS (exit 0)** | conjunction of the three |

Notes:

- Adherence never drifted across three prompt iterations — no lens ever emitted an
  out-of-lane category. All early outcome failures were sibling lenses re-describing the one
  planted defect at their own granularity (e.g. `whole-arc` calling a non-sequitur
  `spine-unclear`); fixed with per-lens precision calibration in the prompts, not by touching
  cases or scorer.
- The adherence checker is guarded by a negative control:
  [`fixtures/poison_trace.json`](./fixtures/poison_trace.json) plants an out-of-lane
  `em-dash` finding under `paragraph-arc`; [`test_lens_contract.py`](./test_lens_contract.py)
  fails the build if the checker passes it.
- **Eval v1 scores pass-1 detection only.** The skill's pass 2 (verify-and-apply: re-check
  each finding, drop false flags, apply, re-state the spine) is exercised by the skill but is
  explicitly out of eval scope for v1 — nothing here measures it.

Reproduce:

```bash
python3 tests/eval.py --arc --backend codex --trace transcript   # hard gate; exit 0 iff gate holds
python3 tests/eval.py --arc --backend codex --trace arize        # + OTLP JSON export (POSTs only if ARIZE_API_KEY/ARIZE_SPACE_ID set)
python3 tests/test_lens_contract.py                              # scorer unit tests, no network
```

## Tell eval (July 2026 re-run)

`python3 tests/eval.py --backend codex` on the current 19-case [`cases.jsonl`](./cases.jsonl)
(15 dirty, 4 clean): **19/19, 0 false positives, 0 errors**, including case 7 (`filler`,
codex's documented weak spot below — the detect prompt now walks sentence-by-sentence for
deletable sentences) and case 8 (`abstract-over-number`, the known flap).

## Cross-model tell results (June 2026)

Both models run through [`eval.py`](./eval.py) on [`cases.jsonl`](./cases.jsonl) (14 cases:
11 dirty, 3 clean), detect mode, single run each. June 2026.

## Scores

| Model | Pass | Rate | False positives (clean) |
|---|---|---|---|
| `codex exec` (codex-cli 0.142.4, default model) | 13/14 | 93% | 0 |
| Claude `sonnet-4-6` (Anthropic API) | 12/14 | 86% | 0 |

Zero false positives for both — neither over-flags clean writing, including the long-form
em-dash sentence and the genuine three-item list.

## Per-tell

| Tell | Claude | Codex |
|---|---|---|
| throat-clear | ✅ | ✅ |
| claimed-emotion | ✅ | ✅ |
| manufactured-drama | ✅ | ✅ |
| manuf-quotability / parataxis (case 4) | ❌ | ✅ |
| parataxis (case 5) | ✅ | ✅ |
| not-just-x | ✅ | ✅ |
| filler | ✅ | ❌ |
| abstract-over-number | ❌ | ✅ |
| business-speak | ✅ | ✅ |
| em-dash (social) | ✅ | ✅ |
| real-actual | ✅ | ✅ |
| clean ×3 | ✅✅✅ | ✅✅✅ |

## Findings

- The clear lexical and structural tells (throat-clear, drama, not-just-x, business-speak,
  em-dash, real/actual, parataxis) are caught reliably by both models.
- **Codex's weak spot is `filler`** — missed it in both runs. Filler detection asks the model
  to judge that a sentence adds nothing, which it under-calls.
- **`abstract-over-number` is the hardest tell for both** — caught inconsistently. Vague
  quantifiers like "a huge number" aren't an obvious error, so detection is unreliable. It
  reads more as a rewrite suggestion than a detectable pattern.
- **Run-to-run variance is real:** cases 4 and 8 flip between runs on both models, which is
  how the two ended one point apart. A single run is noisy.

## Limitations / next

- Single run per case. LLM detectors vary run-to-run; the honest fix is majority-vote over N
  runs (e.g. 3) per case. This harness should add it.
- The codex backend uses whatever model `codex exec` defaults to; pin the model for
  reproducibility.
- `abstract-over-number` and `manufactured-quotability` may need sharper, less subjective
  definitions in the skill, or to be marked lower-confidence tells.

## Reproduce

```bash
scripts/score.sh codex
ANTHROPIC_API_KEY=… scripts/score.sh anthropic
```
