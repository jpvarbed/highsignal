# highsignal

A writing skill that strips AI tells and filler, and rewrites in a plain human voice. Run a
draft through it and you get high signal, no slop: the real hook up front, the throat-clears
and manufactured depth gone, the writing sounding like a sharp person wrote it.

It works as a `SKILL.md` for coding agents (Claude Code, Cursor, Copilot) and as a checklist
you can read and apply by hand.

## Skill card

| | |
|---|---|
| **Name** | highsignal |
| **Does** | Detects and rewrites AI tells + filler in tweets, threads, posts, emails, docs |
| **Use when** | "clean this up", "make it sound human", "cut the slop", "does this read like AI" |
| **Modes** | `detect` (flag only) · `rewrite` (fix + show changes) |
| **Inputs** | A draft, an optional target (tweet / LinkedIn / email / doc) |
| **Output** | Flagged tells, or a rewritten draft with a change list |
| **Not for** | Generating a draft from nothing, or fact-checking. It sharpens what you wrote. |

## The goal

High signal, no filler. Cut the AI tells, keep the one true sharp thing, lead with a real hook.

One principle underneath all of it: assume the reader is intelligent and patient. Don't try to
sound insightful. Every claim should come from reasoning, not assertion. If a sentence sounds
like ad copy, cut it.

## The three passes

1. **Find the hook** — the most surprising true thing, moved to the front and tightened.
2. **Cut the tells** — throat-clears, manufactured quotability, parataxis, "it's not just X,
   it's Y", filler, abstract-over-concrete, business-speak, vision-speak over outcomes, em dashes in posts.
3. **Cleanup** — vocabulary, length, rhythm.

The full list, with before/after for each tell, lives in [`SKILL.md`](./SKILL.md).

## One before/after

> Before: It's not just a planner — it's a way to never miss a talk.
>
> After: A planner that resolves the time conflicts for you.

## Install

Copy the skill into your agent's skills directory:

```bash
git clone https://github.com/jpvarbed/highsignal
ln -s "$PWD/highsignal" ~/.claude/skills/highsignal   # Claude Code
```

Then ask your agent to "clean up this draft with highsignal" or "detect the AI tells in this."

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

Latest cross-model results: [`tests/RESULTS.md`](./tests/RESULTS.md).

## Companions

highsignal is the opinionated middle pass. Pair it with:

- [`avoid-ai-writing`](https://github.com/conorbronsdon/avoid-ai-writing) by Conor Bronsdon
  (MIT) — a broader AI-ism vocabulary and structure pass. Run it last.
- A hook-writing skill — for generating the hook angle before you tighten it.

These are separate skills with their own licenses; highsignal links to them rather than
copying them.

## License

MIT — see [LICENSE](./LICENSE). The checklist and examples are original; the companion skills
above remain under their own authors and licenses.
