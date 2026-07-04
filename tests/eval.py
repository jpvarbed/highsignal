#!/usr/bin/env python3
"""highsignal eval harness.

Runs each test case through a model in DETECT mode and scores it:
  - dirty case passes when the model flags the expected tell
  - clean case passes when the model flags nothing (false-positive guard)

Backends (pick with --backend):
  codex        codex exec CLI            (no key; uses your codex/ChatGPT auth)
  claude-cli   claude -p CLI             (no key; uses your Claude subscription)
  anthropic    Anthropic API            (env ANTHROPIC_API_KEY, --model default claude-sonnet-4-6)
  openrouter   OpenRouter API           (env OPENROUTER_API_KEY, --model required)
  fireworks    Fireworks API            (env FIREWORKS_API_KEY, --model required; open models)

Usage:
  python3 tests/eval.py --backend codex
  python3 tests/eval.py --backend anthropic --model claude-opus-4-8
  python3 tests/eval.py --backend fireworks --model accounts/fireworks/models/qwen3-235b-a22b
"""
import argparse, json, os, re, subprocess, sys, urllib.request

TELLS = {
    "throat-clear": "soft setup that delays the point (\"One thing that helps:\")",
    "claimed-emotion": "claims a feeling instead of showing it (\"what surprised me\")",
    "manufactured-drama": "a tease dressed as a hook (\"refuses to\")",
    "manufactured-quotability": "a clever closer built to sound deep, earning nothing",
    "parataxis": "short clauses stacked with no conjunction, implying an unstated link",
    "not-just-x": "\"it's not just X, it's Y\" fake elevation",
    "filler": "a sentence that carries no information; delete it and lose nothing",
    "abstract-over-number": "vague framing where a concrete number would hit harder",
    "business-speak": "lever, unlock, leverage, move the needle, step-change",
    "label-colon": "a colon faking a beat before a short payoff (\"My hardest problem: sales\")",
    "em-dash": "em dashes overused in any medium (more than ~1 per 100 words)",
    "real-actual": "real/actual as an empty intensifier",
}

def build_prompt(draft, context="social"):
    lines = "\n".join(f"- {k}: {v}" for k, v in TELLS.items())
    return (
        "You are running the 'highsignal' writing skill in DETECT mode.\n"
        "Given the DRAFT, decide which of these AI-writing tells it contains.\n"
        "Only use ids from this exact list:\n" + lines + "\n\n"
        f"The draft is a {context} piece. 'em-dash' counts in any medium when the density "
        "is high (more than ~1 per 100 words); a single em dash in long-form prose is fine. "
        "A colon introducing a genuine list is NOT 'label-colon'. Judge accordingly.\n\n"
        "Output ONLY a JSON array of the matching ids (e.g. [\"filler\",\"em-dash\"]), "
        "or [] if the draft is clean. No prose, no explanation, just the array.\n\n"
        f"DRAFT:\n{draft}\n"
    )

def parse_array(text):
    # find the last bracketed array that parses as a list of strings
    for m in reversed(re.findall(r"\[[^\[\]]*\]", text, re.S)):
        try:
            v = json.loads(m)
            if isinstance(v, list):
                return {str(x).strip().lower() for x in v}
        except Exception:
            pass
    return None  # could not parse -> treat as error

# ---- backends: prompt -> raw text ----
def call_codex(prompt, model):
    out = subprocess.run(["codex", "exec", "--skip-git-repo-check", prompt],
                         capture_output=True, text=True, timeout=180)
    text = out.stdout + "\n" + out.stderr
    # a quota-limited codex answers every case with an error banner; without this
    # guard that scores as [] and a full-suite wipeout masquerades as case failures
    if "hit your usage limit" in text:
        raise RuntimeError("codex usage limit hit; retry after the reset shown in the codex error")
    return text

def call_claude_cli(prompt, model):
    args = ["claude", "-p", prompt] + (["--model", model] if model else [])
    out = subprocess.run(args, capture_output=True, text=True, timeout=180)
    return out.stdout + "\n" + out.stderr

def _http(url, key_header, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"content-type": "application/json", **key_header})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)

def call_anthropic(prompt, model):
    key = os.environ["ANTHROPIC_API_KEY"]
    d = _http("https://api.anthropic.com/v1/messages",
              {"x-api-key": key, "anthropic-version": "2023-06-01"},
              {"model": model or "claude-sonnet-4-6", "max_tokens": 200,
               "messages": [{"role": "user", "content": prompt}]})
    return "".join(b.get("text", "") for b in d.get("content", [])) or json.dumps(d)

def _openai_style(url, key, model, prompt):
    d = _http(url, {"authorization": f"Bearer {key}"},
              {"model": model, "max_tokens": 200, "temperature": 0,
               "messages": [{"role": "user", "content": prompt}]})
    return d["choices"][0]["message"]["content"]

def call_openrouter(prompt, model):
    return _openai_style("https://openrouter.ai/api/v1/chat/completions",
                         os.environ["OPENROUTER_API_KEY"], model, prompt)

def call_fireworks(prompt, model):
    return _openai_style("https://api.fireworks.ai/inference/v1/chat/completions",
                         os.environ["FIREWORKS_API_KEY"], model, prompt)

BACKENDS = {"codex": call_codex, "claude-cli": call_claude_cli, "anthropic": call_anthropic,
            "openrouter": call_openrouter, "fireworks": call_fireworks}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", required=True, choices=BACKENDS)
    ap.add_argument("--model", default=None)
    ap.add_argument("--cases", default=os.path.join(os.path.dirname(__file__), "cases.jsonl"))
    a = ap.parse_args()
    fn = BACKENDS[a.backend]
    cases = [json.loads(l) for l in open(a.cases) if l.strip()]
    passed = errors = fp = 0
    print(f"\nbackend={a.backend} model={a.model or '(default)'}  cases={len(cases)}\n")
    for c in cases:
        try:
            got = parse_array(fn(build_prompt(c["draft"], c.get("context", "social")), a.model))
        except Exception as e:
            got = None
            err = str(e)[:60]
        if got is None:
            errors += 1
            print(f"  {c['id']:>3} ERROR  ({c['kind']})")
            continue
        if c["kind"] == "dirty":
            exp = set(c["expect"]) if isinstance(c["expect"], list) else {c["expect"]}
            ok = bool(exp & got)  # any acceptable tell counts
        else:
            ok = len(got) == 0
            if not ok:
                fp += 1
        passed += ok
        mark = "PASS" if ok else "FAIL"
        extra = "" if ok else f"  expected={c['expect']} got={sorted(got)}"
        print(f"  {c['id']:>3} {mark}  ({c['kind']}){extra}")
    n = len(cases)
    print(f"\n  {passed}/{n} passed · {fp} false-positive(s) on clean · {errors} error(s)")
    print(f"  pass rate: {passed/n:.0%}\n")
    sys.exit(0 if passed == n else 1)

if __name__ == "__main__":
    main()
