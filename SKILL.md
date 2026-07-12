---
name: highsignal
description: 'Strip AI tells and filler from writing and rewrite in a plain human voice. Use when drafting or editing a tweet, thread, LinkedIn post, email, or doc and you want high signal and no slop: lead with the real hook, cut throat-clears, value-teasers, manufactured quotability, parataxis, "it''s not just X, it''s Y", em dashes in posts, business-speak, vision-speak over concrete outcomes, and filler. Supports detect-only and rewrite modes. Trigger when the user says "clean this up", "make it sound human", "cut the slop", "tighten this post", or "does this read like AI".'
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

Four lenses, run bottom-up: `tells`, then `adjacency`, then `paragraph-arc`, then `whole-arc`.
Each lens catches a break at a different scale, from a single sentence up to the whole piece,
and stays inside its own lane rather than re-grading what the lens below or above it already
covers.

1. `tells` scans every sentence against the tells below and the avoid-ai-writing detector, and
   ships at 0 / Clean. Two checks come before calling it clean: count every em dash in the
   piece (see Em-dash overuse), and mark every run of two or more short period-separated
   sentences and check Parataxis.
2. `adjacency` checks whether each sentence follows from the one before it. It flags a
   non-sequitur when two adjacent sentences share no logical link, a missing connective when
   the link exists but the reader has to supply "because," "so," or "but" that the draft never
   states, a broken referent when a pronoun at a sentence boundary could point to more than one
   antecedent, and a local contradiction when adjacent sentences conflict. This lens is broader
   than the parataxis tell: parataxis stays a sentence-level tell under `tells`, adjacency is
   the general sentence-to-sentence flow check, and some overlap between the two is expected.
3. `paragraph-arc` asks whether each paragraph does one job and has a shape. It cuts any
   paragraph whose removal loses nothing, and any paragraph that restates the one before it.
4. `whole-arc` states the spine in one sentence. The first sentence earns the read: the true
   thing that most updates what the reader currently believes, moved to the front and never
   manufactured. The last sentence lands. Every paragraph moves the spine forward.

The review runs in two passes. Pass 1 finds: the four lenses run concurrently, and each one
reports findings scoped to its own lane, the quoted offending text plus a proposed fix, without
touching the draft itself. Pass 2 verifies and applies: for each finding, check it against the
text again, confirm it is real and that the fix keeps the meaning, drop what does not hold up,
apply what survives, then re-state the spine and confirm the arc still holds once the edits
land.

A quick edit runs one reviewer through all four lenses inline, one find pass and one verify
pass, and that is the default for throwaway writing. Product-critical writing, anything
published or sent under the author's name, runs the real fan-out instead: one reviewer per
lens for pass 1, then the same verify-and-apply sweep for pass 2. This is the review-council
pattern aimed at prose, and it is now the one product-critical path; there is no separate
adversarial pass alongside it.

Remove throat-clears, label-colons, and weird punctuation. Em dashes: at most ~1 per 100
words, ideally none; two or more in a short piece, or three or more anywhere, is always a
fail. Cutting is the default; anything added must add information, and the more concise
wording is always on offer.

If the spine will not state and the fix is not in the text, do not invent one. In rewrite
mode, ask the author (companion: `grilling`) for the one point, the reader, and the next
action, then restructure from the answers. In detect mode, flag "arc unclear" and list those
three questions instead.

## The tells (detect and fix)

**Throat-clear** — a soft setup that delays the point to fake anticipation: "One thing that
helps:", "Here's what works:", "What I found is:". Cut the setup, lead with the point.
- Before: "One thing that reliably helps: specifying an output format."
- After: "Specifying an output format helps."

**Label-colon** — a colon that fakes a beat before a short payoff: "My hardest problem: sales."
A throat-clear in punctuation form. Write the plain sentence.
- Before: "My hardest problem: sales."
- After: "Sales is my hardest problem."

**Value-teaser** — a phrase that announces something is worth attention instead of just
presenting it: "the one thing worth 30 seconds", "here's the kicker", "worth noting", "the
interesting part is". A throat-clear that packages importance. Agents reach for these as a
reflex and reuse the same container across pieces — kill it on sight. State the thing; if you
need a signpost, use a flat label ("Worth a look:") not a value claim.
- Before: "The one thing worth 30 seconds: Pydantic V2.0 bundles tools and hooks into one unit."
- After: "Worth a look: Pydantic V2.0 bundles tools and hooks into one unit."

**Claimed emotion** — "what surprised me", "I was fascinated to find". The fact carries it;
cut the claim.

**Manufactured drama** — a tease dressed as a hook ("a tool that refuses to…"). Lead with the
actual finding instead.

**Manufactured quotability** — a closer built to sound deep, asserting a vibe instead of
earning it. Tell: it would fit on a poster but doesn't follow from anything you argued.
- Before: "The fat was always the point. The salad was just keeping it company."
- After: cut it, or state the reasoning that should have led there.

**Parataxis** — short clauses or sentences stacked with no conjunction, so the juxtaposition
implies a connection you never made. Mechanical scan (do this on every piece, not only when
something "sounds punchy"): find every run of 2+ consecutive independent sentences, each under
~10 words, joined only by periods — no because / so / but / and / while / which between them.
If the link is left for the reader to invent (punchline, faux progression, poster pair), flag
`parataxis`. Do not skip the flag when another tell also fits: a profundity pair is often both
parataxis and manufactured quotability — emit both. Not parataxis when each sentence adds a
distinct fact the next one depends on ("The deploy failed. Reordering the steps fixed it.").

Always flag these shapes (canonical AI staccato):
- **Three-beat staccato:** three short period-separated beats, often parallel ("We X. We Y.
  We Z." / "We shipped fast. We broke things. We learned."). The third beat is the "lesson"
  the first two never earned in prose.
- **Two-sentence profundity pair:** sentence A asserts a fate ("X was always the bottleneck");
  sentence B rebrands a second actor as sidekick or foil ("Y was just along for the ride" /
  "just keeping it company" / "never the real story"). The period is doing the work of a
  conjunction you never wrote.
- **Any period-run that fails the read-aloud test:** if you'd have to insert because / so /
  but / and to say it out loud, the periods are faking the logic.

Fix: state the relationship, or merge into one sentence.
https://en.wikipedia.org/wiki/Parataxis
- Before: "We shipped fast. We broke things. We learned."
- After: "We shipped fast, broke things, and learned what not to do next time."
- Before: "The cache was always the bottleneck. The database was just along for the ride."
- After: "The cache was the bottleneck; the database was fine." (Flag both parataxis and
  manufactured quotability: second sentence is poster-ready and follows from nothing argued.)

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

**Vision abstraction over the outcome** — an abstract category label ("platform", "layer",
"solution", "engine", "system", "intelligence") standing in for what the thing does, so the
reader has to translate it. Readers aren't allergic to vision, they're allergic to homework.
Name the concrete outcome, ideally with a number. Flag it when the label is doing positioning
work and a concrete result is available; don't flag a category noun used as a literal referent
("we moved the service off the legacy platform").
- Before: "an AI-native intelligence layer for field operations"
- After: "we cut pump inspection reports from 42 minutes to 6."

**Business-speak** — lever, unlock, leverage, move the needle, supercharge. Use the plain verb.

**Em-dash overuse** — flag the `em-dash` tell on density and on pattern, not only "posts."
Hard ceiling: at most ~1 em dash per 100 words, ideally none in any medium. A period, comma,
or parentheses reads more human.

Mechanical scan (do this before judging "does this feel like overuse?"): search the draft for
every `—` (U+2014 EM DASH). Count them. Also catch lookalikes models paste in: `--` used as a
dash, or spaced hyphens ` - ` standing in for an em dash. Do not wait for the avoid-ai-writing
detector, and do not skip the count because the piece is "long-form" or otherwise fine.

Always flag when any of these hold (zero judgment, zero "but the rest is clean"):
- **Two or more em dashes in a short piece** (under ~50 words) — the loudest AI tell. Social
  one-liners with a pair of dashes almost always fail. Count beats, not vibes: "faster —
  cheaper — and it ships today" is two dashes in one line → flag.
- **List / appositive dashes** that replace commas in a short run: "A — B — and C". Even two
  dashes in a three-item list is enough; rewrite with commas.
- **Paired / interruptive dashes** used as fake parentheticals: "X — aside — Y" (e.g. "went
  fine — mostly — but…"). Those two count toward density; if a third dash trails later in the
  same sentence or paragraph ("…felt it — for a full week"), flag immediately.
- **Three or more em dashes in any piece**, short or long-form. Long-form is not a free pass
  and does not reset the counter. "One justified aside" means exactly one `—` in the whole
  piece when the word count is high; two paired asides plus a trailing dash is overuse.

Single em dash in long-form prose (~100+ words) used once as a genuine aside can pass; still
prefer a period when the aside can stand alone. If you counted two or more, you do not get
this exception.
- Before: "Our new model is faster — cheaper — and it ships today."
- After: "Our new model is faster, cheaper, and it ships today."
- Before: "The launch went fine — mostly — but the docs lagged and support felt it — for a
  full week."
- After: "The launch went mostly fine, but the docs lagged and support felt it for a full
  week."

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
