# Digest hooks — highsignal training log

Running log of daily-dev-digest hooks. Each round: the facts, my hook, Jason's edit, and the
rule learned. Recurring rules get promoted into `SKILL.md` tells + a `tests/cases.jsonl` case.
This is the DemoEvolve seed set — Jason's corrections are the demonstrations.

---

## 2026-07-05

**Facts:** No Claude Code release, no skill updates. Fifth harness-self-improvement paper of the
week (Self-Harness, DemoEvolve, a survey) — same theme, no new info. Vercel Eve (agent = a
directory of files) and Pydantic AI V2.0 (composable Capabilities) shipped. Nothing changed the day.

**My hook (v1, slop):**
> Three independent sources landed on the same idea today: the harness improves itself.

**My hook (v2, after self-review):**
> Nothing today changes your workflow. The one thing worth 30 seconds: Pydantic AI V2.0's
> "Capabilities" — bundle a tool, its hooks, and instructions into one unit you attach to any
> agent instead of wiring each one. Everything else is the week's fifth harness-self-improvement
> paper and two framework launches you can skim if curious.

**Jason's edit:**
> Nothing today changes your workflow. Interesting add-on: Pydantic AI V2.0's "Capabilities" —
> bundle a tool, its hooks, and instructions into one unit you attach to any agent instead of
> wiring each one. Everything else is the week's fifth harness-self-improvement paper and two
> framework launches you can skim if curious.

**Rules learned:**
1. **v1 → v2:** manufactured convergence ("three sources landed on the same idea"), burying the
   one usable item, and hiding repetition instead of naming it ("fifth paper this week"). Covered
   by existing tells (manufactured-drama, hook-first).
2. **v2 → edit (NEW):** "the one thing worth 30 seconds" is a **value-teaser** — announcing that
   something deserves attention instead of just presenting it. Agents reach for a stock framing
   container and reuse it across pieces. → promoted to a `value-teaser` tell + eval case 14.

## 2026-07-06
**Facts:** Quiet day. Skills: only refinements — writing-great-skills gained Negation + Negative Space failure modes; wayfinder/grilling/to-issues tightened; avoid-ai-writing bumped; no new skills. Claude Code: still 2.1.201, no new release; local still 2.1.187. Research: "Looking Is Not Picking" (2606.16364) — agents attend to the right tool 80% of the time during mis-selection; description tweaks recover only ~23%, readout-layer fixes 59–91%. Harness-self-improvement theme saturated (5th this week), demoted. Feeds: Fabian Wesner ran Claude Code 4 days non-stop on a Fable/Opus/Haiku mix ($169–1302/day); Pietro Schirano Fable-NES-assembly demo.
**Hook:** `writing-great-skills` gained two failure modes today, both about how a skill steers the agent through words you'd read as neutral. Negation is the elephant (name what not to do → makes it more likely → prompt the positive); Negative Space is the void (declined decisions get delegated to priors → read a draft for its silences). You author skills constantly, so this earns a re-read of your own SKILL.md files. Otherwise a quiet day: no Claude Code release, no new skills, harness-self-improvement paper on its fifth entry this week.
**Jason's edit:**
**Rule:**

## 2026-07-06 manual Codex run
**Facts:** Codex reran the 2026-07-06 digest with the comms extension enabled and `COMMS_WRITEBACK=0`. Skills: `knowledge-work-plugins` fast-forwarded by one connector metadata bump; no new skills; mattpocock fetched only because local `.DS_Store` files made the checkout dirty. Claude Code: installed 2.1.201, npm registry latest 2.1.202, public changelog still tops out at 2.1.201. Research/articles: tool-selection paper says wrong-tool calls often happen after the model attended to the right tool; LangChain cost tracing post; Vercel AI SDK 7; Cloudflare Monetization Gateway/x402. Feeds skipped because no Claude-in-Chrome browser tools were connected. Added three post candidates: tool descriptions are the wrong place to fix tool choice; coding-agent cost is a trace problem; agents are getting wallets before CFO controls.
**Hook:** Your agent work is converging on one problem: keeping delegated systems accountable when they pick tools, spend tokens, or touch money. The useful thread today is not another harness paper. It is the control layer around agents: smaller tool surfaces, cost traces, human approval, and receipts.
**Jason's edit:**
**Rule:**

## 2026-07-09
**Facts:** Local harness work shipped in `dotfiles`: `4d27e09 feat(harness): escalation decider` and `0a5ecf7 feat(harness): wire the self-improving loop end-to-end`. `mattpocockskills` pulled v1.1.0, including `to-spec`, `to-tickets`, graduated `wayfinder`, graduated `code-review`, and new `research`. `plugins`, `knowledge-work-plugins`, and 12 global skills updated. Claude Code local is 2.1.201; public changelog latest is 2.1.205 with background-agent, auto-mode, worktree, MCP import, and setup-check fixes. Research/feed signal: Simon/Kenton on AI-written change descriptions omitting intent; Addy on loop engineering; Anthropic J-space; Cloudflare Code Mode MCP; Continual Harness; ARC-AGI-3 agents repo. Post candidates: AI change descriptions must preserve intent; self-improving harness as local receipt; MCP tool count as context tax.
**Hook:** The harness thread crossed from reading material into shipped local work. Tonight's useful signal is not another paper saying agents need loops. It is the concrete control surface around those loops: what changed, who approved it, what the agent saw, and whether the next run can learn from the last one.
**Jason's edit:**
**Rule:**

## 2026-07-10
**Facts:** Local receipts: HAR-43 integration fixes, review-council Cursor seat key loading from `.env.local` + BWS, trace secret-scrub work, new `gtm-diligence` skill, and Brandlens MCP v1 beta remote connector + `/v1` API. `mattpocockskills` pulled `setup-ts-deep-modules`; `knowledge-work-plugins` pulled metadata. Claude Code latest is 2.1.206 with `/doctor`, worktree confirmation, background-agent upgrade, and MCP timeout fixes. TTHE landed July 9 and matches the local harness-evolution loop. Feed signal supported Matt skills, Claude/Fable map-vs-territory framing, Claude budget warnings, Product Hunt agent launches, and Manufact MCP Cloud on HN.
**Hook:** The local harness work finally has the outside paper it needed. TTHE landed yesterday with almost the same loop you just wired: inspect execution traces, propose harness edits, judge the change, persist the better control program. The useful move today is to treat HAR-43 as a real receipt, not another generic "agents need loops" take.
**Jason's edit:**
**Rule:**
