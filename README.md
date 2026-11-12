# highsignal

Highsignal helps you tighten prose and edit arguments without losing the author's
voice or changing what the draft claims.

It works as a `SKILL.md` for coding agents (Claude Code, Cursor, Copilot) and as a checklist
you can read and apply by hand.

## Skill card

| | |
|---|---|
| **Name** | highsignal |
| **Detect** | "Does this read like AI?" Get quoted findings without a rewrite. |
| **Rewrite** | "Tighten this without changing my voice." Get a clean draft with the smallest edits that help the reader. |
| **Edit** | "Where does my argument lose you?" Get an editorial note, a revision, and before/after examples with reasons. |

For an argument edit, highsignal reads the whole draft before changing a line.
It tells you what it thinks you're saying, where it loses the thread, and what
it would change. It gives you exact replacements you can accept, reject, or
improve. The [board memo](examples/board-memo.md) shows a buried recommendation.
The [pilot report](examples/pilot-report.md) shows how to edit an inference the
evidence can't support. Google Docs Suggesting mode and comments are opt-in.

The [skill](SKILL.md) checks the wording, how sentences connect, what each
paragraph does, and whether the whole draft makes its point. The
[revision check](references/revision-check.md) catches changes to claims
that a smoother sentence can hide. Ask for an AI-style pass to use the
[pattern guide](references/tells.md). If you supply writing samples, the
[voice guide](references/voice.md) helps separate your habits from generic style advice.

## One before/after

> Before: It's not just a calendar, it's a way to see when two talks overlap.
>
> After: The calendar shows when two talks overlap.

## Install

Copy the skill into your agent's skills directory:

```bash
git clone https://github.com/jpvarbed/highsignal
ln -s "$PWD/highsignal" ~/.claude/skills/highsignal   # Claude Code
```

Then ask: "Use highsignal to edit this draft. Tell me where you lose the thread
and show me what you'd change."

## Tests

The skill ships with a real eval harness, not just a checklist:

- [`tests/cases.jsonl`](./tests/cases.jsonl) — labeled cases: one dirty draft per tell (must
  flag it) plus clean drafts (must flag nothing). Each carries its context (social vs
  long-form), since some tells like em dashes are context-dependent.
- [`tests/eval.py`](./tests/eval.py) — runs each case through a model in detect mode and
  scores dirty-catch and clean false-positives separately. Backends: codex, anthropic,
  openrouter, fireworks.
- [`scripts/score.sh`](./scripts/score.sh) — run one or more backends.

```bash
scripts/score.sh codex
ANTHROPIC_API_KEY=… scripts/score.sh anthropic
```

The review's four lenses (`tells` → `adjacency` → `paragraph-arc` → `whole-arc`, see "The
review" in [`SKILL.md`](./SKILL.md)) have their own fan-out eval, scored deterministically
against [`tests/lens_contract.md`](./tests/lens_contract.md) with no LLM judge in the loop:

- [`tests/arc_cases.jsonl`](./tests/arc_cases.jsonl) — 5 planted cases (one issue planted at a
  specific lens) + 2 clean cases.
- `tests/eval.py --arc` — runs each case through all four lenses, scores adherence (did the
  lens stay in its own category set) and outcome (did the expected lens catch it, quietly),
  and prints both aggregate rates.
- [`tests/test_lens_contract.py`](./tests/test_lens_contract.py) — deterministic-scorer unit
  tests (poison control + a clean-case false-positive check), no network calls.

```bash
python3 tests/eval.py --arc --backend codex --trace transcript   # writes tests/traces/<case>/<lens>.txt
python3 tests/eval.py --arc --backend codex --trace arize         # + OTLP JSON export
python3 tests/test_lens_contract.py
```

The legacy eval prompts are embedded in the runner. They test detection and the first
pass of the four lenses. They do not load the installed skill or test the final revision.

Latest cross-model results: [`tests/RESULTS.md`](./tests/RESULTS.md).

The [editorial eval prompts](tests/edit-prompts.md) cover structure, evidence
conflicts, voice preservation, and scoped feedback. See the [editorial eval results](tests/EDIT-RESULTS.md)
for the baseline, revised skill, and remaining mistakes.

## Companions

Use a companion when the task calls for it.

- [`avoid-ai-writing`](https://github.com/conorbronsdon/avoid-ai-writing) by Conor Bronsdon
  (MIT) — a broader vocabulary and structure audit for an explicit AI-style pass.
- A hook-writing skill — for generating the hook angle before you tighten it.

These are separate skills with their own licenses; highsignal links to them rather than
copying them.

## Credits

- Oskar Austegard's Declauding informed the revision check, the distinction
  between tics and deliberate choices, and the read for someone new to the
  document. The revision check quotes its ranking example.
  [Declauding v0.13.0](https://github.com/oaustegard/claude-skills/releases/tag/declauding-v0.13.0)
- [RPI Prose](https://github.com/humanlayer/skills/blob/main/plugins/rpi/skills/rpi/references/prose.md)
  by HumanLayer informed the guidance on plain words, precise names, and clear referents.
- [Natural Voice](https://github.com/hcastro/agent-artifacts/tree/main/skills/natural-voice)
  by Henry Castro informed the voice guide and the second read after revision.

## License

MIT. See [LICENSE](LICENSE). The revision check attributes the example quoted from Declauding.
