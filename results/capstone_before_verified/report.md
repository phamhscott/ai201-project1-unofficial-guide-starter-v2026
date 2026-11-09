## Run Log - Before (Unit 9)

The baseline ran the committed five-criterion protocol three times with the
same application, criteria, and evaluator throughout the complete set. The
criteria were first committed in `f7d1fb1`, followed by Scott's introductory
cleanup in `e036e3a` before testing. The complete set
used source commit `80d6a03`. The
[manifest](../../results/capstone_before_verified/manifest.json) records the criteria commit and source
fingerprints. The [summary](../../results/capstone_before_verified/summary.json) confirms that the source
stayed unchanged across all three trials.

Each trial rebuilt 98 city-guide chunks in the isolated checkout, used fresh
server processes, and saved 17 HTTP observations with 17 original request log
records. The five normal questions used real embeddings and uncached Gemini
answers. Missing-index, injected-exception, and missing-metadata cases were
run exactly as specified. Synthetic probes are labeled in the independent
captures and are not presented as actual provider outages or API spending.

**Evaluator history:** Two earlier incomplete sets are retained in
[the first attempt](../../results/capstone_before/ATTEMPT.md) and
[the second attempt](../../results/capstone_before_complete/ATTEMPT.md).
Both stopped after nine requests per trial because the evaluator's port
checks prevented the next server phase from starting. Their original raw
outputs and provisional MISSED tables remain unchanged. They did not execute
the complete protocol, so they cannot establish a complete system verdict.
The evaluator was repaired and its four server phases checked without model
calls before the complete three-trial set below. No application code or
criterion target was changed, and the evaluator repair does not count as the
later system improvement. No failed request from the complete set was rerun
or dropped.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Local endpoint answer contract | 5/5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Expected error responses | 6/6 | 6/6 | 6/6 | 6/6 | MET |
| 3. Complete matching request records | 11/11 | 11/11 | 11/11 | 11/11 | MET |
| 4. Independent timing agreement | 5/5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Per-request usage attribution | 6/6 | 6/6 | 6/6 | 5/6 | MISSED |

### Criterion 1 - Local endpoint answer contract

**Claim:** All five supported questions returned the specified answer-response
contract in each trial, for 5/5, 5/5, and 5/5.

**Location:** `serve.py::ask` calls `app.py::ask_pipeline` and builds the HTTP
response. `tools/run_capstone_eval.py::answer_contract` checks its status and
fields. This is the actual response body for trial 1's first question, saved
in [observations.jsonl](../../results/capstone_before_verified/trial_1/observations.jsonl).

**Output:**

```json
{"answer":"Based on the provided documents, the text lists four difficult locations for getting around with limited mobility under the \"Difficult\" section: Kestrelford, Halden Bay, Corry Vale, and Elder Ness (guide_accessibility.md).","best_distance":0.5351,"corpus":"city_guides","question":"What are the four most difficult towns to get around with limited mobility?","refused":false,"sources":["guide_accessibility.md","guide_corry_vale.md","guide_walking.md"],"threshold":0.65}
```

### Criterion 2 - Expected error responses

**Claim:** Each trial returned the expected JSON error and status for all six
failure cases, for 6/6, 6/6, and 6/6.

**Location:** `serve.py::ask` validates input and catches pipeline exceptions.
`tools/capstone_probe_server.py::main` injects the specified model failure.
`tools/run_capstone_eval.py::error_contract` checks the results. The following
malformed-input and injected-failure observations are copied exactly from
[trial 1 output.txt](../../results/capstone_before_verified/trial_1/output.txt).

**Output:**

```text
HTTP {"case": "error_malformed", "phase": "normal", "input": null, "raw_input": "{broken", "expected_status": 400, "request_id": "6f06acb3822248a88c1b8cf3d513d264", "status_code": 400, "response": {"error": "Send JSON with a question in it, like {\"question\": \"When should I visit Kestrelford?\"}"}, "client_ms": 14.641399960964918, "raw_response": "{\"error\":\"Send JSON with a question in it, like {\\\"question\\\": \\\"When should I visit Kestrelford?\\\"}\"}\n"}
HTTP {"case": "error_failed_call", "phase": "failed-call", "input": {"question": "When is the recommended time to go visit Kestrelford?"}, "raw_input": "{\"question\": \"When is the recommended time to go visit Kestrelford?\"}", "expected_status": 500, "request_id": "a3c6e2764b4a4293b1dbd7a46cc7cf39", "status_code": 500, "response": {"error": "RuntimeError: unable to answer question"}, "client_ms": 178.521899972111, "raw_response": "{\"error\":\"RuntimeError: unable to answer question\"}\n"}
```

### Criterion 3 - Complete matching request records

**Claim:** All eleven core requests, including errors, had one complete matching
record in each trial, for 11/11, 11/11, and 11/11.

**Location:** `serve.py::finish_request_record` sends the record to
`request_log.py::append_record`. `tools/run_capstone_eval.py::log_contract`
matches it with the independently saved HTTP status, body, and response header.
This missing-index record is copied from
[trial 1 requests.jsonl](../../results/capstone_before_verified/trial_1/requests.jsonl).

**Output:**

```jsonl
{"timestamp": "2026-11-09T22:20:36.513509+00:00", "request_id": "a7902fffcb184409a6eb35461b09c98d", "method": "POST", "path": "/ask", "corpus": "city_guides", "model": "gemini-3.5-flash-lite", "cache_enabled": false, "usage": {"model_calls": 0, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 0, "output_tokens": 0, "total_tokens": 0}, "input": {"question": "When is the recommended time to go visit Kestrelford?"}, "output": {"error": "RuntimeError: unable to answer question"}, "status_code": 500, "duration_ms": 13.477}
```

### Criterion 4 - Independent timing agreement

**Claim:** All fifteen timing comparisons met the larger-of-50-ms-or-10-percent
tolerance, for 5/5 in each trial. The first request after startup was included.

**Location:** `serve.py::start_request_record` and
`serve.py::finish_request_record` measure server duration.
`tools/run_capstone_eval.py::Trial.post` independently measures elapsed client
time through reading the response body. `timing_comparison` applies the fixed
formula. These five measurements are copied from
[trial 1 output.txt](../../results/capstone_before_verified/trial_1/output.txt).

**Output:**

```text
TIMING {"case": "answer_1", "request_id": "dc96dd49d36647c2abf1dfac3ebe1823", "client_ms": 1897.463500034064, "logged_ms": 1876.344, "difference_ms": 21.119500034064004, "allowed_ms": 189.7463500034064, "passed": true}
TIMING {"case": "answer_2", "request_id": "6059c296ab504cd288220a41e16b4d3f", "client_ms": 790.3674002736807, "logged_ms": 773.173, "difference_ms": 17.194400273680685, "allowed_ms": 79.03674002736807, "passed": true}
TIMING {"case": "answer_3", "request_id": "7c66901b465740d895276df9fbdb1e00", "client_ms": 561.3776999525726, "logged_ms": 535.099, "difference_ms": 26.278699952572538, "allowed_ms": 56.13776999525726, "passed": true}
TIMING {"case": "answer_4", "request_id": "59aa7316f5314068bb2a62b5b952a66d", "client_ms": 637.4633996747434, "logged_ms": 626.228, "difference_ms": 11.235399674743462, "allowed_ms": 63.74633996747434, "passed": true}
TIMING {"case": "answer_5", "request_id": "b495928a37e84dbbb8e416840ca2f567", "client_ms": 995.4708996228874, "logged_ms": 983.602, "difference_ms": 11.868899622887398, "allowed_ms": 99.54708996228874, "passed": true}
```

The complete set's elapsed-time distribution is shown below, derived from
the fifteen saved comparisons. This criterion measures timing accuracy and
does not impose a maximum answer latency.

| Trial | Client measurements | Minimum ms | Median ms | Maximum ms | Largest timing discrepancy ms |
|---|---:|---:|---:|---:|---:|
| 1 | 5 | 561.378 | 790.367 | 1897.464 | 26.279 |
| 2 | 5 | 540.917 | 722.666 | 1917.626 | 19.438 |
| 3 | 5 | 660.945 | 693.428 | 2007.488 | 25.720 |

### Criterion 5 - Per-request usage attribution

**Claim:** The six accounting cases scored 6/6, 6/6, and 5/6. Criterion 5 is
MISSED because trial 3's first supported accounting request made four API
attempts, exceeding its fixed one-call target.

**Location:** `generate.py::generate` counts attempts and handles retries.
`generate.py::_record_tokens` records returned metadata, and
`generate.py::RequestUsage.as_dict` marks incomplete aggregate usage unknown.
`tools/capstone_probe_server.py::observed_call`, defined inside `main`, forwards
real calls and independently captures their metadata. The evaluator's
`usage_comparison` compares that capture with the request log.

**Output from trial 1:** These six exact comparisons are copied from
[output.txt](../../results/capstone_before_verified/trial_1/output.txt).

```text
USAGE {"case": "usage_first", "request_id": "553621e08e3f43f7a28b690d116986d5", "expected": {"model_calls": 1, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 716, "output_tokens": 50, "total_tokens": 766}, "actual": {"model_calls": 1, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 716, "output_tokens": 50, "total_tokens": 766}, "independently_observed_calls": 1, "passed": true}
USAGE {"case": "usage_cached", "request_id": "8f6f1205dc7a4ff194396f31463df069", "expected": {"model_calls": 0, "cache_hits": 1, "usage_complete": true, "prompt_tokens": 0, "output_tokens": 0, "total_tokens": 0}, "actual": {"model_calls": 0, "cache_hits": 1, "usage_complete": true, "prompt_tokens": 0, "output_tokens": 0, "total_tokens": 0}, "independently_observed_calls": 0, "passed": true}
USAGE {"case": "usage_refused", "request_id": "433daefbcb544a2a90ce94511ceaa2fe", "expected": {"model_calls": 0, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 0, "output_tokens": 0, "total_tokens": 0}, "actual": {"model_calls": 0, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 0, "output_tokens": 0, "total_tokens": 0}, "independently_observed_calls": 0, "passed": true}
USAGE {"case": "usage_blank", "request_id": "5fd4546450064013a390b20239851d35", "expected": {"model_calls": 0, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 0, "output_tokens": 0, "total_tokens": 0}, "actual": {"model_calls": 0, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 0, "output_tokens": 0, "total_tokens": 0}, "independently_observed_calls": 0, "passed": true}
USAGE {"case": "usage_missing_metadata", "request_id": "4bb62cc5365546289c136103e4d33276", "expected": {"model_calls": 1, "cache_hits": 0, "usage_complete": false, "prompt_tokens": null, "output_tokens": null, "total_tokens": null}, "actual": {"model_calls": 1, "cache_hits": 0, "usage_complete": false, "prompt_tokens": null, "output_tokens": null, "total_tokens": null}, "independently_observed_calls": 1, "passed": true}
USAGE {"case": "usage_failed_call", "request_id": "6d8a513388ac4552a1f9b8e88de53f2c", "expected": {"model_calls": 1, "cache_hits": 0, "usage_complete": false, "prompt_tokens": null, "output_tokens": null, "total_tokens": null}, "actual": {"model_calls": 1, "cache_hits": 0, "usage_complete": false, "prompt_tokens": null, "output_tokens": null, "total_tokens": null}, "independently_observed_calls": 1, "passed": true}
```

The real SDK response metadata for trial 1's first accounting request was
captured independently in
[accounting_api_capture.jsonl](../../results/capstone_before_verified/trial_1/accounting_api_capture.jsonl):

```jsonl
{"timestamp": "2026-11-09T22:20:39.415119+00:00", "request_id": "553621e08e3f43f7a28b690d116986d5", "attempt": 1, "model": "gemini-3.5-flash-lite", "source": "real_api", "question": "When should I visit Kestrelford?", "usage_metadata": {"cache_tokens_details": null, "cached_content_token_count": null, "candidates_token_count": 50, "candidates_tokens_details": null, "prompt_token_count": 716, "prompt_tokens_details": [{"modality": "TEXT", "token_count": 716}], "thoughts_token_count": null, "tool_use_prompt_token_count": null, "tool_use_prompt_tokens_details": null, "total_token_count": 766, "traffic_type": null}, "outcome": "response"}
```

**Diagnosis of the miss:** Trial 3's generator classified three `ClientError`
exceptions as rate-limit failures and retried with 1-, 2-, and 4-second waits.
The fourth attempt returned an answer. The request log correctly agreed with
the independent capture on four calls and unknown aggregate token usage.
The unknown fields reflect the three failed attempts without usage metadata.
Correct attribution does not meet this case's separate strict one-call
requirement. The original criterion explicitly says a retry is a miss, so its
target and verdict remain unchanged.

The exact retry output is in
[trial 3 accounting_console.txt](../../results/capstone_before_verified/trial_3/accounting_console.txt):

```text
  [rate limit] service pushed back. Retrying in 1s (attempt 1 of 4).
  [rate limit] service pushed back. Retrying in 2s (attempt 2 of 4).
  [rate limit] service pushed back. Retrying in 4s (attempt 3 of 4).
```

The independent attempt records are in
[trial 3 accounting_api_capture.jsonl](../../results/capstone_before_verified/trial_3/accounting_api_capture.jsonl):

```jsonl
{"timestamp": "2026-11-09T22:21:10.248637+00:00", "request_id": "8968a1b137c74dcb9151028c813bfab8", "attempt": 1, "model": "gemini-3.5-flash-lite", "source": "real_api", "question": "When should I visit Kestrelford?", "outcome": "exception", "exception_type": "ClientError", "usage_metadata": null}
{"timestamp": "2026-11-09T22:21:12.415375+00:00", "request_id": "8968a1b137c74dcb9151028c813bfab8", "attempt": 2, "model": "gemini-3.5-flash-lite", "source": "real_api", "question": "When should I visit Kestrelford?", "outcome": "exception", "exception_type": "ClientError", "usage_metadata": null}
{"timestamp": "2026-11-09T22:21:14.528935+00:00", "request_id": "8968a1b137c74dcb9151028c813bfab8", "attempt": 3, "model": "gemini-3.5-flash-lite", "source": "real_api", "question": "When should I visit Kestrelford?", "outcome": "exception", "exception_type": "ClientError", "usage_metadata": null}
{"timestamp": "2026-11-09T22:21:18.623743+00:00", "request_id": "8968a1b137c74dcb9151028c813bfab8", "attempt": 4, "model": "gemini-3.5-flash-lite", "source": "real_api", "question": "When should I visit Kestrelford?", "usage_metadata": {"cache_tokens_details": null, "cached_content_token_count": null, "candidates_token_count": 50, "candidates_tokens_details": null, "prompt_token_count": 716, "prompt_tokens_details": [{"modality": "TEXT", "token_count": 716}], "thoughts_token_count": null, "tool_use_prompt_token_count": null, "tool_use_prompt_tokens_details": null, "total_token_count": 766, "traffic_type": null}, "outcome": "response"}
```

The matching request record is in
[trial 3 requests.jsonl](../../results/capstone_before_verified/trial_3/requests.jsonl):

```jsonl
{"timestamp": "2026-11-09T22:21:10.087616+00:00", "request_id": "8968a1b137c74dcb9151028c813bfab8", "method": "POST", "path": "/ask", "corpus": "city_guides", "model": "gemini-3.5-flash-lite", "cache_enabled": true, "usage": {"model_calls": 4, "cache_hits": 0, "usage_complete": false, "prompt_tokens": null, "output_tokens": null, "total_tokens": null}, "input": {"question": "When should I visit Kestrelford?"}, "output": {"answer": "You should visit Kestrelford in late spring and early autumn (*guide_kestrelford.md*). Additionally, August is a busy time with walkers (*guide_kestrelford.md* and *guide_seasons.md*).", "best_distance": 0.3251, "corpus": "city_guides", "question": "When should I visit Kestrelford?", "refused": false, "sources": ["guide_kestrelford.md", "guide_seasons.md"], "threshold": 0.65}, "status_code": 200, "duration_ms": 9227.479}
```

### Limits exposed by the baseline

The verdicts concern the five operational contracts. They do not establish
factual answer accuracy. Trial 3's first answer incorrectly added Givens Mill
as a fifth difficult location. In
[`guide_accessibility.md`](../../corpora/city_guides/documents/guide_accessibility.md),
Givens Mill is under `Mixed` and also appears under `Practical`. The `Difficult`
section names Kestrelford, Halden Bay, Corry Vale, and Elder Ness. Criterion 1
explicitly checks the HTTP response schema and excludes factual accuracy, so
this content error does not change its MET verdict. A future stronger
answer-content criterion would need to compare the asserted group against the
source. The current criteria have not been revised after these results.

**Location:** `generate.py::answer_from_chunks` generates the answer, returned
by `serve.py::ask`. The exact trial 3 response is preserved in
[observations.jsonl](../../results/capstone_before_verified/trial_3/observations.jsonl).

**Output:**

```json
{"answer":"Based on the documents provided, there are five locations listed as \"Difficult\" for limited mobility rather than four: Kestrelford, Halden Bay, Corry Vale, Elder Ness, and Givens Mill (mentioned under practical medical facilities). \n\nSource: guide_accessibility.md","best_distance":0.5351,"corpus":"city_guides","question":"What are the four most difficult towns to get around with limited mobility?","refused":false,"sources":["guide_accessibility.md","guide_corry_vale.md","guide_walking.md"],"threshold":0.65}
```

The baseline is preserved before any system improvement. No fix or after-run
results are claimed in this milestone.
