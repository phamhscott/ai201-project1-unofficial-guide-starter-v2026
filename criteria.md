# Unit 9 capstone acceptance criteria

**Status:** Finalized for the formal before-and-after evaluation. Scott selected
the larger of 50 milliseconds or 10 percent for the timing-accuracy tolerance.

These five criteria cover the Shape A extension, using Path B with the local
HTTP service. They follow Scott's priorities of a working endpoint, expected
error responses, and usable logs, together with the previously agreed timing
and token-accounting focuses. Codex helped turn those priorities into measurable
wording and technical rationales. They are not claimed as unaided work.

**Chronology:** The Project 1 results, development checks, and Milestone 3
operational logs and cost measurements already exist. These criteria are being
written after those observations and before the capstone's formal acceptance
trials. The earlier records remain intact and will not be counted as formal
trials against these targets.

## Trial protocol

Run three independent trials before the improvement and three afterward,
using the same requests, targets, and scoring rules. Each trial starts a fresh
server process from a checkout set up through `RUNNING.md`, with a rebuilt
city-guides index. Use a separate JSONL log for each trial. Preserve all
responses and request identifiers, including failures. Do not replace a failed
trial with a successful rerun.

For criteria 1 and 4, disable the answer cache with `AI201_CACHE=0`. Use these
five fixed questions, taken from the original Project 1 question set:

1. What are the four most difficult towns to get around with limited mobility?
2. What is the train frequency and duration to get to Brightwater?
3. What town has fresh seafood?
4. What can you see at Thornby Wells?
5. When is the recommended time to go visit Kestrelford?

For criterion 2, trigger the six specified failure cases in isolated server
processes where necessary. The missing-index case must use a separate checkout
or empty temporary index directory. The API failure is a deliberately injected
exception at the model-call boundary, not a claim of an actual provider outage.
Do not delete the working index or change the submitted corpus to create a
failure.

For criterion 5, use a separate process with caching enabled and an initially
empty temporary response-cache directory. Controlled model responses used to
test missing metadata or API errors must be labeled as synthetic fault probes.
They do not count as real generated answers or measured API spending.

For every criterion, the target must hold in all three trials for the final
verdict to be `MET`. Otherwise the verdict is `MISSED`. A request that never
returns a response cannot be scored as meeting its response, logging, or timing
target. Use a 120-second client timeout to stop such a request and preserve it
as a failed observation, rather than silently dropping it.

## 1. The local endpoint returns the expected answer response

**Target:** In each trial, all five fixed in-scope questions sent to
`POST http://127.0.0.1:5000/ask` after the documented startup return HTTP 200
with the answer-response contract defined below.

**Measurement:** Start with the command in `RUNNING.md` and confirm
`GET /health` reports `index_ready: true`. Send each question as JSON with a
string `question` field. The response contract requires the same `question`,
a nonempty string `answer`, `refused: false`, a nonempty list of source
filenames in `sources`, numeric `best_distance` and `threshold`, and
`corpus: "city_guides"`. An unreachable service, unsuccessful HTTP status,
unparseable JSON, or a missing or wrongly typed field is a failed response.
This criterion measures the HTTP answer contract, not factual answer accuracy.

**Why this target:** A local service must make the existing guide available
through its documented endpoint. The five existing questions exercise both
town-specific and cross-town requests without introducing a new corpus or
retriever. All five must work because a missing response or broken schema
prevents a caller from using the service even if retrieval itself is correct.
A stricter claim about every possible question would exceed this fixed sample.

## 2. Failed requests return the expected error response

**Target:** In each trial, all six specified failure cases return their expected
HTTP status and a JSON object with a nonempty string `error` field instead of
an answer response.

**Measurement:** Send these cases with `Content-Type: application/json`:

| Case | Request or controlled condition | Expected status |
|---|---|---:|
| Missing question | `{}` | 400 |
| Blank question | `{"question":" "}` | 400 |
| Wrong question type | `{"question":42}` | 400 |
| Malformed JSON | Raw body `{broken` | 400 |
| Missing index | A fixed in-scope question with no city-guides index | 500 |
| Failed model call | A fixed in-scope question with an injected `RuntimeError` from the model call | 500 |

A case fails if its status differs, its JSON cannot be parsed, its `error`
field is absent or empty, or its body contains an `answer` field. Preserve the
injection setup so another person can repeat the two controlled server faults.

**Why this target:** Clients need to distinguish a request they should correct
from a server dependency failure. Four cases cover the accepted request shape,
while the other two cover the local index and the external generator. All six
must follow the error contract because accepting a silent failure would leave
the caller without a usable outcome. This does not claim that the service
automatically repairs an index or recovers an unavailable API.

## 3. Every question request has one matching structured log record

**Target:** In each trial, every one of the eleven requests from criteria 1
and 2 produces exactly one complete, matching JSONL record, including failures.

**Measurement:** Match records to responses by the `X-Request-ID` header and
the record's `request_id`. Identifiers must be nonempty and unique across
requests. Each record must have a parseable UTC `timestamp`, `input`, `output`,
`status_code`, finite nonnegative `duration_ms`, `method`, `path`, `corpus`,
`model`, `cache_enabled`, and an object `usage`. Check `method: "POST"`,
`path: "/ask"`, and `corpus: "city_guides"`. For valid JSON bodies, `input`
must equal the submitted JSON. For the malformed body, require `input: null`
under the documented parsing policy. `output` must equal the returned JSON
and `status_code` must equal the HTTP status. Combine records from isolated
fault processes for the trial, preserving their original lines and identifiers.
Do not count health checks as question requests.

**Why this target:** A missing or duplicate record makes it impossible to
reconcile a request with the service's behavior. Requiring all eleven prevents
successful answers from hiding unlogged failures. Exact input, output, and
identifier matching gives a concrete diagnostic record rather than a count of
lines that might belong to different requests. This criterion checks record
coverage and identity. Timing accuracy and usage values are assessed separately.

## 4. Logged duration agrees with independently measured elapsed time

**Target:** In each trial, the logged
`duration_ms` for all five in-scope requests differs from the local client's
elapsed time by no more than the larger of 50 milliseconds or 10 percent of
that client's elapsed time.

**Measurement:** At the HTTP client, use `time.perf_counter()` immediately
before sending each request and immediately after reading its entire response
body. Convert the difference to milliseconds and compare it with the matching
record's `duration_ms`. The condition is
`abs(logged_ms - client_ms) <= max(50, 0.10 * client_ms)`.
Include the first request after server startup so model-loading time is not
removed from the sample. Do not infer duration from timestamps or compare
the log field with another copy of the same server timer.

**Why this target:** The timing field needs to support diagnosis of
slow requests. A missing wait or model-loading stage would make that diagnosis
misleading. Exact equality would reject normal socket, transfer, scheduling,
and log-writing overhead measured by the client. A 50-millisecond floor allows
small local overhead, while the 10-percent allowance scales to longer API calls
without permitting an arbitrarily large discrepancy. This is a timing-accuracy
target, not a promise of a maximum answer wait.

## 5. Usage records attribute API cost to the correct request

**Target:** In each trial, all six requests in the accounting sequence below
record the expected per-request model calls, cache hits, and token usage.

**Measurement:** Use `When should I visit Kestrelford?` for the two repeated
requests. For real API usage, preserve an independent capture of the returned
SDK response's `usage_metadata` and actual call count through a forwarding spy
at the client boundary. Compare the log with that capture rather than deriving
the expected values from the log itself. Run the sequence with an empty
temporary response cache and preserve the request identifiers.

| Request | Expected usage record |
|---|---|
| First supported question | One real model call, zero cache hits, and token counts matching the captured API metadata |
| Exact repeat of that question | Zero model calls, one cache hit, and zero new API tokens |
| `How do I write a for loop in Rust?` | Zero model calls, zero cache hits, and zero API tokens |
| Blank question | Zero model calls, zero cache hits, and zero API tokens |
| Supported question with a synthetic response lacking usage metadata | One model call, zero cache hits, `usage_complete: false`, and all three token fields `null` |
| Supported question with an injected model-call exception | One model call, zero cache hits, `usage_complete: false`, and all three token fields `null` |

Use `When should someone visit Kestrelford?` for the missing-metadata probe and
`What seasons does the guide recommend for visiting Kestrelford?` for the
injected-exception probe, so the earlier cached answer cannot bypass either
injected call. When a real response has complete
metadata, require `usage_complete: true` and exact agreement with its prompt,
candidate-output, and total token counts. If that real response lacks complete
metadata, require the documented unknown representation instead. Requests
making no model call must have `usage_complete: true` and zero token fields.
If a real call retries, preserve every attempt and its metadata. Unreported
usage from any attempt makes the aggregate token fields unknown, and the
first-row one-call target is missed rather than reclassified as a clean call.

**Why this target:** Session totals cannot show what a particular request
cost, and a cached answer must not inherit the cost of the request that created
it. The six cases distinguish an actual call, cache reuse, a gate refusal,
invalid input, missing metadata, and a failed call. Exact attribution is
required in every case because even one inherited token total or unknown cost
reported as zero would distort a small run's average. This checks accounting
correctness without choosing a spending limit from the observed cost sample.

## Criteria self-check

The written self-check below evaluates the criteria's measurability, not system
results. No acceptance verdicts have been assigned.

| Criterion | Observable target | Repeatable procedure | One behavior | System-specific reason | Extension coverage |
|---|---|---|---|---|---|
| 1 | Five valid answer responses per trial | Fixed questions and response contract | HTTP answer contract | Every caller needs a usable response | Local run path |
| 2 | Six expected error responses per trial | Fixed invalid inputs and injected faults | HTTP error contract | Failed requests need explicit outcomes | Failure handling at the endpoint |
| 3 | Eleven complete matching records per trial | Header and response comparisons | Request-to-record correspondence | Missing failures cannot be diagnosed | Structured logging |
| 4 | Five timing comparisons per trial | Independent monotonic client timer | Timing accuracy | Misreported waits mislead diagnosis | Timing instrumentation |
| 5 | Six correctly attributed usage records per trial | API metadata capture and fixed accounting sequence | Per-request cost attribution | Cache reuse and unknown usage must be distinct | Cost instrumentation |

All five focus on the extension and have explicit measurement instructions.
Criterion 2 covers bad paths, while criteria 3 and 5 require failure records
and unknown-cost handling. Losing even one request record or attributing cost
to the wrong request would defeat the stated purpose of this extension.
Scott selected the 50-millisecond or 10-percent timing tolerance because
accurate timing is a priority for this extension.

---

# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in week 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next week costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**
<!-- e.g. "One of my questions is about a topic only two documents mention, so
     I expect that one to be hard." -->

I chose 4 of 5 because one test question comes from
[`guide_accessibility.md`](corpora/city_guides/documents/guide_accessibility.md),
one of the five cross-town guides. Unlike the town-specific guides, it groups
information about many places under shared topics, so its relevant passage may
be harder to retrieve. I still expect the system to retrieve the needed chunk
for most questions.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**
<!-- Why all five and not four? What about your setup makes that achievable —
     or what would have to go wrong for it not to be? -->

I chose 5 of 5 because the system attaches source information to every chunk,
which can be inspected with `python app.py chunks`, and each in-scope answer is
generated from retrieved chunks. Source attribution is a built-in requirement,
so accepting fewer than five would allow an answer that cannot be traced back
to the corpus.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**
<!-- What did your distances look like when you set the cutoff in Milestone 4?
     Was there a clean gap, or did the two groups overlap? -->

I chose 4 of 5 because the relevance cutoff makes a yes or no decision from
semantic distance, and an out-of-scope question may occasionally share enough
language with the topic-organized guides to pass the gate. I allow one such
boundary case, but more than one would mean the cutoff does not reliably
separate supported questions from unsupported ones.

---

## 4. Chunks preserve complete guide sections

At least 4 of the 5 chunks printed by `python app.py chunks -n 5` contain
exactly one complete guide section, from its heading through its final sentence,
and contain no text from another section.

<!-- YOU WRITE THIS ONE.

     How would you know if your chunks were the right size? Name something
     countable or observable.

     Examples of the right shape — don't copy these, they should come from
     what you actually saw in Milestone 3:
       - "At least 4 of 5 sampled chunks read as a complete thought, with no
          sentence cut in half at either end."
       - "No chunk is shorter than 200 characters, since anything below that
          in my corpus turned out to be a heading with no content under it." -->



**Why this target:**

I chose 4 of 5 because the town-specific guides use repeated sections such as
`Getting there`, `Eat and drink`, and `When to go`, making section boundaries
natural chunk boundaries. I allow one miss because section lengths vary and the
cross-town guides use a different structure, but more than one would suggest
that the chunking strategy does not fit this corpus.

---

## 5. Cross-town answers include every listed place

For the limited-mobility test question, the answer names all four places listed
under `Difficult` in `guide_accessibility.md`: Kestrelford, Halden Bay, Corry
Vale, and Elder Ness.

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. It could be about
     speed, about refusals, about a particular kind of question your corpus
     handles badly, about source attribution being correct rather than merely
     present — anything, as long as it names a number or an observable
     outcome. -->



**Why this target:**

I require all four places because the question asks for a complete group from a
cross-town topic, so omitting even one would make the answer incomplete. This
also tests whether the system can use a cross-town guide rather than assemble a
partial answer from separate town-specific documents.


---

<!-- ─────────────────────────────────────────────────────────────────────────
     WEEK 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in week 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
