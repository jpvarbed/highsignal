---
name: highsignal
description: 'Strip AI tells and filler from writing and rewrite in a plain human voice. Use when drafting or editing a tweet, thread, LinkedIn post, email, or doc and you want high signal and no slop: lead with the real hook, cut throat-clears, manufactured quotability, parataxis, "it''s not just X, it''s Y", em dashes in posts, business-speak, and filler. Supports detect-only and rewrite modes. Trigger when the user says "clean this up", "make it sound human", "cut the slop", "tighten this post", or "does this read like AI".'
license: MIT
compatibility: Any agent that reads a SKILL.md (Claude Code, Cursor, Copilot, etc.). No external tools required.
metadata:
  author: Jason Varbedian
---

# highsignal: write like a sharp human

Goal: high signal, no filler. Cut the AI tells, keep the one true sharp thing, lead with a
real hook. The output should read like a sharp person wrote it, not a model.

## The principle

Assume the reader is intelligent and patient. Don't try to sound insightful. Every claim
should come from reasoning, not assertion. If a sentence sounds like ad copy, cut it.

Read-aloud test: would you say this sentence to another person's face? If it sounds like
marketing, rewrite it.

## The review

Work top down. A quick edit is one pass through the four levels; product-critical writing
(anything published or sent under the author's name) gets full passes plus the fan-out below.

1. **Whole-piece arc.** State the spine in one sentence. The first sentence earns the read: the
   true thing that most updates what the reader currently believes, moved to the front, never
   manufactured. The last sentence lands. Every paragraph moves the spine forward.
2. **Paragraph arc.** One job per paragraph, with a shape. Delete any paragraph whose removal
   loses nothing. Cut any that restates the one before it.
3. **Sentence prose.** Each sentence in its tightest form; for anything carrying fat, offer the
   shorter version. Vary sentence length. Read-aloud test: would a sharp person say this to
   another person's face?
4. **Sentence tells.** Scan every sentence against the tells below and the avoid-ai-writing
   detector; ship at 0 / Clean.

**Hard rules.** Remove throat-clears, label-colons, and weird punctuation (em dashes: at most
~1 per 100 words, ideally none). Cutting is the default; anything added must add information.
Always offer the more concise wording.

**Grill gate.** If the arc won't state and the fix isn't in the text, don't invent one. In
rewrite mode, ask the author (companion: `grilling`) for the one point, the reader, and the next
action, then restructure from the answers. In detect mode, flag "arc unclear" and list those
three questions instead.

**Adversarial fan-out (product-critical only).** Don't review important prose once. Fan out one
reviewer per lens (arc, concision, tells, hook, read-aloud), synthesize, verify each finding
against the text before applying. This is the review-council pattern aimed at prose.

## The tells (detect and fix)

**Throat-clear** — a soft setup that delays the point to fake anticipation: "One thing that
helps:", "Here's what works:", "What I found is:". Cut the setup, lead with the point.
- Before: "One thing that reliably helps: specifying an output format."
- After: "Specifying an output format helps."

**Label-colon** — a colon that fakes a beat before a short payoff: "My hardest problem: sales."
A throat-clear in punctuation form. Write the plain sentence.
- Before: "My hardest problem: sales."
- After: "Sales is my hardest problem."

**Claimed emotion** — "what surprised me", "I was fascinated to find". The fact carries it;
cut the claim.

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

**Em-dash overuse** — at most ~1 per 100 words, ideally none, in any medium (not only posts).
A period or comma reads more human, and the avoid-ai-writing detector flags higher density as the
`em-dash` tell. Multiple em dashes in a short piece is one of the loudest AI tells there is.

**Markdown in tweets** — `*italics*` and `**bold**` render as literal asterisks on X, and `#`
makes a hashtag, not a header. Don't use markdown emphasis in a post.

**real / actual as an intensifier** — "the real bottleneck", "actual results". Name what makes
it so, or drop the word.

## Modes

- **detect.** Flag the tells with the offending text quoted; don't rewrite. Use to audit
  someone else's writing or decide what to fix yourself.
- **rewrite** (default). Fix the tells, return the clean version, and list what changed.

## Worked examples

Longer-form before/after for a whole genre, when the atomic tells above aren't enough:

- [`examples/cold-outreach-email.md`](examples/cold-outreach-email.md): cold email to an
  expert/investor: lead with their specific idea (not generic praise), show traction over
  claims, split tangled asks.

## Companions (separate skills; use alongside, don't fold in)

highsignal is the opinionated middle pass. Order: hook-writing (if you need the angle) →
highsignal → avoid-ai-writing last.

- **avoid-ai-writing** (Conor Bronsdon, MIT). A broad AI-ism vocabulary and structure pass
  with tiered word lists and context profiles; its detector is the 0 / Clean ship gate.
- **hook-writing / hook-tactics.** For generating the hook angle and choosing a tactic.
- **grilling.** The interview behind the grill gate above.

See `tests/prompts.md` for the eval set used to check this skill catches each tell without
over-flagging clean writing.
