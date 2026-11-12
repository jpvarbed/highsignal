# Patterns to inspect

These examples show changes for passages with a concrete reader problem.
Use [the rewrite decision](../SKILL.md#decide-whether-to-change-the-line)
for each instance in the draft.

**Throat-clear** — a soft setup that delays the point to fake anticipation: "One thing that
helps:", "Here's what works:", "What I found is:". Cut the setup, lead with the point.
- Before: "One thing that reliably helps: specifying an output format."
- After: "Specifying an output format reliably helps."

**Label-colon** — a colon that fakes a beat before a short payoff: "My hardest problem: sales."
A throat-clear in punctuation form. Write the plain sentence.
- Before: "My hardest problem: sales."
- After: "Sales is my hardest problem."

**Value-teaser** — a phrase that announces something is worth attention instead of just
presenting it: "the one thing worth 30 seconds", "here's the kicker", "worth noting", "the
interesting part is". State what the reader came to learn.
- Before: "The one change worth 30 seconds: the importer now accepts a folder."
- After: "The importer now accepts a folder."

**Claimed emotion** — "what surprised me" can stall a finding. Keep first-person
reactions when they tell the reader something about the writer's expectations or judgment.

**Manufactured drama** — a tease dressed as a hook ("a tool that refuses to…"). Lead with the
actual finding instead.

**Manufactured quotability** — a closer built to sound deep, asserting a vibe instead of
earning it. Tell: it would fit on a poster but doesn't follow from anything you argued.
- Before: "The fat was always the point. The salad was just keeping it company."
- After: cut it, or state the reasoning that should have led there.

**Parataxis** — short clauses or sentences stacked with no conjunction can
leave the reader to invent a connection. When checking for this, look at
runs of two or more short sentences. If the link is left for the reader to
invent, flag `parataxis`. Two short sentences can work when the relationship
is clear ("The deploy failed. Reordering the steps fixed it.").

Inspect these common shapes:
- **Three-beat staccato:** three short period-separated beats, often parallel ("We X. We Y.
  We Z." / "We shipped fast. We broke things. We learned."). The third beat is the "lesson"
  the first two never earned in prose.
- **Two-sentence profundity pair:** sentence A asserts a fate ("X was always the bottleneck");
  sentence B rebrands a second actor as sidekick or foil ("Y was just along for the ride" /
  "just keeping it company" / "never the real story"). The period is doing the work of a
  conjunction you never wrote.
- **Any period-run that fails the read-aloud test:** if you'd have to insert because / so /
  but / and to say it out loud, the periods are faking the logic.

Fix: state the relationship the draft supports. If the draft leaves it open, ask rather
than supplying a causal link or an unnamed lesson.
- Before: "We skipped staging. The import broke. Restoring staging fixed it."
- After: "The import broke when we skipped staging. Restoring staging fixed it."

**"It's not just X, it's Y"** — fake elevation: demote the literal thing to crown a grander
one. Say what it does. Keep a contrast if it distinguishes two real possibilities.
- Before: "It's not just a calendar, it's a way to see when two talks overlap."
- After: "The calendar shows when two talks overlap."

**Filler** — a sentence that carries no information. Tell: delete it and nothing is lost.
- Before: "There are 300 talks. That's the number of talks on the schedule."
- After: "The schedule lists 300 talks."

**Abstract framing over a number** (lower-confidence) — a vague magnitude word ("a lot",
"huge", "tons", "many", "way more") sits where a real number belongs. This is a rewrite hint,
not a hard error: flag it only when a concrete figure is actually available and would clearly
land harder. Don't flag ordinary informal writing. (In testing, both Claude and Codex catch
this inconsistently, so treat it as a suggestion, not a verdict.)
- Before: "We got a huge number of signups this week. The count was 4,200."
- After: "We got 4,200 signups this week."

**Vision abstraction over the outcome** — an abstract category label ("platform", "layer",
"solution", "engine", "system", "intelligence") standing in for what the thing does, so the
reader has to translate it. Readers aren't allergic to vision, they're allergic to homework.
Name the concrete outcome, ideally with a number. Flag it when the label is doing positioning
work and a concrete result is available; don't flag a category noun used as a literal referent
("we moved the service off the legacy platform").
- Before: "We offer a new layer of productivity for field crews. It cut the time
  they spend writing pump inspection reports from 42 minutes to 6."
- After: "Our tool cut the time field crews spend writing pump inspection reports
  from 42 minutes to 6."

**Business-speak** — lever, unlock, leverage, move the needle, supercharge. Use the plain verb.

**Compressed syntax** — a stack of nouns or a verb buried far from its subject makes
the reader untangle the sentence. Give the actor a verb. Unpack modifiers and use the
same name for the same thing. Keep familiar names and exact terms.
- Before: "We completed the tenant access review deadline extension."
- After: "We extended the deadline for reviewing tenant access."

**Borrowed certainty** — words like "clearly" or "proved" can make limited
evidence sound conclusive. If the evidence supports a weaker claim, flag that
for the author. Cut empty hedges when doing so preserves the writer's certainty.

**Em-dash overuse** — count em dashes and lookalikes (`--` or ` - ` used as prose
punctuation). Two dashes in a short post, more than about one per 100 words, and
repeated interruption or list beats warrant a close read. Use a period, comma or
parentheses when clearer. Keep a dash that does a real job in the author's voice.

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
