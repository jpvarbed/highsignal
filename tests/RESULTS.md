# highsignal — cross-model eval results

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
