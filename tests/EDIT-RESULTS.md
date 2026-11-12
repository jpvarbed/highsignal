# Editorial eval results

Each arm used `gpt-5.6-sol` at requested low reasoning effort, with one run per
prompt and tools disabled. The baseline received only the draft and task.
The skill arms received the same prompt plus the skill and relevant references.
Only synthetic drafts were used.

| Frozen case | Baseline | First revision | After tuning |
| --- | --- | --- | --- |
| Buried recommendation | Fail | Fail | Pass |
| Conflicting evidence | Fail | Pass | Pass |
| Clean copy | Pass | Pass | Pass |
| Selected paragraph | Fail | Fail | Pass |
| Total | 1/4 | 2/4 | 4/4 |

The first revision asked how to reconcile two incompatible ridership counts
before citing growth. It kept both denominators in the recommendation memo.
It still omitted exact before/after pairs in the memo and selected paragraph.
After tuning the edit procedure to show explicit pairs, both cases passed.

The rubric missed changes in meaning. The tuned memo dropped the option to
opt out and assumed the four-week window applied to both groups. The shuttle
edit read a reason for extending the pilot as a claim about what caused the
increase. The selected paragraph kept the vote condition but picked a meaning
for “finish” that the draft left open.

An additional museum memo tested a causal claim about audio-guide reservations.
Both arms met the stated rubric. The baseline offered a phrase replacement
and assumed the other two groups returned the guides late. The tuned skill
showed full sentence replacements but called the measured groups school
groups. The source specified school groups only for the proposed policy.

The tuned run shows that the explicit pairs appeared on these prompts. One
sample per prompt on one model gives limited evidence about reliability.
The extra memo probes one new case after tuning. [Frozen prompts](edit-prompts.md)

## Public excerpt benchmark

The benchmark used 100 excerpts from 100 public pages. The set included
20 social posts (eight from X), 15 blog posts, 17 news articles, 18 press
releases, 15 engineering documents, and 15 excerpts from jasonv.dev.
Each excerpt contained at most 25 words. The set included both passages
with clear editing opportunities and passages that already worked.

Both arms received the same excerpt, public context, and editing request.
The Highsignal arm also received the skill and editing references. A fresh
session graded the two responses in randomized order with their labels
hidden. The editor arms and judge used GPT-5.6 Sol at requested low effort.
The judge could consider both the edit and its explanation.

| Measure | Baseline | Highsignal |
| --- | --- | --- |
| Preferred responses | 37 | 26 |
| Edits made | 46 | 64 |
| Unnecessary edits | 2 | 14 |
| Missed edits | 12 | 6 |
| Edits judged to change meaning | 2/46 | 20/64 |
| Edits judged to change voice | 1/46 | 18/64 |

The judge called 37 cases ties. On jasonv.dev, it preferred Highsignal in
four cases and baseline in two, with nine ties. Both arms received 13 useful
ratings out of 15 for those excerpts.

Highsignal caught a latency claim that contradicted its source table and
turned generic product descriptions into supported specifics. It also
strengthened an invitation for public feedback into a claim that the public
had a central role, and turned a stated purpose into a claim about results.
The earlier four prompts tested whether the editorial procedure appeared
in responses. This benchmark tested short copy edits across more genres.
It used one run per arm and one judge from the same model family.

## Retest after making polish selective

The two retests reused the same 100 excerpts and the same baseline outputs.
Each used the same model settings, judge instructions, and presentation order.
The first change required a reader problem and the smallest viable fix.
The second moved the AI-style catalogue out of ordinary polish and added
checks for claims about purpose, results, and comparison.

| Measure | Original Highsignal | First change | Selective polish |
| --- | ---: | ---: | ---: |
| Edits made | 64 | 55 | 44 |
| Edits judged to change meaning | 20 | 11 | 6 |
| Edits judged to change voice | 18 | 7 | 4 |
| Unnecessary edits | 14 | 10 | 3 |
| Missed edits | 6 | 3 | 7 |
| Useful responses | 68 | 80 | 86 |

On the final run, the judge preferred the baseline 23 times and Highsignal
23 times, with 54 ties. It rated 87 baseline responses and 86 Highsignal
responses useful. On the 15 excerpts from jasonv.dev, it preferred Highsignal
four times, the baseline twice, and tied nine times. Highsignal kept the
data engineering note as shorthand. It still overstated a city's commitment
to public feedback as a central role for residents in the design.

The judge changed some grades even though the baseline text stayed fixed.
The first judge called 56 excerpts in need of edits. The last judge called
48. Using the original 56 labels throughout, missed edits rise from 6 to
10 to 16, while unnecessary edits fall from 14 to 9 to 4. The retest shows
fewer changes to meaning on the same sample. The cost in missed edits
depends on which judgments about the source are held fixed.

All four synthetic argument edits passed the existing rubric on the final
version. The selected-paragraph edit still picked a meaning for “finish”
after identifying the ambiguity. One public editor batch failed output
validation and passed on retry. All 100 pairs were scored.
