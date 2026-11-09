## Diagnosis and One Improvement (Unit 9)

The baseline verdicts remain MET for criteria 1 through 4 and MISSED for
criterion 5. The single scored miss was trial 3's first accounting request:
four recorded model-call attempts exceeded that case's one-call target.

**Stage:** Generation API scheduling and the retry loop in
`generate.py::generate`, using `generate.py::_wait_for_slot`.

**Mechanism:** The old limiter returned immediately whenever fewer than 30
attempts were in its local 60-second window. It capped a burst but did not
space the calls inside that burst. Its history was also local to one server
process. The provider errors were classified as rate-limit failures and the
generation loop waited 1, 2, and 4 seconds before succeeding on its fourth
attempt. The complete before-run captures and retry output remain above.
The confirmed reason for the missed target is the extra retry attempts.
The burst-only limiter was a local weakness that could contribute to that
pressure. The capture does not establish the provider's exact quota or rule
out traffic elsewhere using the same account.

**Pattern:** The same baseline trial also recorded two model attempts for the
fifth normal question. That response still met its HTTP and timing contracts,
but its retry is a second symptom of the same generation-stage problem.
There were four rate-limit retry messages across the complete baseline,
one in the normal phase and three in the accounting phase. The accounting
logic was already reporting attempts and unknown usage correctly.

**Location and output:** This unchanged record is from
[baseline trial 3 requests.jsonl](../../results/capstone_before_verified/trial_3/requests.jsonl), written by
`serve.py::finish_request_record` through `request_log.py::append_record`:

```jsonl
{"timestamp": "2026-11-09T22:21:04.190185+00:00", "request_id": "ed3eb7e59b4d4e9682b3d8ba2ed1095e", "method": "POST", "path": "/ask", "corpus": "city_guides", "model": "gemini-3.5-flash-lite", "cache_enabled": false, "usage": {"model_calls": 2, "cache_hits": 0, "usage_complete": false, "prompt_tokens": null, "output_tokens": null, "total_tokens": null}, "input": {"question": "When is the recommended time to go visit Kestrelford?"}, "output": {"answer": "The recommended time to visit Kestrelford is in late spring and early autumn (guide_kestrelford.md).", "best_distance": 0.3375, "corpus": "city_guides", "question": "When is the recommended time to go visit Kestrelford?", "refused": false, "sources": ["guide_givens_mill.md", "guide_halden_bay.md", "guide_kestrelford.md", "guide_marchwood.md", "guide_seasons.md"], "threshold": 0.65}, "status_code": 200, "duration_ms": 1555.005}
```

**One improvement:** Commit `c579e15` changes
outbound pacing in `generate.py::_wait_for_slot`. It reserves slots spaced by
`60 / REQUESTS_PER_MINUTE`, using the existing setting of 30, so the interval
is two seconds. The first slot waits too. A thread lock serializes reservations
within a server process, and the original rolling-window ceiling is retained.
The reservation is recorded in the pacing function rather than appended later
by the caller. Retrieval, prompts, model selection, retry count, response
format, token accounting, criteria, and the formal evaluator are unchanged.

**Controlled check:** `tools/probe_pacing.py::measure` uses a virtual clock and
five synthetic 0.1-second model responses to isolate the scheduling behavior.
It made no real API calls. The before probe shows a 0.1-second minimum gap,
and the after probe shows two-second reserved slots with 9.6 seconds of total
pacing wait. These measurements prove the local pacing change and do not
measure provider reliability or API spending. All 18 development tests passed,
including the initial wait, minimum spacing, rolling-window limit, retry
accounting, concurrent usage isolation, and evaluator scoring checks.

**Output from [capstone_pacing_before.json](../../results/capstone_pacing_before.json):**

```json
{
  "kind": "synthetic_virtual_clock_probe",
  "real_api_calls": 0,
  "configured_requests_per_minute": 30,
  "simulated_model_response_seconds": 0.1,
  "call_start_seconds": [
    0.0,
    0.1,
    0.2,
    0.3,
    0.4
  ],
  "inter_call_gap_seconds": [
    0.1,
    0.1,
    0.1,
    0.1
  ],
  "minimum_gap_seconds": 0.1,
  "total_pacing_wait_seconds": 0
}
```

**Output from [capstone_pacing_after.json](../../results/capstone_pacing_after.json):**

```json
{
  "kind": "synthetic_virtual_clock_probe",
  "real_api_calls": 0,
  "configured_requests_per_minute": 30,
  "simulated_model_response_seconds": 0.1,
  "call_start_seconds": [
    2.0,
    4.0,
    6.0,
    8.0,
    10.0
  ],
  "inter_call_gap_seconds": [
    2.0,
    2.0,
    2.0,
    2.0
  ],
  "minimum_gap_seconds": 2.0,
  "total_pacing_wait_seconds": 9.6
}
```

## Run Log - After (Unit 9)

The full fixed protocol ran three times after the one pacing change. Every
trial rebuilt the isolated index and used fresh server processes. The five
normal questions remained uncached, and the same six error and six accounting
cases were used. All 51 HTTP observations and their 51 original JSONL records
are saved. No trial was replaced and no further application change was made
between these three trials.

The [after manifest](../../results/capstone_after/manifest.json) records source commit
`c579e15` and the same criteria commit as the
baseline. The [summary](../../results/capstone_after/summary.json) confirms unchanged source throughout
the three after-trials. Comparing the fixed input fingerprints identifies only
`generate.py` as changed between the before and after runs. The formal
evaluator and the criteria are identical.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Local endpoint answer contract | 5/5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Expected error responses | 6/6 | 6/6 | 6/6 | 6/6 | MET |
| 3. Complete matching request records | 11/11 | 11/11 | 11/11 | 11/11 | MET |
| 4. Independent timing agreement | 5/5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Per-request usage attribution | 6/6 | 6/6 | 6/6 | 6/6 | MET |

### Criterion 1 - MET

All five supported questions met the HTTP answer contract in each trial.
`serve.py::ask` builds the response and
`tools/run_capstone_eval.py::answer_contract` checks it. This exact first
response body is from [after trial 1 observations.jsonl](../../results/capstone_after/trial_1/observations.jsonl).

```json
{"answer":"Based on the provided documents, the towns listed under the \"Difficult\" category for getting around with limited mobility are Kestrelford, Halden Bay, Corry Vale, and Elder Ness. \n\n*(Source: guide_accessibility.md)*","best_distance":0.5351,"corpus":"city_guides","question":"What are the four most difficult towns to get around with limited mobility?","refused":false,"sources":["guide_accessibility.md","guide_corry_vale.md","guide_walking.md"],"threshold":0.65}
```

### Criterion 2 - MET

All six invalid-input and controlled server-fault cases returned their expected
error contracts in each trial. `serve.py::ask` returns the error and the
evaluator's `error_contract` checks it. The injected model failure below is
copied from [after trial 1 output.txt](../../results/capstone_after/trial_1/output.txt).

```text
HTTP {"case": "error_failed_call", "phase": "failed-call", "input": {"question": "When is the recommended time to go visit Kestrelford?"}, "raw_input": "{\"question\": \"When is the recommended time to go visit Kestrelford?\"}", "expected_status": 500, "request_id": "2a2d56c1687f4d8ab87ad495661e56ec", "status_code": 500, "response": {"error": "RuntimeError: unable to answer question"}, "client_ms": 2174.051799811423, "raw_response": "{\"error\":\"RuntimeError: unable to answer question\"}\n"}
```

### Criterion 3 - MET

All eleven core requests had one complete matching log record in each trial.
`serve.py::finish_request_record` and `request_log.py::append_record` produce
the record, and the evaluator's `log_contract` compares it with the response.
This missing-index record is from
[after trial 1 requests.jsonl](../../results/capstone_after/trial_1/requests.jsonl).

```jsonl
{"timestamp": "2026-11-09T22:37:06.781128+00:00", "request_id": "abbd108129924bceaa44edba616067ff", "method": "POST", "path": "/ask", "corpus": "city_guides", "model": "gemini-3.5-flash-lite", "cache_enabled": false, "usage": {"model_calls": 0, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 0, "output_tokens": 0, "total_tokens": 0}, "input": {"question": "When is the recommended time to go visit Kestrelford?"}, "output": {"error": "RuntimeError: unable to answer question"}, "status_code": 500, "duration_ms": 12.969}
```

### Criterion 4 - MET

All fifteen timing comparisons met the original 50-ms-or-10-percent tolerance.
`serve.py::start_request_record` and `finish_request_record` time the server.
`tools/run_capstone_eval.py::Trial.post` measures the independent client time,
and `timing_comparison` applies the same formula. These exact comparisons are
from [after trial 1 output.txt](../../results/capstone_after/trial_1/output.txt).

```text
TIMING {"case": "answer_1", "request_id": "0648e78cd50e445cb9bef99d83cb62ca", "client_ms": 4016.596999950707, "logged_ms": 3992.259, "difference_ms": 24.337999950706944, "allowed_ms": 401.6596999950707, "passed": true}
TIMING {"case": "answer_2", "request_id": "382764357149413a966fa9d4b52334c2", "client_ms": 746.201700065285, "logged_ms": 726.884, "difference_ms": 19.317700065284953, "allowed_ms": 74.6201700065285, "passed": true}
TIMING {"case": "answer_3", "request_id": "e92fb347623b4e10b11f2e29838c3e92", "client_ms": 1904.4881002046168, "logged_ms": 1886.563, "difference_ms": 17.925100204616683, "allowed_ms": 190.44881002046168, "passed": true}
TIMING {"case": "answer_4", "request_id": "6614359561ba4424986213b1869fdcfb", "client_ms": 2128.4316000528634, "logged_ms": 2111.251, "difference_ms": 17.180600052863156, "allowed_ms": 212.84316000528634, "passed": true}
TIMING {"case": "answer_5", "request_id": "2c067c0211244b158949e795834f7b36", "client_ms": 1858.2580997608602, "logged_ms": 1842.129, "difference_ms": 16.1290997608603, "allowed_ms": 185.82580997608602, "passed": true}
```

### Criterion 5 - MET

All six accounting cases met their original targets in each trial, including
one real model call for every first supported accounting request.
`generate.py::generate` and `_record_tokens` produce usage counts.
`tools/capstone_probe_server.py::main` installs the independent forwarding spy,
and the evaluator's `usage_comparison` checks attribution. These six exact
comparisons are from [after trial 1 output.txt](../../results/capstone_after/trial_1/output.txt).

```text
USAGE {"case": "usage_first", "request_id": "0b8217fd73bb4dc9a2bc4a690c981748", "expected": {"model_calls": 1, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 716, "output_tokens": 50, "total_tokens": 766}, "actual": {"model_calls": 1, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 716, "output_tokens": 50, "total_tokens": 766}, "independently_observed_calls": 1, "passed": true}
USAGE {"case": "usage_cached", "request_id": "e65c5762dfcb468ea0d50888ce470173", "expected": {"model_calls": 0, "cache_hits": 1, "usage_complete": true, "prompt_tokens": 0, "output_tokens": 0, "total_tokens": 0}, "actual": {"model_calls": 0, "cache_hits": 1, "usage_complete": true, "prompt_tokens": 0, "output_tokens": 0, "total_tokens": 0}, "independently_observed_calls": 0, "passed": true}
USAGE {"case": "usage_refused", "request_id": "80c82c4180574e878035b61b73167b62", "expected": {"model_calls": 0, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 0, "output_tokens": 0, "total_tokens": 0}, "actual": {"model_calls": 0, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 0, "output_tokens": 0, "total_tokens": 0}, "independently_observed_calls": 0, "passed": true}
USAGE {"case": "usage_blank", "request_id": "72262eef1ea64629a80edfdab4781cbe", "expected": {"model_calls": 0, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 0, "output_tokens": 0, "total_tokens": 0}, "actual": {"model_calls": 0, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 0, "output_tokens": 0, "total_tokens": 0}, "independently_observed_calls": 0, "passed": true}
USAGE {"case": "usage_missing_metadata", "request_id": "46577f56b4324fecb2046b7a85f2f27d", "expected": {"model_calls": 1, "cache_hits": 0, "usage_complete": false, "prompt_tokens": null, "output_tokens": null, "total_tokens": null}, "actual": {"model_calls": 1, "cache_hits": 0, "usage_complete": false, "prompt_tokens": null, "output_tokens": null, "total_tokens": null}, "independently_observed_calls": 1, "passed": true}
USAGE {"case": "usage_failed_call", "request_id": "000f76ca6bdc4b6a8cd6f13cd0b1ab25", "expected": {"model_calls": 1, "cache_hits": 0, "usage_complete": false, "prompt_tokens": null, "output_tokens": null, "total_tokens": null}, "actual": {"model_calls": 1, "cache_hits": 0, "usage_complete": false, "prompt_tokens": null, "output_tokens": null, "total_tokens": null}, "independently_observed_calls": 1, "passed": true}
```

For comparison with the original miss, after trial 3's first accounting request
made exactly one observed call with complete reported usage. The independent
capture is from [accounting_api_capture.jsonl](../../results/capstone_after/trial_3/accounting_api_capture.jsonl)
and its matching record is from [requests.jsonl](../../results/capstone_after/trial_3/requests.jsonl).

```jsonl
{"timestamp": "2026-11-09T22:38:07.775455+00:00", "request_id": "626268acaeaf4b07a9ee1e4ee1bb4188", "attempt": 1, "model": "gemini-3.5-flash-lite", "source": "real_api", "question": "When should I visit Kestrelford?", "usage_metadata": {"cache_tokens_details": null, "cached_content_token_count": null, "candidates_token_count": 50, "candidates_tokens_details": null, "prompt_token_count": 716, "prompt_tokens_details": [{"modality": "TEXT", "token_count": 716}], "thoughts_token_count": null, "tool_use_prompt_token_count": null, "tool_use_prompt_tokens_details": null, "total_token_count": 766, "traffic_type": null}, "outcome": "response"}
{"timestamp": "2026-11-09T22:38:05.610856+00:00", "request_id": "626268acaeaf4b07a9ee1e4ee1bb4188", "method": "POST", "path": "/ask", "corpus": "city_guides", "model": "gemini-3.5-flash-lite", "cache_enabled": true, "usage": {"model_calls": 1, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 716, "output_tokens": 50, "total_tokens": 766}, "input": {"question": "When should I visit Kestrelford?"}, "output": {"answer": "You should visit Kestrelford in late spring and early autumn (*guide_kestrelford.md*). Additionally, August is a busy time with walkers (*guide_kestrelford.md* and *guide_seasons.md*).", "best_distance": 0.3251, "corpus": "city_guides", "question": "When should I visit Kestrelford?", "refused": false, "sources": ["guide_kestrelford.md", "guide_seasons.md"], "threshold": 0.65}, "status_code": 200, "duration_ms": 3970.474}
```

## Before and After (Unit 9)

Both result sets use the same targets. Each triple lists run 1, run 2, and run 3.

| Criterion | Target per trial | Before runs 1, 2, 3 | Before | After runs 1, 2, 3 | After |
|---|---|---|---|---|---|
| 1. Local endpoint answer contract | 5/5 | 5/5, 5/5, 5/5 | MET | 5/5, 5/5, 5/5 | MET |
| 2. Expected error responses | 6/6 | 6/6, 6/6, 6/6 | MET | 6/6, 6/6, 6/6 | MET |
| 3. Complete matching request records | 11/11 | 11/11, 11/11, 11/11 | MET | 11/11, 11/11, 11/11 | MET |
| 4. Independent timing agreement | 5/5 | 5/5, 5/5, 5/5 | MET | 5/5, 5/5, 5/5 | MET |
| 5. Per-request usage attribution | 6/6 | 6/6, 6/6, 5/6 | MISSED | 6/6, 6/6, 6/6 | MET |

**Did it help?** The measured accounting score improved from 6/6, 6/6, 5/6 to
6/6 in all three trials. The first accounting requests changed from 1, 1, and
4 observed attempts to 1, 1, and 1. Recorded rate-limit retry messages changed
from four in the complete baseline to zero in the after set. All other
criterion verdicts remained MET. The unchanged baseline miss is retained.

**Tradeoff:** The normal-request sample has fifteen independent client timings
on each side, including each server's first answer. The mean increased from
1.008 seconds to 2.141
seconds, and the median increased from 0.723
seconds to 1.938 seconds. Slower answers are a
measured cost of the pacing policy. Timing remained accurate against the
independent client measurements. There is no maximum-latency criterion, so
the slower responses do not change criterion 4's verdict.

| Normal-request client time | Before, 15 requests | After, 15 requests |
|---|---:|---:|
| Mean seconds | 1.008 | 2.141 |
| Median seconds | 0.723 | 1.938 |
| Minimum seconds | 0.541 | 0.746 |
| Maximum seconds | 2.007 | 4.106 |

These figures are calculated from the saved timing observations in
[comparison.json](../../results/capstone_after/comparison.json). The actual pacing waits are visible
in [after trial 1 normal_console.txt](../../results/capstone_after/trial_1/normal_console.txt):

```text
  [pacing] Waiting 2.00s for a spaced model-call slot.
  [pacing] Waiting 0.11s for a spaced model-call slot.
  [pacing] Waiting 1.36s for a spaced model-call slot.
  [pacing] Waiting 1.45s for a spaced model-call slot.
  [pacing] Waiting 1.33s for a spaced model-call slot.
```

The controlled probe establishes the scheduling change, and the live retest
shows a better score on this sample. Provider load and quota state were not
controlled, so the live difference alone does not prove that pacing caused
every avoided retry or that future requests will always use one call.
Reservations are per process, before SDK initialization. They are not a
shared account-wide limiter or a measurement of exact wire-level call times.
The baseline answer-content error also remains a separate limitation because
no prompt or retrieval change was made. Only one application improvement was
attempted, and the original targets were not relaxed.
