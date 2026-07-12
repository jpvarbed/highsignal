# Holdout Δskill eval — narrative-arc lenses on held-out REAL cases

**Question:** do the four frozen narrative-arc lenses beat a bare model on writing they were
never tuned on? The merged v1 eval (5/5 planted, cleans quiet) proved the harness, not
generalization — its prompts were calibrated three rounds against the same 7 frozen cases.
This run holds everything frozen and tests on 12 new cases mined verbatim from real writing.

**Setup:** lens prompts, taxonomies, and scorer byte-identical to merged main
(`git diff <merged-main> -- tests/eval.py` = empty, verified at close-out; no tuning after the
holdout set existed). Backend codex (GPT-5.6, xhigh reasoning, subscription). k=3 fresh trials
per case per arm, no transcript cache. Two arms:

- **SKILL** — the four-lens fan-out exactly as `eval.py --arc` runs it (same
  `build_lens_prompt`, same deterministic contract in `tests/lens_contract.md`).
- **BASELINE** — same backend, same draft, one generic prompt: *"List the writing problems in
  this draft."* No taxonomy, no skill content. Baseline + ALL judge calls run from an empty
  isolated cwd (see Deviations #1).

Both arms get a judge-scored column: fixed-prompt LLM judge (prompts written before any runs,
never edited after), majority of 3 calls per trial — *does this critique identify the known
defect?* (planted) / *does it claim a concrete problem?* (clean, inverted: a claim = false
positive). The skill arm is additionally scored by the existing deterministic contract.

**Cases:** `tests/holdout_cases.jsonl` — 9 planted + 3 clean, all verbatim excerpts from real
writing (digest-hooks before/after log, dotfiles dev digests 2026-06-28…07-10), provenance
per case. Label origin: 2 planted cases `derived` from Jason's actual documented edits, 7
planted + 3 clean `agent-labeled` (see Deviations #5 for the cap breach and why).

## Per-case table (P/F per trial, trials 1–3)

| case | origin | expected defect | skill det | skill judge | baseline judge |
|------|--------|-----------------|-----------|-------------|----------------|
| hd1 | derived | tells/manufactured-drama | FFF | FFF | FFF |
| hd2 | derived | tells/value-teaser | PPP | PPP | PPP |
| ha3 | agent-labeled | tells/filler | FFF | FFF | PFP |
| ha4 | agent-labeled | tells/parataxis | PFP | PFP | PPP |
| ha5 | agent-labeled | tells/business-speak | PPP | PPP | PPP |
| ha6 | agent-labeled | tells/em-dash | PPP | PPP | FPP |
| ha7 | agent-labeled | tells/label-colon | PPP | PPP | FFF |
| ha8 | agent-labeled | adjacency/missing-connective | FFF | FFF | FFF |
| ha9 | agent-labeled | paragraph-arc/no-shape | FFF | FFF | PPP |
| hc1 | agent-labeled | (clean) | PPP | PPP | FFF |
| hc2 | agent-labeled | (clean) | PPP | PPP | FFF |
| hc3 | agent-labeled | (clean) | PPP | PPP | FFF |

Raw transcripts: `tests/traces_holdout/<case>/<arm>/trial<n>/`. Full structured results:
`tests/holdout_run.json`.

## Aggregates (judge-scored column unless noted)

**Planted cases (N=9, 27 trials/arm):**

| metric | rate | per-trial spread |
|--------|------|------------------|
| skill judge rate | **51.9%** (14/27) | 56% / 44% / 56% |
| baseline judge rate | **59.3%** (16/27) | 56% / 56% / 67% |
| **Δskill (planted detection)** | **−7.4pp** | +0 / −11 / −11 pp |
| skill deterministic rate | 51.9% (14/27) | 56% / 44% / 56% |

(The deterministic and judge columns agree exactly on this set: every trial where the
expected lens caught the expected category also had the other lenses quiet, and vice versa.)

**Clean cases (N=3, 9 trials/arm):**

| metric | skill | baseline |
|--------|-------|----------|
| quiet-on-clean rate | **100%** (9/9) | **0%** (0/9) |
| false-positive rate | **0%** | **100%** |

The baseline claimed concrete writing problems on every clean trial (e.g. on hc1's one plain
factual sentence). The skill emitted [] from all four lenses on all nine clean trials.

**Combined accuracy, all 12 cases (36 trials/arm):**

| metric | rate | per-trial spread |
|--------|------|------------------|
| skill | **63.9%** (23/36) | 66.7% / 58.3% / 66.7% |
| baseline | **44.4%** (16/36) | 41.7% / 41.7% / 50.0% |
| **Δskill (combined)** | **+19.4pp** | +25.0 / +16.7 / +16.7 pp |

**Derived vs agent-labeled (planted only):**

| slice | N | skill | baseline | Δ |
|-------|---|-------|----------|---|
| derived | 2 | 50.0% | 50.0% | +0.0pp |
| agent-labeled | 7 | 52.4% | 61.9% | −9.5pp |

**Per-case wins:** skill wins 2 (ha6, ha7), baseline wins 3 (ha3, ha4, ha9), ties 4. Cases
were near-deterministic across trials: 10/12 cases were 3/3 or 0/3 in the skill arm.

## What the failures actually are

- **hd1 (manufactured-drama, derived):** the tells lens fired on *other* tells in the excerpt
  (em-dash, label-colon, parataxis — trials 1 and 3) but never manufactured-drama. Both arms
  0/3: nobody catches this one; the skill's miss is category-level, not silence.
- **ha3 (filler):** the tells lens flagged `label-colon` ("Why it matters:") and `not-just-x`
  ("infrastructure claims, not just local workflow preferences") on all three trials — and
  the second one is *literally present in the draft*. Real writing carries multiple genuine
  defects; the single-planted-defect scoring convention (fine for authored fixtures) punishes
  catching a real unplanted one. Scored as a fail per the frozen contract, but this is partly
  a scoring-model artifact, not pure lens failure.
- **ha8 (missing-connective) / ha9 (no-shape):** all four lenses emitted [] on all trials.
  The precision-calibrated prompts ("[] is the normal answer") suppress mild structural
  defects on real prose. The bare baseline caught ha9's flat-list paragraph 3/3 — the one
  place the calibration visibly costs recall the baseline keeps. Both labels are
  agent-labeled and contestable (ha8's connective is arguably reader-suppliable, which the
  adjacency calibration itself says not to flag).

## Verdict (honest, both directions)

**The skill does not beat the baseline at raw defect detection on held-out real writing.**
Planted-detection Δskill is −7.4pp with per-trial spread of ±11pp on N=9 — statistically
indistinguishable from zero at this sample size, and pointing the wrong way. Anyone claiming
the lens taxonomy improves *recall* over a bare frontier model does not have support here.

**Where the skill wins, decisively and consistently, is precision.** The baseline
false-positived on 9/9 clean trials; the skill on 0/9 — a 100pp gap with zero spread, visible
in every trial. Folding cleans and planteds together, Δskill = **+19.4pp** (spread +16.7 to
+25.0pp across trials, positive in all three). For the skill's actual product use — an
automated pass over drafts where most text is fine and every false flag costs editor trust —
quiet-on-clean is the binding constraint, and it is exactly what three rounds of precision
calibration bought. But that same calibration suppresses recall on mild structural defects
(ha8/ha9), and the whole-arc/adjacency/paragraph-arc lenses caught nothing on this set (their
only two planted cases both failed; all their passes are clean-case silences).

**Label-bias caveat:** 7/9 planted labels are this agent's judgment, and the failure analysis
above already impeaches two of them (ha3's "one defect" fiction, ha8's contestable
connective). The 2 derived cases split 1/1 both arms — too few to carry a conclusion alone.
N=9 planted is small; treat the planted-detection number as "no evidence of a detection win,"
not as proof of a detection loss.

## Deviations log

1. **Isolated cwd for baseline + judge calls.** A smoke test showed codex, run from the repo
   root, agentically reading `SKILL.md` mid-call — which would hand the baseline arm the
   skill content it must not see. Baseline generation and all judge calls (both arms, for
   fairness) run from an empty directory outside the repo. Skill-arm lens calls keep eval.py's
   behavior unchanged (they must run exactly as `--arc` does).
2. **Judge polarity fix after the smoke test, before any scored runs.** The unsigned judge
   scored a quiet-on-clean skill run as FAIL and a false-positive baseline as PASS; fixed so
   a clean-case "yes, it claims a problem" = FAIL. No scored trial ran under the buggy
   polarity.
3. **One hung backend call.** ha5 skill trial 3, adjacency lens: codex hung to the 600s
   subprocess timeout. Not scored; the runner gained a retry-once-then-stop path and the
   trial was redone fresh. No quota errors occurred in the entire run (396 planned backend
   calls all completed).
4. **Judge = same backend as the arms (codex), not an independent model** — a shared-model
   bias both arms inherit equally. Majority-of-3 per trial as specified.
5. **Agent-labeled cases exceed the half cap: 10/12 overall, 7/9 planted.** The mining rules
   preferred derived labels, but the source material contains exactly ONE documented
   before/after edit (digest-hooks 2026-07-05 — every later entry has an empty "Jason's
   edit:" field), yielding hd1+hd2; ha3 is edit-supported (Jason replaced the exact bullet in
   dotfiles commit 484b6a3) but the category attribution is agent judgment, so it is marked
   agent-labeled. Raised rather than padded with fake derivations; the derived-vs-agent
   breakdown above is the mitigation.
6. **Case-count at the low end for planted (9 of the 10–15 total target; 12 total).** Chosen
   over stretching into excerpts whose defect labels would have been even weaker.
