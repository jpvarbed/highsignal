---
name: highsignal
description: 'Strip AI tells and filler from writing and rewrite in a plain human voice. Use when drafting or editing a tweet, thread, LinkedIn post, email, or doc and you want high signal and no slop: lead with the real hook, cut throat-clears, manufactured quotability, parataxis, "it''s not just X, it''s Y", em dashes in posts, business-speak, and filler. Supports detect-only and rewrite modes. Trigger when the user says "clean this up", "make it sound human", "cut the slop", "tighten this post", or "does this read like AI".'
license: MIT
compatibility: Any agent that reads a SKILL.md (Claude Code, Cursor, Copilot, etc.). No external tools required.
metadata:
  author: Jason Varbedian
---

# highsignal — write like a sharp human

Goal: high signal, no filler. Cut the AI tells, keep the one true sharp thing, lead with a
real hook. The output should read like a sharp person wrote it, not a model.

## The principle

Assume the reader is intelligent and patient. Don't try to sound insightful. Every claim
should come from reasoning, not assertion. If a sentence sounds like ad copy, cut it.

Read-aloud test: would you say this sentence to another person's face? If it sounds like
marketing, rewrite it.

## The three passes

Run a draft through these in order:

1. **Find the hook** — the most surprising true thing you already wrote, moved to the front
   and tightened. Don't manufacture it. If you have to invent drama, you buried the real point.
2. **Cut the tells** — the list below.
3. **Cleanup** — vocabulary, length, and rhythm (vary sentence length; avoid a flat row of
   equal-length lines).

## The tells (detect and fix)

**Throat-clear** — a soft setup that delays the point to fake anticipation: "One thing that
helps:", "Here's what works:", "What I found is:". Cut the setup, lead with the point.
- Before: "One thing that reliably helps: specifying an output format."
- After: "Specifying an output format helps."

**Claimed emotion** — "what surprised me", "I was fascinated to find". If it's surprising, the
fact carries it. Cut the claim.

**Manufactured drama** — a tease dressed as a hook ("a tool that refuses to…"). Lead with the
actual finding instead.

**Manufactured quotability** — a closer built to sound deep, asserting a vibe instead of
earning it. Tell: it would fit on a poster but doesn't follow from anything you argued.
- Before: "The fat was always the point. The salad was just keeping it company."
- After: cut it, or state the reasoning that should have led there.

**Parataxis** — short clauses stacked with no conjunction, so the juxtaposition implies a
connection you never made. State the relationship (because / so / but), or merge into one
sentence. https://en.wikipedia.org/wiki/Parataxis

**"It's not just X, it's Y"** — fake elevation: demote the literal thing to crown a grander
one. Just say what it is.
- Before: "It's not just a planner, it's a way to never miss a talk."
- After: "A planner that resolves the time conflicts for you."

**Filler** — a sentence that carries no information. Tell: delete it and nothing is lost.
- Before: "There are 300 talks. You can't see them all."
- After: "551 talks. A few I'm not missing:"

**Abstract framing over a number** (lower-confidence) — a vague magnitude word ("a lot",
"huge", "tons", "many", "way more") sits where a real number belongs. This is a rewrite hint,
not a hard error: flag it only when a concrete figure is actually available and would clearly
land harder. Don't flag ordinary informal writing. (In testing, both Claude and Codex catch
this inconsistently, so treat it as a suggestion, not a verdict.)
- Before: "We got a huge number of signups this week."
- After: "We got 4,200 signups this week."

**Business-speak** — lever, unlock, leverage, move the needle, supercharge. Use the plain verb.

**Em dashes in posts** — on social, a period or colon reads more human. (In long-form prose
they're fine in moderation.)

**Markdown in tweets** — `*italics*` and `**bold**` render as literal asterisks on X, and `#`
makes a hashtag, not a header. Don't use markdown emphasis in a post.

**real / actual as an intensifier** — "the real bottleneck", "actual results". Name what makes
it so, or drop the word.

## Modes

- **detect** — flag the tells with the offending text quoted; don't rewrite. Use to audit
  someone else's writing or decide what to fix yourself.
- **rewrite** (default) — fix the tells, return the clean version, and list what changed.

## Companions (separate skills — use alongside, don't fold in)

highsignal is the opinionated middle pass. It pairs with:

- **avoid-ai-writing** (Conor Bronsdon, MIT) — a broad AI-ism vocabulary and structure pass
  with tiered word lists and context profiles. Run it last for the general cleanup.
- **hook-writing / hook-tactics** — for generating the hook angle and choosing a tactic.

See `tests/prompts.md` for the eval set used to check this skill catches each tell without
over-flagging clean writing.
