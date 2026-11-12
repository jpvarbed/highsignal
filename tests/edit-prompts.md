# Edit and rewrite eval

Run each prompt in a fresh session. Give the baseline only the fenced prompt.
Give the treatment the same prompt with `SKILL.md` and its local references
available. Use the same model and effort. Score each condition as pass or fail
against the visible response. A case passes only if every condition passes.

## 1. Buried recommendation

```text
Can you edit this memo before I send it to our library director? It still feels
like the reader has to do too much work.

We tried two ways to remind patrons about holds. The desk team recorded pickups
for four weeks. Sending another email was easier to set up, and we could keep
using the template. The SMS pilot was harder to set up. Staff needed an extra
shift to record consent, and patrons could opt out.

Among patrons who opted in, 71 of 100 picked up their holds on time. That compares
with 54 of 100 who received a second email. We let patrons choose whether to opt
in, so the groups may have differed before we sent anything.

We should keep SMS opt-in at the two pilot branches for another month and
record staff time. Then we can decide whether to test it at another branch.
```

Pass if the response identifies the narrow decision and why the current order
makes it hard to find, provides a continuous revision that opens with the pilot
decision, and shows at least one exact before/after pair for a consequential
choice. The revision keeps the two branches, one month, staff time, opt-in
limit, both pickup counts and the caveat about group differences. The revision
must not claim SMS caused the difference or recommend a rollout.

## 2. Conflicting evidence

```text
Edit this paragraph for a council memo. I want readers to understand the case
for continuing the pilot.

During the shuttle pilot, average weekend rides rose from 80 to 110. The board
packet says the same pilot logged an average of 76 weekend rides. Riders who
answered our survey said Saturday service helped them reach the market. That
increase is why we should extend the pilot through the winter.
```

Pass if the response names the 110 versus 76 conflict, explains why the
extension cannot rest on an unverified increase, and asks for the one source
or definition needed to resolve it. Any proposed copy keeps the survey finding
limited to respondents and avoids choosing, averaging, or explaining away the
two numbers without evidence.

## 3. Clean draft with a deliberate voice

```text
Tighten this for an engineering update. Return just the copy.

We paused the migration, not the cleanup. Old snapshots still expire after 30
days. Keep the dry-run flag on until we’ve checked the restore in staging.
```

Pass if the response returns only the draft, keeps the contrast between the
migration and the cleanup, preserves the 30-day retention and restore
condition, and leaves the plain directive and exact flag name intact. A
harmless spelling or formatting change is acceptable.

## 4. Feedback on one selected paragraph

```text
I'm reviewing a Google Doc. Give me feedback only on the middle paragraph. The
other paragraphs are context. You can show proposed wording here.

We promised residents a decision on the playground by June. The Parks
Committee has the final vote.

The drainage plan is still pending. This makes it harder to know when we can
finish. The June vote should proceed if Public Works delivers the drainage
plan by May 15.

If the committee votes in June, construction could start in September.
```

Pass if the response states what the selected paragraph is trying to convey,
identifies the vague sentence or delayed condition, and shows an exact before
and proposed after drawn from that paragraph. It preserves the conditional
May 15 deadline and leaves the first and last paragraphs alone. It does not
claim to have changed the Google Doc or start a comment or suggestion thread.

## 5. Clean copy with a conflict

```text
Tighten this for a staff update. Return just the copy.

The order ledger lists 24 refunds for May. The billing export lists 29 refunds
for May. At this point in time, the review is still open.
```

Pass if the response returns only the draft, keeps both sentences that report
refund counts verbatim, and tightens the final sentence without changing the
status of the review.
