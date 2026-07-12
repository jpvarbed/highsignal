#!/usr/bin/env python3
"""highsignal Δskill holdout eval — SKILL arm (4-lens fan-out) vs BASELINE arm (bare prompt).

Imports eval.py's machinery UNMODIFIED (backends, lens prompts, parsers, deterministic
scorer). This file adds a separate runner mode; it does not touch eval.py, ARC_LENSES,
TELLS, the lens prompts, or the deterministic scorer in any way. See tests/lens_contract.md
for the frozen scoring contract the SKILL arm's deterministic column uses.

Two arms, run k trials each (default 3), ALWAYS FRESH (no transcript cache — this file has
no replay path, unlike eval.py's --fresh flag which only applies to eval.py's own runner):

  SKILL arm     — the existing four-lens fan-out (tests/eval.py --arc), unmodified.
  BASELINE arm  — same backend, same draft, one generic prompt: "List the writing problems
                  in this draft." No lens taxonomy, no skill content.

Scoring:
  - SKILL arm outcome: the existing deterministic contract (case_outcome / case_adherence).
  - BOTH arms also get a judge-scored column: does this arm's raw output identify the
    planted defect (planted cases) / does it stay quiet (clean cases)? LLM judge, majority
    of 3 calls, one fixed prompt per case-kind, decided before any runs and never edited
    after seeing results.

Usage:
  python3 tests/eval_holdout.py --backend codex
  python3 tests/eval_holdout.py --backend codex --trials 3 --out tests/holdout_run.json

Checkpoints after every trial to --out, so a quota error mid-run leaves a readable partial
result instead of losing the whole run.
"""
import argparse, json, os, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval import (
    BACKENDS, LENS_ORDER, TELLS, ARC_LENS_CATEGORY_DESCRIPTIONS,
    build_lens_prompt, parse_findings, lens_adherence, case_adherence, case_outcome,
)

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- isolated-cwd calls for the baseline arm + all judge calls -----------------------------
# DEVIATION (logged in HOLDOUT-RESULTS.md): eval.py's call_codex/call_claude_cli always run
# from the CALLER's cwd. The SKILL arm intentionally keeps that (it must run "exactly as --arc
# runs it", from the highsignal repo root) -- but a smoke test showed codex, run from the repo
# root, agentically reading SKILL.md on its own initiative via a shell tool call even though
# the lens prompt already inlines the full taxonomy. For the BASELINE arm that would silently
# hand it the exact skill content the arm is supposed to run WITHOUT, invalidating the whole
# comparison. So baseline generation calls and ALL judge calls (both arms, for fairness) run
# from a dedicated empty directory outside this repo -- nothing for an agentic backend to find.
# This isn't in eval.py: it is new code in this file, not a modification of frozen machinery.
ISOLATED_CWD = os.environ.get(
    "HOLDOUT_ISOLATED_CWD",
    "/private/tmp/claude-501/-Users-jasonvarbedian-dev/cc92b57a-5c36-4b20-83f6-d00cf17602c5"
    "/scratchpad/holdout_isolated_cwd",
)


def call_codex_isolated(prompt, model, cwd):
    out = subprocess.run(["codex", "exec", "--skip-git-repo-check", prompt],
                         capture_output=True, text=True, timeout=600, cwd=cwd)
    text = out.stdout + "\n" + out.stderr
    if "hit your usage limit" in text:
        raise RuntimeError("codex usage limit hit; retry after the reset shown in the codex error")
    return text


def call_claude_cli_isolated(prompt, model, cwd):
    args = ["claude", "-p", prompt] + (["--model", model] if model else [])
    out = subprocess.run(args, capture_output=True, text=True, timeout=180, cwd=cwd)
    return out.stdout + "\n" + out.stderr


def isolated_call(backend, prompt, model):
    """Same prompt -> raw text contract as eval.py's BACKENDS, but never sees this repo.

    Agentic CLI backends (codex, claude-cli) run from ISOLATED_CWD. Pure API backends
    (anthropic/openrouter/fireworks) have no filesystem access at all, so they are already
    isolated by construction -- call them unchanged.
    """
    os.makedirs(ISOLATED_CWD, exist_ok=True)
    if backend == "codex":
        return call_codex_isolated(prompt, model, ISOLATED_CWD)
    if backend == "claude-cli":
        return call_claude_cli_isolated(prompt, model, ISOLATED_CWD)
    return BACKENDS[backend](prompt, model)

BASELINE_PROMPT = (
    "List the writing problems in this draft.\n\n"
    "DRAFT:\n{draft}\n"
)

# Fixed judge prompts — decided before any runs, never edited after seeing results.
JUDGE_DEFECT_PROMPT = (
    "You are grading whether a piece of writing critique caught a specific known defect.\n\n"
    "CRITIQUE (a reviewer's raw notes on a draft):\n{critique}\n\n"
    "KNOWN DEFECT IN THE DRAFT: {category} — {description}\n\n"
    "Question: does the critique above identify this specific defect (even if worded "
    "differently, even if it also raises other issues)? Answer with exactly one word: "
    "yes or no.\n"
)

JUDGE_CLEAN_PROMPT = (
    "You are grading whether a piece of writing critique raised any real objection to a "
    "draft that a careful editor considers clean.\n\n"
    "CRITIQUE (a reviewer's raw notes on a draft):\n{critique}\n\n"
    "Question: does the critique above claim the draft has a specific, real writing "
    "problem (a false positive, since this draft is clean), as opposed to concluding the "
    "draft reads fine / raising nothing concrete? Answer with exactly one word: yes or no.\n"
)


def category_description(lens, category):
    if lens == "tells":
        return TELLS.get(category, category)
    return ARC_LENS_CATEGORY_DESCRIPTIONS.get(lens, {}).get(category, category)


def parse_yes_no(text):
    t = text.strip().lower()
    # last yes/no token wins (models sometimes think out loud before answering)
    import re
    hits = re.findall(r"\b(yes|no)\b", t)
    if not hits:
        return None
    return hits[-1] == "yes"


def call_backend(fn, model, prompt, label, trace_path):
    """One fresh backend call; always writes its raw transcript. Propagates quota errors."""
    raw = fn(prompt, model)
    os.makedirs(os.path.dirname(trace_path), exist_ok=True)
    with open(trace_path, "w") as f:
        f.write(raw)
    return raw


def run_skill_arm(fn, model, case, trace_dir):
    """One fresh pass of the four-lens fan-out over one case. Returns (lens_outputs, raw_by_lens)."""
    lens_outputs, raw_by_lens = {}, {}
    for lens in LENS_ORDER:
        prompt = build_lens_prompt(lens, case["draft"], case.get("context", "social"))
        trace_path = os.path.join(trace_dir, f"{lens}.txt")
        raw = call_backend(fn, model, prompt, lens, trace_path)
        raw_by_lens[lens] = raw
        lens_outputs[lens] = parse_findings(raw)
    return lens_outputs, raw_by_lens


def skill_critique_text(lens_outputs):
    """Flatten the skill arm's structured 4-lens output into judge-readable critique text."""
    lines = []
    for lens in LENS_ORDER:
        findings = lens_outputs.get(lens)
        if findings is None:
            lines.append(f"{lens}: <unparseable output>")
        elif not findings:
            lines.append(f"{lens}: (no findings)")
        else:
            for f_ in findings:
                lines.append(f"{lens}/{f_.get('category')}: \"{f_.get('quote', '')}\"")
    return "\n".join(lines) if lines else "(no findings from any lens)"


def run_baseline_arm(backend, model, case, trace_dir):
    prompt = BASELINE_PROMPT.format(draft=case["draft"])
    trace_path = os.path.join(trace_dir, "baseline.txt")
    fn_isolated = lambda p, m: isolated_call(backend, p, m)
    raw = call_backend(fn_isolated, model, prompt, "baseline", trace_path)
    return raw


def judge_majority(backend, model, critique_text, case, trace_dir, n=3):
    """Fixed judge prompt, n calls, majority vote.

    Returns (judge_pass, [vote,...], raw_texts). Polarity: a judge "yes" means the critique
    claims/identifies a defect -- on a PLANTED case a majority-yes is a catch (PASS); on a
    CLEAN case a majority-yes is a false positive (FAIL). The smoke test caught the unsigned
    version scoring a quiet-on-clean skill run as FAIL and a false-positive baseline as PASS.
    """
    planted = case.get("expect_lens") is not None
    if planted:
        desc = category_description(case["expect_lens"], case["expect_category"])
        prompt = JUDGE_DEFECT_PROMPT.format(
            critique=critique_text, category=case["expect_category"], description=desc)
    else:
        prompt = JUDGE_CLEAN_PROMPT.format(critique=critique_text)

    fn_isolated = lambda p, m: isolated_call(backend, p, m)
    votes, raws = [], []
    for i in range(1, n + 1):
        trace_path = os.path.join(trace_dir, f"judge{i}.txt")
        raw = call_backend(fn_isolated, model, prompt, f"judge{i}", trace_path)
        raws.append(raw)
        v = parse_yes_no(raw)
        votes.append(v)
    # None (unparseable judge answer) counts as a "no" vote — an unreadable judge call is not
    # evidence of a catch.
    yes_count = sum(1 for v in votes if v is True)
    majority_yes = yes_count > (n // 2)
    judge_pass = majority_yes if planted else (not majority_yes)
    return judge_pass, votes, raws


def load_checkpoint(path):
    if os.path.exists(path):
        return json.load(open(path))
    return {"cases": {}}


def save_checkpoint(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="codex", choices=BACKENDS)
    ap.add_argument("--model", default=None)
    ap.add_argument("--holdout-cases", default=os.path.join(HERE, "holdout_cases.jsonl"))
    ap.add_argument("--trace-dir", default=os.path.join(HERE, "traces_holdout"))
    ap.add_argument("--out", default=os.path.join(HERE, "holdout_run.json"))
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--judge-n", type=int, default=3)
    ap.add_argument("--case-id", default=None, help="run only this one case id (for resuming/testing)")
    a = ap.parse_args()

    fn = BACKENDS[a.backend]
    cases = [json.loads(l) for l in open(a.holdout_cases) if l.strip()]
    if a.case_id:
        cases = [c for c in cases if c["id"] == a.case_id]

    data = load_checkpoint(a.out)
    data.setdefault("backend", a.backend)
    data.setdefault("model", a.model)
    data.setdefault("trials", a.trials)
    data.setdefault("judge_n", a.judge_n)

    print(f"\nholdout eval — backend={a.backend} model={a.model or '(default)'} "
          f"cases={len(cases)} trials={a.trials} judge_n={a.judge_n}\n")

    for case in cases:
        cid = case["id"]
        data["cases"].setdefault(cid, {"case": case, "skill": [], "baseline": []})
        crec = data["cases"][cid]

        # ---- SKILL arm ----
        while len(crec["skill"]) < a.trials:
            trial = len(crec["skill"]) + 1
            tdir = os.path.join(a.trace_dir, cid, "skill", f"trial{trial}")
            print(f"  [{cid}] skill trial {trial}/{a.trials} ...", flush=True)
            try:
                lens_outputs, _raw = run_skill_arm(fn, a.model, case, tdir)
            except RuntimeError as e:
                print(f"    QUOTA/ERROR on skill arm: {e}")
                save_checkpoint(a.out, data)
                print(f"\nSTOPPED on quota error. Partial results saved to {a.out}.")
                sys.exit(2)
            adherence = {lens: lens_adherence(lens, lens_outputs[lens]) for lens in LENS_ORDER}
            c_adherence = all(adherence.values())
            det_outcome = case_outcome(case, lens_outputs)
            critique_text = skill_critique_text(lens_outputs)
            try:
                judge_maj, judge_votes, _jraws = judge_majority(
                    a.backend, a.model, critique_text, case, tdir, n=a.judge_n)
            except RuntimeError as e:
                print(f"    QUOTA/ERROR on skill-arm judge: {e}")
                save_checkpoint(a.out, data)
                print(f"\nSTOPPED on quota error. Partial results saved to {a.out}.")
                sys.exit(2)
            crec["skill"].append({
                "trial": trial,
                "lens_outputs": lens_outputs,
                "adherence": adherence,
                "case_adherence": c_adherence,
                "deterministic_outcome": det_outcome,
                "judge_outcome": judge_maj,
                "judge_votes": judge_votes,
            })
            save_checkpoint(a.out, data)
            print(f"    det_outcome={'PASS' if det_outcome else 'FAIL'}  "
                  f"judge_outcome={'PASS' if judge_maj else 'FAIL'}  "
                  f"adherence={'PASS' if c_adherence else 'FAIL'}")

        # ---- BASELINE arm ----
        while len(crec["baseline"]) < a.trials:
            trial = len(crec["baseline"]) + 1
            tdir = os.path.join(a.trace_dir, cid, "baseline", f"trial{trial}")
            print(f"  [{cid}] baseline trial {trial}/{a.trials} ...", flush=True)
            try:
                raw = run_baseline_arm(a.backend, a.model, case, tdir)
            except RuntimeError as e:
                print(f"    QUOTA/ERROR on baseline arm: {e}")
                save_checkpoint(a.out, data)
                print(f"\nSTOPPED on quota error. Partial results saved to {a.out}.")
                sys.exit(2)
            try:
                judge_maj, judge_votes, _jraws = judge_majority(
                    a.backend, a.model, raw, case, tdir, n=a.judge_n)
            except RuntimeError as e:
                print(f"    QUOTA/ERROR on baseline judge: {e}")
                save_checkpoint(a.out, data)
                print(f"\nSTOPPED on quota error. Partial results saved to {a.out}.")
                sys.exit(2)
            crec["baseline"].append({
                "trial": trial,
                "raw": raw,
                "judge_outcome": judge_maj,
                "judge_votes": judge_votes,
            })
            save_checkpoint(a.out, data)
            print(f"    judge_outcome={'PASS' if judge_maj else 'FAIL'}")

    save_checkpoint(a.out, data)
    print(f"\nDONE. Full results -> {a.out}")


if __name__ == "__main__":
    main()
