# highsignal — test prompts (eval set)

Run each draft through the skill in `detect` mode. It passes a case when it flags the listed
tell (and, for clean cases, when it flags nothing). Use this to check the skill catches what
it should and doesn't over-flag what it shouldn't.

How to run it by hand: load `../SKILL.md`, paste a draft, ask "detect tells, don't rewrite",
and compare against `expect`. `scripts/score.sh` prints these cases for a batch pass.

---

## Dirty cases (must flag the named tell)

### 1 — throat-clear
> One thing that really helps with agent reliability: you specify an output format.

expect: **throat-clear** ("One thing that really helps:") → "Specifying an output format helps."

### 2 — claimed emotion
> What surprised me most was that a smaller model handled the routing just fine.

expect: **claimed emotion** ("What surprised me most"). Cut the claim; state the fact.

### 3 — manufactured drama
> I built a linter that refuses to let your code lie to you.

expect: **manufactured drama** ("refuses to"). Lead with what it does.

### 4 — manufactured quotability
> The cache was always the bottleneck. The database was just along for the ride.

expect: **manufactured quotability** + **parataxis**. Poster-ready, follows from nothing.

### 5 — parataxis
> We shipped fast. We broke things. We learned.

expect: **parataxis** — stacked clauses imply a connection never stated.

### 6 — "it's not just X, it's Y"
> It's not just a database, it's a system of record for your whole company.

expect: **"it's not just X, it's Y"** fake elevation. Say what it is.

### 7 — filler
> There were forty sessions on the schedule. You couldn't possibly attend all of them.

expect: **filler** — the second sentence carries no information. Cut it.

### 8 — abstract framing over a number
> There were so many talks happening at once that you always had to miss something good.

expect: **abstract framing** — lead with the number, not the commentary.

### 9 — business-speak
> This unlocks a step-change in velocity and lets teams leverage their existing stack.

expect: **business-speak** (unlock, leverage, step-change). Use plain verbs.

### 10 — em dashes in a post
> Our new model is faster — cheaper — and it ships today. No asterisks needed.

expect: **em dashes in posts** — replace with periods/colons for social.

### 11 — real/actual intensifier
> This is the real reason your evals are flaky and the actual fix nobody mentions.

expect: **real/actual as intensifier** — name what makes it so, or drop it.

### 12 — vision abstraction over the outcome
> We're building an AI-native intelligence layer for field operations.

expect: **vision abstraction over the outcome** — an abstract category label ("intelligence
layer") with no concrete result. Replace with what it does, ideally a number: "We cut pump
inspection reports from 42 minutes to 6."

---

## Clean cases (must flag nothing)

### C1 — plain technical finding
> Specifying an output format made the agent run more tests. Same model, same prompt.

expect: no flags. Concrete, leads with the finding, no tells.

### C2 — long-form prose with a justified em dash
> The migration took three weeks. Most of that was data backfill — the schema change itself
> landed in an afternoon — and the rollout was uneventful.

expect: no flags. One em dash in long-form prose is fine; not a social post.

### C3 — a list that is genuinely a list
> The release adds three things: resumable uploads, a dark theme, and per-row permissions.

expect: no flags. A real enumeration, not paratactic profundity.

### C4 — category noun used as a literal referent
> We moved the auth service off the legacy platform onto Workers.

expect: no flags. "platform" is a concrete referent here, not vision-speak.
