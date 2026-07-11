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

Narrative-arc lens fan-out (tests/arc_cases.jsonl, scored per tests/lens_contract.md):
  python3 tests/eval.py --arc --backend codex --trace transcript
  python3 tests/eval.py --arc --backend codex --trace arize
  python3 tests/test_lens_contract.py   # deterministic-scorer unit tests, no network
"""
import argparse, json, os, re, secrets, subprocess, sys, time, urllib.error, urllib.request

TELLS = {
    "throat-clear": "soft setup that delays the point (\"One thing that helps:\")",
    "value-teaser": "announces something is worth attention instead of just saying it (\"the one thing worth 30 seconds\", \"here's the kicker\", \"worth noting\")",
    "vision-abstraction": "positioning that names an abstract category (a platform/layer/engine/intelligence) where the concrete outcome belongs; only when it's selling a capability, not when a category noun is a plain literal referent",
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

# ---- narrative-arc lenses (tests/lens_contract.md is the scoring contract) ----
# Four review lenses run bottom-up. adjacency is a lens category set, NOT a TELLS entry;
# `parataxis` stays a sentence tell above. Keyed by each lens's allowed finding categories
# (its "lane") per tests/lens_contract.md.
ARC_LENSES = {
    "tells": set(TELLS.keys()),
    "adjacency": {"non-sequitur", "missing-connective", "broken-referent", "local-contradiction"},
    "paragraph-arc": {"no-single-job", "no-shape", "restates-previous", "deletable"},
    "whole-arc": {"spine-unclear", "weak-opening", "weak-landing", "paragraph-off-spine"},
}
LENS_ORDER = ["tells", "adjacency", "paragraph-arc", "whole-arc"]  # bottom-up, matches SKILL.md

ARC_LENS_CATEGORY_DESCRIPTIONS = {
    "adjacency": {
        "non-sequitur": "two adjacent sentences share no logical link",
        "missing-connective": "the link between adjacent sentences exists but needs a stated "
                               "because/so/but/and that the draft leaves out",
        "broken-referent": "a pronoun or reference at a sentence boundary has an ambiguous or "
                            "dangling antecedent",
        "local-contradiction": "adjacent sentences contradict each other",
    },
    "paragraph-arc": {
        "no-single-job": "the paragraph does not do one clear job",
        "no-shape": "the paragraph has no shape or movement, just a flat list of facts",
        "restates-previous": "the paragraph repeats the previous paragraph without adding new "
                              "information",
        "deletable": "the paragraph could be cut and nothing would be lost",
    },
    "whole-arc": {
        "spine-unclear": "the piece has no statable one-sentence spine",
        "weak-opening": "the first sentence does not earn the read; the real news is buried later",
        "weak-landing": "the last sentence does not land",
        "paragraph-off-spine": "a paragraph does not move the spine forward",
    },
}

ARC_LENS_CALIBRATION = {
    "tells": (
        "Calibration: flag only clear, mechanical hits. 'em-dash' counts in any medium when "
        "the density is high (more than ~1 per 100 words, or 2+ in a short piece); a single em "
        "dash in long-form prose is fine. A colon introducing a genuine list is NOT "
        "'label-colon'. 'abstract-over-number' is a low-confidence rewrite hint, NOT a "
        "detectable error: do not flag it when the vague phrase merely paraphrases a concrete "
        "number that already appears elsewhere in the draft, and do not flag ordinary informal "
        "wording. A sentence sitting oddly next to its neighbor is the adjacency lens's lane, "
        "not a tell."
    ),
    "adjacency": (
        "Calibration: flag only breaks a reader actually stumbles on. Do NOT flag "
        "'missing-connective' when the reader effortlessly supplies the link: plain narrative "
        "sequence, a cause already stated nearby, an explicit because/so/but already present, "
        "or a paragraph break that simply moves to the next point. A paragraph transition "
        "changing topic is paragraph/whole-piece territory, not yours. Flag 'non-sequitur' "
        "only when two adjacent sentences genuinely share no logical link, and "
        "'broken-referent' only when a pronoun really has two or more live candidate "
        "antecedents at the boundary."
    ),
    "paragraph-arc": (
        "Calibration: judge whole paragraphs only. If the draft is a single short paragraph, "
        "output [] unless that one paragraph genuinely restates something or is deletable as a "
        "unit. Do not re-describe a sentence-level flow break (two oddly-joined sentences) as "
        "'no-single-job'; that is the adjacency lens's lane. 'restates-previous' requires a "
        "paragraph that adds no new information over the one before it."
    ),
    "whole-arc": (
        "Calibration: flag only clear whole-piece failures. 'weak-opening' means the real news "
        "is buried later in the piece while the opening spends itself on setup. A short "
        "factual update that states its point and stops does NOT have a 'weak-landing'; a "
        "plain declarative ending is fine. Never flag 'weak-landing' or 'weak-opening' on a "
        "draft of one or two sentences that delivers its information directly. If a sentence "
        "merely sits oddly next to its neighbor, that is the adjacency lens's lane."
    ),
}

def build_lens_prompt(lens, draft, context="social"):
    """Build the single structured-call prompt for one lens agent in the fan-out.

    Each lens is its own backend call (its raw output IS that agent's trace). Output shape is
    fixed by tests/lens_contract.md: a JSON array of {"category", "quote"} findings, using only
    that lens's allowed categories. Calibration blocks bias each lens toward precision: in a
    fan-out, an out-of-lane or borderline flag is a false positive another lens's owner would
    have handled.
    """
    idx = LENS_ORDER.index(lens) + 1
    other_lenses = ", ".join(l for l in LENS_ORDER if l != lens)
    if lens == "tells":
        cats = "\n".join(f"- {k}: {v}" for k, v in TELLS.items())
    else:
        cats = "\n".join(f"- {k}: {v}" for k, v in ARC_LENS_CATEGORY_DESCRIPTIONS[lens].items())
    return (
        f"You are one reviewer in a four-lens fan-out over a piece of writing, run bottom-up: "
        f"tells -> adjacency -> paragraph-arc -> whole-arc. You are lens {idx} of 4: '{lens}'.\n"
        f"Flag ONLY issues that belong to the '{lens}' lens, using ONLY the category ids below. "
        f"Each other lane ({other_lenses}) has its own reviewer: a defect you notice outside "
        f"your lane WILL be caught by its owner, and reporting it yourself, or re-describing it "
        f"in your own categories, is a false positive that costs the review.\n\n"
        f"Precision over recall. Most drafts are clean at most lenses. Flag a finding only when "
        f"a careful human editor would agree it is a real defect at your granularity; if you "
        f"are unsure, or the draft reads fine through your lens, output []. An empty array is "
        f"the normal answer, not a failure.\n\n"
        "Allowed categories for this lens (use these ids EXACTLY, and only these):\n" + cats + "\n\n"
        f"The draft is a {context} piece. " + ARC_LENS_CALIBRATION[lens] + "\n\n"
        "For each issue you find, quote the exact offending span verbatim from the draft.\n\n"
        "Output ONLY a JSON array of findings, each shaped exactly "
        '{"category": "<id from the list above>", "quote": "<verbatim offending span>"}. '
        "Output [] if this lens finds nothing to flag. No prose, no explanation, no markdown "
        "fences, just the JSON array.\n\n"
        f"DRAFT:\n{draft}\n"
    )

def build_prompt(draft, context="social"):
    lines = "\n".join(f"- {k}: {v}" for k, v in TELLS.items())
    return (
        "You are running the 'highsignal' writing skill in DETECT mode.\n"
        "Given the DRAFT, decide which of these AI-writing tells it contains.\n"
        "Only use ids from this exact list:\n" + lines + "\n\n"
        f"The draft is a {context} piece. 'em-dash' counts in any medium when the density "
        "is high (more than ~1 per 100 words); a single em dash in long-form prose is fine. "
        "A colon introducing a genuine list is NOT 'label-colon'. "
        "'vision-abstraction' applies only to positioning that swaps the concrete outcome for an "
        "abstract label; a category noun used as a plain literal referent (\"moved off the legacy "
        "platform\") is NOT vision-abstraction. "
        "Check 'filler' deliberately, sentence by sentence: if deleting a sentence would lose no "
        "information because it only restates or dramatizes what an adjacent sentence already "
        "establishes, flag 'filler' — models under-call this one. A sentence carrying its own "
        "concrete fact (a count, a cause, a duration) is not filler. Judge accordingly.\n\n"
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

def _bracket_matched_arrays(text):
    """Yield every top-level '[...]' substring of text, matched by depth (bracket/quote aware).

    Unlike a `[^\\[\\]]*` regex, this tolerates '[' or ']' characters inside a quoted `quote`
    field (e.g. a finding whose offending span itself contains a bracket).
    """
    n = len(text)
    i = 0
    while i < n:
        if text[i] == "[":
            depth, in_str, esc, j = 0, False, False, i
            while j < n:
                c = text[j]
                if in_str:
                    if esc:
                        esc = False
                    elif c == "\\":
                        esc = True
                    elif c == '"':
                        in_str = False
                else:
                    if c == '"':
                        in_str = True
                    elif c == "[":
                        depth += 1
                    elif c == "]":
                        depth -= 1
                        if depth == 0:
                            yield text[i : j + 1]
                            break
                j += 1
            i = j + 1
        else:
            i += 1

def parse_findings(text):
    """Parse a lens agent's raw output into a list of {"category","quote"} findings.

    Returns [] for "found nothing", a list of findings for real hits, or None if no candidate
    substring parses as a valid findings array (treated as an adherence FAIL, since a lens that
    can't be scored isn't in-lane by construction).
    """
    for cand in reversed(list(_bracket_matched_arrays(text))):
        try:
            v = json.loads(cand)
        except Exception:
            continue
        if not isinstance(v, list):
            continue
        out, ok = [], True
        for item in v:
            if isinstance(item, dict) and "category" in item:
                out.append({"category": str(item["category"]).strip(),
                            "quote": str(item.get("quote", "")).strip()})
            else:
                ok = False
                break
        if ok:
            return out
    return None

# ---- deterministic adherence + outcome scoring (tests/lens_contract.md) ----

def lens_adherence(lens, findings):
    """A lens is in-lane (adherence PASS) iff every finding's category is in its allowed set.

    Pure set-membership, no model in the loop. `findings is None` (unparseable output) is
    scored as drift/FAIL: an unscoreable lens cannot be certified in-lane.
    """
    if findings is None:
        return False
    allowed = ARC_LENSES[lens]
    return all(f.get("category") in allowed for f in findings)

def case_adherence(lens_outputs):
    """Case-level adherence PASS iff all four lenses are in-lane."""
    return all(lens_adherence(lens, lens_outputs.get(lens)) for lens in LENS_ORDER)

def case_outcome(case, lens_outputs):
    """Deterministic outcome per tests/lens_contract.md.

    Planted case: the expected lens emitted >=1 finding with the expected category AND every
    other lens emitted []. Clean case: every lens emitted [].
    """
    def empty(lens):
        f = lens_outputs.get(lens)
        return isinstance(f, list) and len(f) == 0

    if case.get("expect_lens") is None:
        return all(empty(l) for l in LENS_ORDER)
    expect_lens = case["expect_lens"]
    expect_cat = case["expect_category"]
    findings = lens_outputs.get(expect_lens)
    expected_hit = isinstance(findings, list) and any(f.get("category") == expect_cat for f in findings)
    others_quiet = all(empty(l) for l in LENS_ORDER if l != expect_lens)
    return expected_hit and others_quiet

# ---- backends: prompt -> raw text ----
def call_codex(prompt, model):
    out = subprocess.run(["codex", "exec", "--skip-git-repo-check", prompt],
                         capture_output=True, text=True, timeout=600)
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

# ---- --arc: lens fan-out runner ----

def run_lens(fn, model, case, lens, trace_dir, fresh):
    """Run (or replay) one lens agent's call for one case; that raw output IS its trace.

    Caches the raw transcript at tests/traces/<case>/<lens>.txt and replays it on a later
    invocation unless --fresh is passed, so `--trace arize` can reuse a prior `--trace
    transcript` run instead of re-spending codex calls on the same cases.
    """
    case_dir = os.path.join(trace_dir, case["id"])
    os.makedirs(case_dir, exist_ok=True)
    trace_path = os.path.join(case_dir, f"{lens}.txt")
    if not fresh and os.path.exists(trace_path):
        raw = open(trace_path).read()
    else:
        prompt = build_lens_prompt(lens, case["draft"], case.get("context", "social"))
        raw = fn(prompt, model)  # propagates codex usage-limit RuntimeError; never scored as []
        with open(trace_path, "w") as f:
            f.write(raw)
    return parse_findings(raw), trace_path

def run_arc(a):
    fn = BACKENDS[a.backend]
    cases = [json.loads(l) for l in open(a.arc_cases) if l.strip()]
    print(f"\narc eval — backend={a.backend} model={a.model or '(default)'} "
          f"cases={len(cases)} trace={a.trace}\n")

    results = []
    for case in cases:
        lens_outputs, parse_errors = {}, []
        for lens in LENS_ORDER:
            findings, _ = run_lens(fn, a.model, case, lens, a.trace_dir, a.fresh)
            if findings is None:
                parse_errors.append(lens)
            lens_outputs[lens] = findings
        adherence = {lens: lens_adherence(lens, lens_outputs[lens]) for lens in LENS_ORDER}
        c_adherence = all(adherence.values())
        outcome = case_outcome(case, lens_outputs)
        results.append({
            "case": case, "lens_outputs": lens_outputs, "adherence": adherence,
            "case_adherence": c_adherence, "outcome": outcome,
            "fully_pass": c_adherence and outcome, "parse_errors": parse_errors,
        })
        adh_str = " ".join(f"{l}={'PASS' if adherence[l] else 'FAIL'}" for l in LENS_ORDER)
        print(f"  {case['id']:>4} [{case['kind']:>7}]  adherence[{adh_str}]  "
              f"outcome={'PASS' if outcome else 'FAIL'}  "
              f"case={'PASS' if (c_adherence and outcome) else 'FAIL'}")
        if parse_errors:
            print(f"        ! unparseable lens output (scored adherence FAIL): {', '.join(parse_errors)}")

    n_lens_checks = len(cases) * len(LENS_ORDER)
    n_adh_pass = sum(1 for r in results for l in LENS_ORDER if r["adherence"][l])
    adherence_rate = n_adh_pass / n_lens_checks if n_lens_checks else 1.0

    planted = [r for r in results if r["case"].get("expect_lens") is not None]
    clean = [r for r in results if r["case"].get("expect_lens") is None]
    P = len(planted)
    planted_pass = sum(1 for r in planted if r["outcome"])
    planted_outcome_rate = (planted_pass / P) if P else 1.0
    clean_quiet = all(r["outcome"] for r in clean) if clean else True

    gate = (adherence_rate == 1.0) and (P == 0 or planted_pass >= P - 1) and clean_quiet

    print(f"\n  adherence rate:       {n_adh_pass}/{n_lens_checks} = {adherence_rate:.0%}  (gate: 100%)")
    if P:
        print(f"  planted outcome rate: {planted_pass}/{P} = {planted_outcome_rate:.0%}  "
              f"(gate: >= {P-1}/{P} = {(P-1)/P:.0%})")
    else:
        print("  planted outcome rate: n/a (no planted cases)")
    print(f"  clean cases quiet:    {sum(1 for r in clean if r['outcome'])}/{len(clean)}  (gate: 100%)")
    print(f"  GATE: {'PASS' if gate else 'FAIL'}  (exit {0 if gate else 1})\n")

    if a.trace == "arize":
        write_arize_trace(results, a)

    return 0 if gate else 1

# ---- --trace arize: hand-rolled OTLP/HTTP-over-fetch (urllib POST), no OTel SDK ----

def _otlp_attr_value(value):
    if isinstance(value, bool):
        return {"boolValue": value}
    if isinstance(value, int):
        return {"intValue": value}
    if isinstance(value, float):
        return {"intValue": int(value)} if value == int(value) else {"doubleValue": value}
    return {"stringValue": str(value)}

def _attrs_to_otlp(attrs):
    return [{"key": k, "value": _otlp_attr_value(v)} for k, v in attrs.items()]

def build_arize_payload(results, backend, trace_dir, project_name):
    """One trace per case, one span per lens (exactly len(results)*4 spans total)."""
    now_ns = time.time_ns()
    spans = []
    for r in results:
        trace_id = secrets.token_hex(16)
        case_id = r["case"]["id"]
        for lens in LENS_ORDER:
            attrs = {
                "case_id": case_id,
                "lens": lens,
                "backend": backend,
                "trace_path": os.path.join(trace_dir, case_id, f"{lens}.txt"),
                "adherence": "PASS" if r["adherence"][lens] else "FAIL",
                "outcome": "PASS" if r["outcome"] else "FAIL",
                "arize.project.name": project_name,
            }
            spans.append({
                "traceId": trace_id,
                "spanId": secrets.token_hex(8),
                "name": f"lens.{lens}",
                "kind": 1,
                "startTimeUnixNano": str(now_ns),
                "endTimeUnixNano": str(now_ns),
                "attributes": _attrs_to_otlp(attrs),
                "status": {"code": 1},
            })
    return {
        "resourceSpans": [{
            "resource": {"attributes": _attrs_to_otlp({
                "service.name": "highsignal-arc-eval", "arize.project.name": project_name})},
            "scopeSpans": [{"scope": {"name": "highsignal-arc-eval"}, "spans": spans}],
        }]
    }

def post_to_arize(payload, endpoint, api_key, space_id):
    url = endpoint if endpoint.startswith(("http://", "https://")) else f"https://{endpoint}"
    if not url.rstrip("/").endswith("/v1/traces"):
        url = url.rstrip("/") + "/v1/traces"
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), method="POST",
        headers={"Content-Type": "application/json", "authorization": f"Bearer {api_key}",
                 "space_id": space_id})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, ""
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")
    except Exception as e:
        return None, str(e)

def write_arize_trace(results, a):
    """Always write the OTLP JSON locally; POST only if Arize creds are present in env.

    Live creds are never required to pass the eval — this must not crash without them.
    """
    project = os.environ.get("ARIZE_ARC_PROJECT", "highsignal-arc-eval")
    payload = build_arize_payload(results, a.backend, a.trace_dir, project)
    n_spans = sum(len(ss["spans"]) for rs in payload["resourceSpans"] for ss in rs["scopeSpans"])
    out_path = a.arize_out or os.path.join(a.trace_dir, "arize_export.json")
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"  arize trace: wrote {n_spans} spans -> {out_path}")

    api_key = os.environ.get("ARIZE_API_KEY")
    space_id = os.environ.get("ARIZE_SPACE_ID")
    endpoint = os.environ.get("ARIZE_ENDPOINT", "otlp.arize.com:443")
    if api_key and space_id:
        status, detail = post_to_arize(payload, endpoint, api_key, space_id)
        if isinstance(status, int) and 200 <= status < 300:
            print(f"  arize trace: POSTed to {endpoint} project={project} -> HTTP {status}")
        else:
            print(f"  arize trace: POST attempted to {endpoint} but failed -> {status} {detail}")
    else:
        print("  arize trace: ARIZE_API_KEY/ARIZE_SPACE_ID not set; local-only, did not POST")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", required=True, choices=BACKENDS)
    ap.add_argument("--model", default=None)
    ap.add_argument("--cases", default=os.path.join(os.path.dirname(__file__), "cases.jsonl"))
    ap.add_argument("--arc", action="store_true",
                     help="run the four-lens narrative-arc fan-out instead of the tell eval")
    ap.add_argument("--arc-cases", default=os.path.join(os.path.dirname(__file__), "arc_cases.jsonl"))
    ap.add_argument("--trace", choices=["transcript", "arize"], default="transcript",
                     help="transcript (default): tests/traces/<case>/<lens>.txt + table. "
                          "arize: additionally emit an OTLP JSON export (POSTs only if "
                          "ARIZE_API_KEY/ARIZE_SPACE_ID are set).")
    ap.add_argument("--trace-dir", default=os.path.join(os.path.dirname(__file__), "traces"))
    ap.add_argument("--arize-out", default=None,
                     help="path for the OTLP JSON file (default <trace-dir>/arize_export.json)")
    ap.add_argument("--fresh", action="store_true",
                     help="ignore any cached tests/traces/<case>/<lens>.txt and re-call the backend")
    a = ap.parse_args()
    if a.arc:
        sys.exit(run_arc(a))
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
