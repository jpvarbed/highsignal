---
name: highsignal
description: 'Draft, revise, or audit prose for clarity and natural voice. Use for posts, emails, essays, docs, and PR descriptions when asked to tighten a draft, make it sound like the writer, check for AI tells, or give editorial feedback on the argument or structure. Use detect to flag issues, rewrite to polish, and edit to explain where the argument loses the reader and show how to fix it.'
license: MIT
compatibility: Any agent that reads a SKILL.md (Claude Code, Cursor, Copilot, etc.). No external tools required.
metadata:
  author: Jason Varbedian
---

# highsignal

Keep the original wording by default. Change a passage when you can point to
a specific problem for its reader or a style constraint the author asked for.
Make the smallest change that solves it. Give a claim room when cutting makes
it harder to understand.

## Follow the request

- **Detect:** Quote the problems and say what they cost the reader. Leave the draft alone.
- **Rewrite** (default for polish or a voice pass): Return a clean draft. Briefly explain
  substantial changes. If the user asks for clean copy only or calls this from another
  workflow, return only the draft. When revising an existing draft, copy each sentence
  with a conflicting or unresolved claim verbatim. Follow this output rule throughout
  the review, including when a reference guide calls for a question or separate note.
  When drafting from supplied material, check it for disagreements first.
  Keep unresolved claims attributed to their sources in the draft. Then run this pass.
  If the wording already works, keep it.
- **Edit:** For feedback on an argument, structure, or reader experience, start
  with [the edit procedure](references/edit.md). Do that before polishing any
  sentences. If the user asks for a light copyedit, use rewrite and keep the
  structure.

If the user provides or asks for a voice profile or writing samples, read
[the voice guide](references/voice.md). Otherwise take your cues from the draft and its
audience. Read surrounding text to understand a selection, then stay within it.

When the user asks to find or remove AI-style patterns, use the
[pattern guide](references/tells.md). For ordinary polish, use the checks below.

## Decide whether to change the line

1. Quote the words that cause a problem. Say what the reader would misread,
   have to work out, or wait too long to learn. A familiar pattern can prompt
   a closer look. Keep the words when the pattern is all you can name, unless
   it violates a style constraint the author asked for.
2. Try the smallest fix. Keep useful fragments in notes, headlines, captions,
   and social posts. Keep the author's emphasis, contrast, and informal
   phrasing. Prefer a local cut or clearer word over replacing the sentence.
3. Check what the new wording commits the writer to. Keep each distinct
   claim and its strength, scope, conditions, and voice. Use context to
   resolve references and check claims. If you can't fix a problem without
   changing a claim or guessing, keep the passage.

## The review

Read the whole draft before changing a line. State its point in one sentence for yourself.
Identify the reader and what the draft wants them to understand or do. Keep facts,
names, numbers, attribution, rankings, scope, conditions, negation and uncertainty.
Preserve quotations, code, frontmatter and link targets. Use specifics from the draft or
supplied material. When the request allows commentary, flag conflicts or unsupported
claims separately. If two plausible readings require different edits, ask the one
question that resolves them when the request allows it.

For detection and polish, use four lenses: `tells`, `adjacency`, `paragraph-arc`
and `whole-arc`. For an argument edit, use the lenses that help after you've
worked through the claim and its evidence.
Each lens catches a break at a different scale, from a single sentence up to the whole piece,
and stays inside its own lane rather than re-grading what the lens below or above it already
covers.

1. `tells` checks for wording that hides, repeats, or delays the point. Use
   the pattern guide for a requested AI-style pass. Keep contrasts that
   rule out a real alternative, lists whose items matter, deliberate asides,
   and the writer's judgments.
2. `adjacency` checks whether each sentence follows from the one before it. It flags a
   non-sequitur when two adjacent sentences share no logical link, a missing connective when
   the link exists but the reader has to supply "because," "so," or "but" that the draft never
   states, a broken referent when a pronoun at a sentence boundary could point to more than one
   antecedent, and a local contradiction when adjacent sentences conflict. This lens is broader
   than the parataxis tell: parataxis stays a sentence-level tell under `tells`, adjacency is
   the general sentence-to-sentence flow check, and some overlap between the two is expected.
3. `paragraph-arc` asks whether each paragraph does one job and has a shape. It
   flags paragraphs whose removal loses nothing and paragraphs that repeat a point.
4. `whole-arc` checks the order against the point. Lead with the finding, request or
   recommendation the reader needs. Keep a slower opening when the reader needs its
   context. Check that each paragraph advances the point and the ending does its job.
   For a README, guide, or report written after a change, check that it makes
   sense to someone who never saw the old version. When an independent reader
   is available, give them the current section alone and ask where they get stuck.

The first pass finds problems. Each lens quotes the passage and explains the problem.
In the second pass, verify each finding in context. In detect mode, report the verified
findings. In rewrite mode, apply fixes that pass the decision above and run
the [revision check](references/revision-check.md). If nothing passes, return
the original. Reread the changed passages in context for new tics and awkward
joins. Keep useful variation in sentence length.

For routine writing, run the applicable lenses yourself. For high-stakes writing,
use one independent reviewer per applicable lens when available, then verify
and synthesize their findings. Keep this pass local unless the writer has
authorized sending the draft elsewhere.

## Worked examples

- [Board memo](examples/board-memo.md): move a recommendation to the front and
  keep the evidence beside its limit.
- [Pilot report](examples/pilot-report.md) shows how to repair an unsupported
  inference and explain what would support the stronger claim.
- [Cold outreach](examples/cold-outreach-email.md): lead with a specific idea and
  untangle two requests.

## Companions (separate skills; use alongside, don't fold in)

Use hook-writing when you need an angle. Use highsignal to edit the draft.

- **avoid-ai-writing** (Conor Bronsdon, MIT). A broad AI-ism vocabulary and structure pass
  with tiered word lists and context profiles. Use its hits as leads to verify in context.
- **hook-writing / hook-tactics.** For generating the hook angle and choosing a tactic.
- **grilling.** Use when the author wants help finding the point or choosing an argument.

See [the README](README.md#credits) for sources and [the tests](tests/) for eval cases.
