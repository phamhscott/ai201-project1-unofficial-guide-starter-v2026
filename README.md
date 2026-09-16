# The Unofficial Guide

Scott Pham, City-Guides Corpus
<!-- Replace this line with your name and which corpus you picked. -->

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none, because the grader can't
> read it.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Week 1

## What This Does

<!-- Three or four sentences. Which corpus you picked, and the kinds of
     questions your system answers. Write it for someone who has never seen
     this repo.

     Milestone 5. -->

I chose the city-guides corpus which contains 9 specific town guides as well as general guides that contain information across multiple towns. The goal of this system is to answer the users questions about city guide related topics that would be found in the original corpus documents. These could be specific town questions like "what kind of food is in Brightwater," or more general non-specific town questions like, "what are the best towns to visit during Summer?" By
investigating each documents structure, specific city related and general, this system (The Unofficial guide) aims to make it easier to search through and find desired information quickly about cities.

## Chunking Strategy

**Chunk size: 800**

**Overlap: 0**

For the city-guide corpus, a more reasonable chunking approach entails structure-aware splitting, not just splitting by char length. Since each doc, specifically town specific ones have discrete sections that are prefixed by a relevant heading (What to see, eat, etc), it feels right to try to have each chunk correspond with a section. However, these specific town docs are not the only types of docs. There are also docs that cross multiple towns and are general (guide_accessibility, guide_walking, etc). The sections here do not follow the same structure. Most importantly, they do not have the same char length (max of town specific: 378 chars, max of cross-town: 724). Since we want structure aware-splitting anyways, the chunk size should just aim to preserve the sections so keeping this at 800 is reasonable. Furthermore, the zero overlap prevents neighboring topics from being mixed (food to eat at a town vs when to visit the town) aiming to again switch to the structure aware chunking by section.

<!-- What about YOUR documents made you pick these numbers? Short posts and
     long sectioned guides don't want the same chunking, and "800 seemed
     reasonable" earns nothing. Point at something you noticed when you read
     the documents in Milestone 1.

     If you changed your mind partway through, say so and say why. That's worth
     more than pretending you got it right first time.

     Milestone 3. -->

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

**Chunk 1** — source: `guide_accessibility.md#0` — produced by: `chunker.py::split_documents`

```
# Getting around the region with limited mobility

An honest assessment rather than a promotional one. Some of these places are
difficult and it is better to know in advance.
```

**Chunk 2** — source: `guide_corry_vale.md#6` — produced by: `chunker.py::split_documents`

```
# Corry Vale

## When to go

May to September. Outside those months the pub in the third village closes, the farm shop reduces its hours, and several footpaths become genuinely boggy rather than merely wet. The road is not gritted above the second village and is impassable in snow.
```

**Chunk 3** — source: `guide_givens_mill.md#3` — produced by: `chunker.py::split_documents`

```
# Givens Mill

## Eat and drink

A tearoom attached to the mill, open 10 to 4 daily except Tuesdays, which sells bread made from the flour ground twenty metres away and is the reason most people come. One pub, food served lunchtimes and Thursday to Saturday evenings.
```

**Chunk 4** — source: `guide_kestrelford.md#6` — produced by: `chunker.py::split_documents`

```
# Kestrelford

## When to go

Late spring and early autumn. The Saturday market runs year-round but is much reduced from November to February. August is busy with walkers. The single-track approach road is genuinely difficult in snow and the town can be cut off for a day or two most winters.
```

**Chunk 5** — source: `guide_regional_transport.md#1` — produced by: `chunker.py::split_documents`

```
# Getting around the region

## The railway

The line runs along the river valley, connecting Brightwater to the regional
hub in 50 minutes. Eleven services a day on weekdays, six on Sundays. The line
north of Brightwater closed in 1963 and everything beyond it is bus or car.

Tickets are cheaper booked the day before than on the day, and considerably
cheaper than that booked a week ahead. There is no ticket office at
Brightwater station outside weekday mornings; the machine on the platform takes
cards only.
```

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question: What are the most difficult places to get around with limited mobility?**

**Answer:**

```
(best distance 0.586, cutoff 0.65)

According to `guide_accessibility.md`, the places that are difficult to get around with limited mobility are Kestrelford, Halden Bay, Corry Vale, and Elder Ness.

Sources retrieved: guide_accessibility.md, guide_corry_vale.md, guide_halden_bay.md, guide_thornby_wells.md, guide_walking.md

1 model calls this session, 767 tokens (730 in, 37 out)
```

**My relevance cutoff: 0.65**

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

| Question | In corpus? | Best distance |
|---|---|---|
|What are the four most difficult towns to get around with limited mobility?  | T | 0.5351 |
|What is the train frequency and duration to get to Brightwater? | T | 0.3091 |
|What town has fresh seafood?| T | 0.4043 |
|What can you see at Thornby Wells? | T | 0.3794 |
|When is the recommended time to go visit Kestrelford?| T | 0.3375 |
|What is the capital of Mongolia? | F | 0.7542 |
|How do I change the oil in a diesel engine | F | 0.8881 |
|Who won the 1994 World Cup? | F | 0.8990 |
|What is the recommended dosage of ibuprofen for a headache?| F | 0.8350 |
|How do I write a for loop in Rust?| F | 0.8365 |


Looking at the results for the corpus and out of scope questions, it does appear that there could be a clear gap that could be made when looking at distances.
For the in corpus questions, the hardest question had a best distance of 0.5351. For the out of scope questions, the closest question had the best distance of 0.7542. The existing 0.60 relevance cutoff did classify all ten correctly, but for now the midpoint of these two distances which is 0.645 is more well informed and
clearly derived so I set the relevance cutoff to be 0.65.

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1. I asked AI to review my acceptance criterion to make sure they met the self-check marks. It reviewed the two new criterion that I created as well as the my reasoning for their targets, ensuring that it was quantifiable and describes one thing. One of my criterion could have been more specific and it considered that that the test might not be reproducible. I changed the keyword "relevant" that I had used to be very specific, describing to look at the original corpus text sections, ensuring that the test was well defined and someone else could check it without any ambiguity.**



**2. I asked AI to help me write the chunking function that I had detailed and brainstormed. After reviewing the structure of the corpus I selected, city-guide, I realized that the original chunking by character length was not well suited, especially after seeing the results of the longest and shortest chunks. For this corpus specifically, I found that the city specific documents had very convenient sections with around 300 chars each explaining a specific topic about the city (what to eat, when to go, etc). With this observation, I found it reasonable to try to make these chunks correspond to each of these sections. I found that it was able to implement these details. I reviewed and it found that some parts could be more clearer/cleaner so I added some comments for readability.**

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

## Stretch Feature: Source Metadata Filtering

I added source metadata filtering so retrieval can be limited to one or more
specific source files with `--files`. `store.py::search` applies a Chroma `$in`
filter to the `source` metadata field. Both `app.py::cmd_retrieve` and
`app.py::ask_pipeline` pass their `--files` selections to this shared search
function.

I ran the same query with and without a source filter. Without the filter, the
top three results came from both `guide_halden_bay.md` and `guide_seasons.md`,
and the Halden Bay chunk ranked first. Filtering to `guide_seasons.md` removed
the Halden Bay result, returned only chunks from the selected source, and moved
the Summer section of `guide_seasons.md` into the first position.

**Without a filter:**

```text
python app.py retrieve "What are the best towns to visit during summer?" --top-k 3

Question: What are the best towns to visit during summer?

#   distance   source                           preview
----------------------------------------------------------------------------------------------------
1   0.5208     guide_halden_bay.md              # Halden Bay  ## When to go  June and September are ...
2   0.5461     guide_seasons.md                 # When to visit the region  ## Summer, June to Augus...
3   0.5564     guide_seasons.md                 # When to visit the region  ## Autumn, September to ...

Gate: best distance 0.521 is under the 0.65 cutoff
```

**Filtered to `guide_seasons.md`:**

```text
python app.py retrieve "What are the best towns to visit during summer?" --top-k 3 --files guide_seasons.md

Question: What are the best towns to visit during summer?

#   distance   source                           preview
----------------------------------------------------------------------------------------------------
1   0.5461     guide_seasons.md                 # When to visit the region  ## Summer, June to Augus...
2   0.5564     guide_seasons.md                 # When to visit the region  ## Autumn, September to ...
3   0.5934     guide_seasons.md                 # When to visit the region  ## Spring, March to May ...

Gate: best distance 0.546 is under the 0.65 cutoff
```

---

# Week 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     week 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunks contain the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunks preserve complete guide sections | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Cross-town answer includes every listed place | All 4 places | 4/4 | 4/4 | 4/4 | MET |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

The complete three-run raw results is in
[`results/run_2026-09-16_1419_before.md`](results/run_2026-09-16_1419_before.md).

### Criterion 1 — Retrieved chunks contain the answer

**Claim:** All five questions retrieved answer-bearing corpus content in each
run, for a result of 5/5 in all three runs. The Thornby Wells question below is
one representative run.

**Location:** `store.py::search` retrieved the chunks produced by
`chunker.py::split_documents`; `run_eval.py::write_report` recorded the result
in `results/run_2026-09-16_1419_before.md`.

**Output — Thornby Wells, run 1:**

```text
Best distance: 0.3794 (passed the gate)
Sources retrieved: guide_thornby_wells.md

Based on the documents, you can see the pump room (where you can drink the water), the formal and well-kept gardens behind the pump room, and the assembly rooms which host concerts most weekends (*guide_thornby_wells.md*).
```

### Criterion 2 — Every answer names a source

**Claim:** All five answers named at least one source in every run, for a result
of 5/5 in all three runs. The Brightwater answer below includes two named source
documents.

**Location:** `generate.py::answer_from_chunks` produced the answer, and
`run_eval.py::write_report` recorded it in
`results/run_2026-09-16_1419_before.md`.

**Output — Brightwater train, run 1:**

```text
Best distance: 0.3091 (passed the gate)
Sources retrieved: guide_brightwater.md, guide_kestrelford.md, guide_marchwood.md, guide_pellew_sands.md, guide_regional_transport.md, guide_thornby_wells.md

Trains run to Brightwater eleven times a day on weekdays and six times on Sundays, taking 50 minutes.

Source: `guide_brightwater.md` (also mentioned in `guide_regional_transport.md`)
```

### Criterion 3 — Gate stops out-of-corpus questions

**Claim:** The relevance gate refused all five out-of-corpus questions. This
retrieval-and-threshold check is deterministic, so the same 5/5 result appears
in all three run columns.

**Location:** `run_eval.py::check_out_of_scope` passed each question through
retrieval and `gate.py::check`; `run_eval.py::write_report` recorded the result
in `results/run_2026-09-16_1419_before.md`.

**Output — deterministic gate check:**

```text
Produced by `run_eval.py::check_out_of_scope`, cutoff 0.65. Refused 5 of 5.

| Out-of-scope question | Best distance | Gate |
|---|---|---|
| What is the capital of Mongolia? | 0.754 | refused |
| How do I change the oil in a diesel engine? | 0.888 | refused |
| Who won the 1994 World Cup? | 0.899 | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.835 | refused |
| How do I write a for loop in Rust? | 0.836 | refused |
```

### Criterion 4 — Chunks preserve complete guide sections

**Claim:** Each of the five sampled chunks contains one complete section and no
text from a neighboring section, for a result of 5/5. Repeating the command
three times produced the same deterministic sample. I counted the document
title and introductory paragraph in `guide_accessibility.md#0` as one complete
top-level introductory section.

**Location:** `chunker.py::split_documents` produced the chunks, and
`app.py::cmd_chunks` selected and printed the sample.

**Output — one run of `python app.py chunks -n 5`:**

```text
98 chunks total. Showing 5, spread across the corpus.

======================================================================
Chunk 1  |  source: guide_accessibility.md#0  |  produced by: chunker.py::split_documents
======================================================================
# Getting around the region with limited mobility

An honest assessment rather than a promotional one. Some of these places are
difficult and it is better to know in advance.

======================================================================
Chunk 2  |  source: guide_corry_vale.md#6  |  produced by: chunker.py::split_documents
======================================================================
# Corry Vale

## When to go

May to September. Outside those months the pub in the third village closes, the farm shop reduces its hours, and several footpaths become genuinely boggy rather than merely wet. The road is not gritted above the second village and is impassable in snow.

======================================================================
Chunk 3  |  source: guide_givens_mill.md#3  |  produced by: chunker.py::split_documents
======================================================================
# Givens Mill

## Eat and drink

A tearoom attached to the mill, open 10 to 4 daily except Tuesdays, which sells bread made from the flour ground twenty metres away and is the reason most people come. One pub, food served lunchtimes and Thursday to Saturday evenings.

======================================================================
Chunk 4  |  source: guide_kestrelford.md#6  |  produced by: chunker.py::split_documents
======================================================================
# Kestrelford

## When to go

Late spring and early autumn. The Saturday market runs year-round but is much reduced from November to February. August is busy with walkers. The single-track approach road is genuinely difficult in snow and the town can be cut off for a day or two most winters.

======================================================================
Chunk 5  |  source: guide_regional_transport.md#1  |  produced by: chunker.py::split_documents
======================================================================
# Getting around the region

## The railway

The line runs along the river valley, connecting Brightwater to the regional
hub in 50 minutes. Eleven services a day on weekdays, six on Sundays. The line
north of Brightwater closed in 1963 and everything beyond it is bus or car.

Tickets are cheaper booked the day before than on the day, and considerably
cheaper than that booked a week ahead. There is no ticket office at
Brightwater station outside weekday mornings; the machine on the platform takes
cards only.
```

### Criterion 5 — Cross-town answer includes every listed place

**Claim:** The limited-mobility answer named all four required places in each
run, for a result of 4/4 in all three runs.

**Location:** `run_eval.py::run_once` retrieved the context and called
`generate.py::answer_from_chunks`; `run_eval.py::write_report` recorded the
answer in `results/run_2026-09-16_1419_before.md`.

**Output — limited mobility, run 1:**

```text
Best distance: 0.5351 (passed the gate)
Sources retrieved: guide_accessibility.md, guide_corry_vale.md, guide_givens_mill.md, guide_walking.md

Based on the provided documents, the text lists four difficult locations for limited mobility: Kestrelford, Halden Bay, Corry Vale, and Elder Ness (guide_accessibility.md).
```


## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     week — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
