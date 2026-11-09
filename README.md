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
| 1 | Retrieved chunks contain the answer | MET | In every run, all five questions had at least one retrieved chunk containing information needed to answer the question. Each run scored 5/5, exceeding the 4/5 target. |
| 2 | Every answer names a source | MET| All five generated answers named at least one source document in every run. Each run scored 5/5, meeting the 5/5 target. |
| 3 | Gate stops out-of-corpus questions | MET | All five out-of-corpus questions had best distanced above the 0.65 cutoff, so the gate refused 5/5. Because the retrieval is deterministic, this one result is repeated across the three run columns. |
| 4 | Chunks preserve complete guide sections | MET | All five sampled chunked contained one complete section without text from an adjacent section. The same deterministic sample scored 5/5 in each check, exceeding the 4/5 target. |
| 5 | Cross-town answer includes every listed town | MET | In all three runs, the limited mobility answer named Kestrelford, Halden Bay, Corry Vale, and Elder Ness. Each run included all 4/4 required places.  |

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

No criteria were missed, so there is no failed pipeline stage or failure
mechanism to diagnose. All five criteria met their targets in every run and in fact got perfect 5/5 scores.
However this only shows that several of the tests were predictable or narrow.

### Target I Would Tighten

Criterion 4 was set too low. Its original target allowed one of the five
sampled chunks to mix sections, but all five chunks preserved their section
boundaries in every check. I would tighten its target from **4 of 5** to the
following:

> All 5 of the 5 chunks printed by `python app.py chunks -n 5` contain exactly
> one complete guide section, from its heading through its final sentence, and
> contain no text from another section.

This is a specific tighter target that is reasonable since the chunks really never do change after the first index. The original criterion was measurable and remains unchanged.


### Testing Gaps / Weaknesses

Although Criterion 1 was met, the retrieval stage showed a weak margin on the Thornby Wells question (Q4). The chunk containing the correct answer, `What to see`, ranked seventh, exactly at the `TOP_K = 7` boundary. Semantic similarity ranked several other Thornby Wells chunks above the answer section, so reducing top-k by even one would have caused a retrieval miss. This was not a formal failure, but it exposed a retrieval-stage weakness that the 5/5 results did not reflect.


Criterion 2 only checks whether an answer names a source, not whether that
source actually supports every claim in the answer. Because source metadata is
attached to every retrieved chunk and source naming is part of the generation
instructions, this was a relatively "safe" target. A stronger future
criterion would check that every named source contains the information used in
the answer, rather than checking only that a filename is present.

Criterion 3 is deterministic with the same indexed corpus, embeddings, questions,
and cutoff that produce the same retrieval distances. Repeating its 5/5 result in
three columns therefore does not provide three independent and meaningful trials. A stronger
future test would use a fixed set of harder out-of-corpus questions chosen
before running the evaluation. Those questions should deliberately share
travel or city-guide language with the corpus while still asking for facts the
documents do not contain. Keeping that harder set fixed would make the test
reproducible while putting more pressure on the 0.65 relevance cutoff.

Criterion 4 has a similar limitation because `python app.py chunks -n 5`
selects the same deterministic sample from the same corpus each time. Raising
the target to 5/5 makes the current standard stricter, but a broader future
test would inspect a predetermined set of chunks spanning town-specific
guides, cross-town guides, and introductory sections. It might also be reasonable to perhaps
index only a certain amount of sources in the corpus (not all at once) and essentially choose a partition of the whole corpus set to chunk across the runs, so that the results can be meaningful and independent across the stages.

Criterion 5 tests only one cross-town question. Repeating generation checks
whether the answer remains complete across model calls, but retrieval uses the
same question and therefore returns the same chunks each time. A stronger
future evaluation would include more cross-town questions and paraphrased
versions that ask for the same information without closely matching a corpus
section heading. The current question set would also be stronger with more of
this cross-town variety, because several existing questions closely resemble
the headings or wording in the source documents.

## The Improvement

**What I changed:**

I changed `store.py::search` from semantic-only retrieval to hybrid retrieval.
The function now ranks every candidate once by semantic similarity and once by
BM25 keyword matching, then combines those two rankings with reciprocal-rank
fusion. The final results keep their original cosine distances so the existing
0.65 relevance gate still measures semantic similarity.

**Why I picked it:**

I picked hybrid search because the Criterion 1 diagnosis found a specific
retrieval weakness for one of the questions, "What can you see at Thornby Wells?." Semantic search
placed the answer-bearing `What to see` chunk seventh, which was only revealed when changing
`TOP_K = 7`. Since BM25 could reward the exact town name and the question's
"see" wording (keywords), it directly addressed that weak ranking used during retrieval rather than changing
the chunking, relevance cutoff, or test questions.

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunks contain the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunks preserve complete guide sections | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Cross-town answer includes every listed place | All 4 places | 4/4 | 4/4 | 4/4 | MET |

The complete three-run raw results is in
[`run_2026-09-16_2058_after.md`](results/run_2026-09-16_2058_after.md).

**Did it help?**

Yes, it helped the specific retrieval weakness, although the five aggregate
criterion scores did not change because every before-run score was already at a 5/5. After the improvement, all five questions still passed in all
three runs, every answer still named a source, and the gate still refused all
5/5 out-of-corpus questions. This shows no regression on the original criteria.

The more meaningful comparison is the rank of the chunk that contains the answer to the Thornby Wells
question (Q4). The following output was produced by `app.py retrieve`, using
`store.py::search`, for `What can you see at Thornby Wells?` with `--top-k 10`.
Before hybrid search, semantic retrieval placed the needed section seventh:

```text
7   0.5180   guide_thornby_wells.md   ## What to see
8   0.5221   guide_walking.md          ## Easy, on good surfaces
```

After hybrid search, reciprocal-rank fusion placed that same section second:

```text
1   0.3794   guide_thornby_wells.md   # Thornby Wells  Thornby Wells was a spa town for ab...
2   0.5180   guide_thornby_wells.md   # Thornby Wells  ## What to see  The pump room is op...
3   0.4009   guide_thornby_wells.md   # Thornby Wells  ## Getting around  Flat and compact...
```

The `What to see` chunk's cosine distance stayed `0.5180` since hybrid search does
not change embeddings or semantic distance. The improvement was its position,
from rank 7 to rank 2, which gives the chunk containing the relevant information a much larger margin
inside `TOP_K = 7`.

## What's Still Broken

None of the five criteria remained missed after the improvement. However, the
passing scores do not mean that every part of the system is working as well as
it could. The clearest remaining problem is answer focus. In run 2 of the last
question, the system gave the requested seasons but then added related details
about the April market and August walkers that were not necessary to answer the
question. This output came from `run_eval.py::run_once`, which retrieved with
`store.py::search` and generated the answer with
`generate.py::answer_from_chunks`:

```text
Based on the provided documents, the recommended times to visit Kestrelford are late spring and early autumn (*guide_kestrelford.md*). Additionally, the Kestrelford Saturday market builds back to full size through April (*guide_seasons.md*). August is also noted as a busy time for walkers (*guide_kestrelford.md* / *guide_seasons.md*).
```

The additional statements are supported by the retrieved documents, so this
answer still passed the existing criteria. However, they make the answer less
direct and show a weakness that Criterion 2 does not measure. That criterion
only checks whether an answer names a source and it does not check whether every
claim is necessary, whether the named source supports that claim, or whether
extra retrieved sources distracted the model.

A next improvement would be to tighten the grounding prompt so it asks for only
the information needed to answer the question, then add a scorer or manual
criterion that checks every factual claim against its named source. I stopped
after hybrid retrieval because this unit permits one system improvement. A
prompt/criterion/test question change or a new scoring method would be a second change, but this would make it more difficult
to compare the before-and-after result to BM25 and reciprocal-rank fusion.

The evaluation itself also still has a ceiling problem. All five criteria
passed before the improvement, so the run-log totals could not show the rank
improvement from seventh to second. The separate retrieval output exposed that
change, but a stronger evaluation would have measured answer-chunk rank from
the beginning.

## What I'd Do Differently

Knowing what I know now, I would make Criterion 1 more strict by measuring
where the chunk that contains the answer appears, not just whether it appears anywhere in
the top seven. For example, I could require the relevant chunk to appear
in the top three results for at least four of five questions. That would have
captured the Thornby Wells weakness and made the effect of hybrid search visible
in the before-and-after run logs.

I would also replace Criterion 2's source-name check with a claim-support check where
every factual claim in an answer should be supported by the source named for
that claim. This would test citation quality instead of just looking at if the answer
included any filename.

The test questions should put more pressure on the system as well. I would
precommit a larger variety of town-specific, cross-town, and paraphrased
questions that do not closely repeat document headings. For the deterministic
out-of-corpus test, I would prepare multiple fixed sets of difficult questions
before testing. Each set would use city or travel vocabulary found in the
corpus while asking for facts the corpus does not contain. That would provide
meaningfully different trials without choosing easier or harder questions after
seeing results. Criterion 4 could similarly inspect a predetermined sample that
includes town guides, cross-town guides, and introductory chunks instead of
repeating the same five chunks. All of these questions, sets, and targets would
need to be written and committed before the next formal evaluation.

## How I Used AI — Unit 2

**3. I asked AI to help organize the evaluation evidence and look for patterns
that the 5/5 totals might hide.** It mapped claims to the relevant result files,
functions, and exact text output, and highlighted that the Thornby Wells
`What to see` chunk was only seventh under semantic retrieval. I checked that
against the actual retrieval output and used it as the specific weakness behind
my improvement. I kept the original criteria and test questions unchanged
rather than altering them after seeing the results.

**4. I asked AI for a high-level way to combine BM25 keyword search with the
existing semantic search using reciprocal-rank fusion.** After I implemented
the approach, retrieval raised a `KeyError`. I asked AI to review my code, and
it found that BM25 ranked every candidate while the semantic rank dictionary
contained only the first `top_k` candidates. It also pointed out that fusion
scores needed to be ordered from highest to lowest. I changed semantic retrieval
to rank the same candidate set as BM25, corrected the fusion ordering, and used
clearer names such as `candidate_index` to distinguish a candidate's original
index from its calculated rank. I questioned some specific coding decisions like the `enumerate` mapping it suggested, then verified both filtered and
unfiltered retrieval before running the formal after-test.

---

# Unit 9 Capstone

## The Shape

I am extending The Unofficial Guide, my Project 1 city-guides RAG system,
using **Shape A: Deploy and instrument**. The extension will add an operational
layer around the existing HTTP service in `serve.py`, which already calls the
same retrieval, relevance gate, and answer pipeline as the command line. I will
use **Path B: local with logs**, with one documented startup command in
`RUNNING.md` and setup instructions checked from a clean checkout. Each question
request will write a structured log record with a timestamp, the input, the
answer or error, and the elapsed time. I will also record actual token usage
per request so I can measure the cost of running the system. The service,
embedding model, and vector database will run locally, while generated answers
will continue to use the Gemini API.

## Out of Scope

- Changing the corpus, chunking strategy, or existing hybrid retrieval.
- Building a new interface or adding new question-answering capabilities.
- Publishing to a cloud host or adding a hosted monitoring dashboard.

## Scope Check

I am keeping the implementation within a roughly 90-minute build budget by
reusing `serve.py`, `app.py::ask_pipeline`, and the token counters in
`generate.py`. The planned changes are request logging, timing, per-request
token accounting, and reproducible local setup documentation. A JSONL file
will hold the structured records, without a separate logging service. This
leaves the rest of the unit for writing and committing five capstone criteria
before formal evaluation, running three trials per criterion before and after
one improvement, and documenting the results and remaining limitations.

## Build Extension

The operational layer is implemented around the existing local HTTP service.
`serve.py::start_request_record` starts a monotonic timer and assigns a request
identifier. `serve.py::finish_request_record` records the JSON input, response,
status, elapsed time, model, corpus, and API usage.
`request_log.py::append_record` appends one JSONL entry under a thread lock.
The response's `X-Request-ID` header links it to its record.

`generate.py::measure_usage` keeps accounting separate for each request using
a context variable. The original session counters remain available to the CLI.
Cache hits and refusals have zero new generation tokens. Failed API attempts
or missing usage metadata make the request's token total unknown, represented
by `null`. The recorded total comes from the API rather than an estimated price.

The run path and environment are documented in
[`RUNNING.md`](RUNNING.md#unit-9-capstone-local-run-path), with exact dependency
versions in [`requirements-lock.txt`](requirements-lock.txt).

## Development Check

These are Milestone 2 development checks, not the capstone acceptance trials.
The capstone's five criteria still need to be written and committed before
formal evaluation. No acceptance verdicts have been assigned.

**Claim:** A real local session returned a sourced answer, reused it from the
cache, refused an unrelated question, rejected blank input, and retained the
original CLI answer path.

**Location:** `tools/dev_session.py::main` starts `serve.py`, exercises
`serve.py::ask` and `app.py::ask_pipeline`, and runs the original CLI command.
The complete text transcript is in
[`results/capstone_milestone2_development.txt`](results/capstone_milestone2_development.txt).

**Output:**

```text
GET /health -> 200 {"corpus": "city_guides", "detail": "ready", "index_ready": true, "status": "ok"}
```

```text
CLI exit code: 0
(best distance 0.325, cutoff 0.65)

According to `guide_kestrelford.md`, late spring and early autumn are the best times to go to Kestrelford.

Sources retrieved: guide_kestrelford.md, guide_marchwood.md, guide_seasons.md, guide_walking.md

0 model calls this session, 1 served from cache
Verified four matching request records and the original CLI answer path
Development checks passed. No capstone acceptance verdicts were assigned.
```

The actual request records are preserved in
[`results/capstone_milestone2_development.jsonl`](results/capstone_milestone2_development.jsonl).
The following entry was written by `serve.py::finish_request_record` through
`request_log.py::append_record`:

```jsonl
{"timestamp": "2026-11-09T21:11:29.493109+00:00", "request_id": "7aade8b168c64eb5b0486ede9c5107d4", "method": "POST", "path": "/ask", "corpus": "city_guides", "model": "gemini-3.5-flash-lite", "cache_enabled": true, "usage": {"model_calls": 1, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 757, "output_tokens": 27, "total_tokens": 784}, "input": {"question": "When should I visit Kestrelford, according to the city guide?"}, "output": {"answer": "According to `guide_kestrelford.md`, late spring and early autumn are the best times to go to Kestrelford.", "best_distance": 0.3254, "corpus": "city_guides", "question": "When should I visit Kestrelford, according to the city guide?", "refused": false, "sources": ["guide_kestrelford.md", "guide_marchwood.md", "guide_seasons.md", "guide_walking.md"], "threshold": 0.65}, "status_code": 200, "duration_ms": 2464.52}
```

The uncached answer recorded 757 input tokens, 27 output tokens, and 784 total
tokens. Its repeated request recorded one cache hit and zero new API tokens.
The first record is a failed development attempt caused by sandbox access to
the embedding-model cache. The subsequent session passed with that access.

**Claim:** The documented setup worked from a clean local checkout with a new
virtual environment and a rebuilt index.

**Location:** The commands in `RUNNING.md` use `app.py::cmd_index` for indexing
and `serve.py::main` to start the service. The check used Windows and Python
3.12.10 at commit `1f16ce7`, with the pinned dependencies installed into a fresh
environment. It provisioned the ignored `.env` locally and reused the existing
per-user ONNX model cache. It did not reuse the original Chroma index or
response cache.

**Output:**

```text
No broken requirements found.
```

```text
Ran 10 tests in 0.057s

OK
```

```text
Corpus: city_guides
  loaded   14 documents, 28,958 characters, ~2,068 characters per document
  chunked  98 chunks, 310 characters on average (shortest 23, longest 762), produced by chunker.py::split_documents
  embedding 98 chunks (first run downloads the model)...
  stored   98 chunks in 2.0s

Ready. Try: python app.py ask "your question here"
```

```text
Fresh environment, rebuilt index, local HTTP service, and CLI checks passed.
```

The complete
[`clean-checkout transcript`](results/capstone_milestone2_clean_checkout.txt)
also preserves the initial setup-command error and its correction. The CLI's
global `--corpus` option must appear before `index`. Its four real request
records are in
[`results/capstone_milestone2_clean_checkout.jsonl`](results/capstone_milestone2_clean_checkout.jsonl).

## Instrumentation

**Claim:** The local HTTP service writes a structured record for each question
request, including requests that fail.

**Location:** `serve.py::start_request_record` assigns the timestamp and request
identifier. `serve.py::finish_request_record` records the parsed input, returned
output, HTTP status, elapsed milliseconds, corpus, model, cache setting, and
per-request API usage. `request_log.py::append_record` writes the JSONL file.
`generate.py::measure_usage` attributes calls and tokens to the current request.

**Run path:** Path B, using the single startup command in
[`RUNNING.md`](RUNNING.md#unit-9-capstone-local-run-path). Milestone 3 verified it
in a new local clone of commit `0f6f05f`, using Python 3.12.10, a fresh virtual
environment installed from `requirements-lock.txt`, and a newly built Chroma
index. The ignored `.env` was provisioned locally with the API key. The existing
per-user ONNX model cache was reused. This checked a local clone of the current
code, rather than claiming that unpushed commits were available on GitHub.

The complete command and response transcript is in
[`results/capstone_milestone3_session.txt`](results/capstone_milestone3_session.txt).
The normal setup succeeded with the corrected command documented in Milestone 2.
A separate controlled probe started the server before indexing. Its health
response reported `index_ready: false`, and `store.py::search` raised the
missing-index error recorded as HTTP 500. After indexing and restarting, a
blank question returned HTTP 400. Both failed requests made zero model calls.
They are retained as failure evidence and excluded from the generated-answer
cost sample.

**Output:** These are all 12 unmodified request records from that real session,
also committed in
[`results/capstone_milestone3_requests.jsonl`](results/capstone_milestone3_requests.jsonl).
The first two are the deliberate failures. The remaining ten are the uncached
cost sample. Health checks are outside the question log.

```jsonl
{"timestamp": "2026-11-09T21:27:28.204548+00:00", "request_id": "0f863b6cda9a4e4d8520869ee8d3401a", "method": "POST", "path": "/ask", "corpus": "city_guides", "model": "gemini-3.5-flash-lite", "cache_enabled": false, "usage": {"model_calls": 0, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 0, "output_tokens": 0, "total_tokens": 0}, "input": {"question": "When should I visit Kestrelford?"}, "output": {"error": "RuntimeError: unable to answer question"}, "status_code": 500, "duration_ms": 26.202}
{"timestamp": "2026-11-09T21:27:32.085202+00:00", "request_id": "c4e1d46c487b4c1893b27a06becce818", "method": "POST", "path": "/ask", "corpus": "city_guides", "model": "gemini-3.5-flash-lite", "cache_enabled": false, "usage": {"model_calls": 0, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 0, "output_tokens": 0, "total_tokens": 0}, "input": {"question": " "}, "output": {"error": "Send JSON with a question in it, like {\"question\": \"When should I visit Kestrelford?\"}"}, "status_code": 400, "duration_ms": 0.705}
{"timestamp": "2026-11-09T21:27:32.215513+00:00", "request_id": "96d4c4c96faa4c489d0bf3de5636e151", "method": "POST", "path": "/ask", "corpus": "city_guides", "model": "gemini-3.5-flash-lite", "cache_enabled": false, "usage": {"model_calls": 1, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 716, "output_tokens": 50, "total_tokens": 766}, "input": {"question": "When should I visit Kestrelford?"}, "output": {"answer": "You should visit Kestrelford in late spring and early autumn (*guide_kestrelford.md*). Additionally, August is a busy time with walkers (*guide_kestrelford.md* and *guide_seasons.md*).", "best_distance": 0.3251, "corpus": "city_guides", "question": "When should I visit Kestrelford?", "refused": false, "sources": ["guide_kestrelford.md", "guide_seasons.md"], "threshold": 0.65}, "status_code": 200, "duration_ms": 2417.433}
{"timestamp": "2026-11-09T21:27:34.662986+00:00", "request_id": "601dff13360a4b2ab516082d857de4c2", "method": "POST", "path": "/ask", "corpus": "city_guides", "model": "gemini-3.5-flash-lite", "cache_enabled": false, "usage": {"model_calls": 1, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 716, "output_tokens": 78, "total_tokens": 794}, "input": {"question": "When should I visit Kestrelford?"}, "output": {"answer": "You should visit Kestrelford in late spring and early autumn (*guide_kestrelford.md*). Additionally, August is busy with walkers, while November to February features a much reduced Saturday market and a difficult single-track approach road that can cut the town off for a day or two (*guide_kestrelford.md* and *guide_seasons.md*).", "best_distance": 0.3251, "corpus": "city_guides", "question": "When should I visit Kestrelford?", "refused": false, "sources": ["guide_kestrelford.md", "guide_seasons.md"], "threshold": 0.65}, "status_code": 200, "duration_ms": 849.282}
{"timestamp": "2026-11-09T21:27:35.519298+00:00", "request_id": "a5af1c6f273b4fd09ee7417a6e8b8160", "method": "POST", "path": "/ask", "corpus": "city_guides", "model": "gemini-3.5-flash-lite", "cache_enabled": false, "usage": {"model_calls": 1, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 716, "output_tokens": 50, "total_tokens": 766}, "input": {"question": "When should I visit Kestrelford?"}, "output": {"answer": "You should visit Kestrelford in late spring and early autumn (*guide_kestrelford.md*). Additionally, August is a busy time with walkers (*guide_kestrelford.md* and *guide_seasons.md*).", "best_distance": 0.3251, "corpus": "city_guides", "question": "When should I visit Kestrelford?", "refused": false, "sources": ["guide_kestrelford.md", "guide_seasons.md"], "threshold": 0.65}, "status_code": 200, "duration_ms": 761.198}
{"timestamp": "2026-11-09T21:27:36.287174+00:00", "request_id": "da9391c3b9d24eba86097b62eaf4b270", "method": "POST", "path": "/ask", "corpus": "city_guides", "model": "gemini-3.5-flash-lite", "cache_enabled": false, "usage": {"model_calls": 1, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 716, "output_tokens": 50, "total_tokens": 766}, "input": {"question": "When should I visit Kestrelford?"}, "output": {"answer": "You should visit Kestrelford in late spring and early autumn (*guide_kestrelford.md*). Additionally, August is a busy time with walkers (*guide_kestrelford.md* and *guide_seasons.md*).", "best_distance": 0.3251, "corpus": "city_guides", "question": "When should I visit Kestrelford?", "refused": false, "sources": ["guide_kestrelford.md", "guide_seasons.md"], "threshold": 0.65}, "status_code": 200, "duration_ms": 763.041}
{"timestamp": "2026-11-09T21:27:37.066379+00:00", "request_id": "3074cfd108ac47cd9408d065aee0e7ea", "method": "POST", "path": "/ask", "corpus": "city_guides", "model": "gemini-3.5-flash-lite", "cache_enabled": false, "usage": {"model_calls": 1, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 716, "output_tokens": 24, "total_tokens": 740}, "input": {"question": "When should I visit Kestrelford?"}, "output": {"answer": "According to `guide_kestrelford.md`, you should visit Kestrelford in late spring and early autumn.", "best_distance": 0.3251, "corpus": "city_guides", "question": "When should I visit Kestrelford?", "refused": false, "sources": ["guide_kestrelford.md", "guide_seasons.md"], "threshold": 0.65}, "status_code": 200, "duration_ms": 641.772}
{"timestamp": "2026-11-09T21:27:37.714859+00:00", "request_id": "daaaef84435c48ac8880b62150ec320a", "method": "POST", "path": "/ask", "corpus": "city_guides", "model": "gemini-3.5-flash-lite", "cache_enabled": false, "usage": {"model_calls": 1, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 716, "output_tokens": 50, "total_tokens": 766}, "input": {"question": "When should I visit Kestrelford?"}, "output": {"answer": "You should visit Kestrelford in late spring and early autumn (*guide_kestrelford.md*). Additionally, August is a busy time with walkers (*guide_kestrelford.md* and *guide_seasons.md*).", "best_distance": 0.3251, "corpus": "city_guides", "question": "When should I visit Kestrelford?", "refused": false, "sources": ["guide_kestrelford.md", "guide_seasons.md"], "threshold": 0.65}, "status_code": 200, "duration_ms": 621.07}
{"timestamp": "2026-11-09T21:27:38.361324+00:00", "request_id": "762de942272343da97a53259ca35ada2", "method": "POST", "path": "/ask", "corpus": "city_guides", "model": "gemini-3.5-flash-lite", "cache_enabled": false, "usage": {"model_calls": 1, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 716, "output_tokens": 58, "total_tokens": 774}, "input": {"question": "When should I visit Kestrelford?"}, "output": {"answer": "Based on the provided documents, you should visit Kestrelford in late spring and early autumn (*guide_kestrelford.md*). Additionally, August is noted as a busy month with walkers (*guide_kestrelford.md* and *guide_seasons.md*).", "best_distance": 0.3251, "corpus": "city_guides", "question": "When should I visit Kestrelford?", "refused": false, "sources": ["guide_kestrelford.md", "guide_seasons.md"], "threshold": 0.65}, "status_code": 200, "duration_ms": 545.529}
{"timestamp": "2026-11-09T21:27:38.913168+00:00", "request_id": "e0e9fe1303f1400a913d6cf1f281d37d", "method": "POST", "path": "/ask", "corpus": "city_guides", "model": "gemini-3.5-flash-lite", "cache_enabled": false, "usage": {"model_calls": 1, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 716, "output_tokens": 50, "total_tokens": 766}, "input": {"question": "When should I visit Kestrelford?"}, "output": {"answer": "You should visit Kestrelford in late spring and early autumn (*guide_kestrelford.md*). Additionally, August is a busy time with walkers (*guide_kestrelford.md* and *guide_seasons.md*).", "best_distance": 0.3251, "corpus": "city_guides", "question": "When should I visit Kestrelford?", "refused": false, "sources": ["guide_kestrelford.md", "guide_seasons.md"], "threshold": 0.65}, "status_code": 200, "duration_ms": 669.813}
{"timestamp": "2026-11-09T21:27:39.590033+00:00", "request_id": "db62aa5ab2174754b5a75bcb9784c9c0", "method": "POST", "path": "/ask", "corpus": "city_guides", "model": "gemini-3.5-flash-lite", "cache_enabled": false, "usage": {"model_calls": 1, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 716, "output_tokens": 50, "total_tokens": 766}, "input": {"question": "When should I visit Kestrelford?"}, "output": {"answer": "You should visit Kestrelford in late spring and early autumn (*guide_kestrelford.md*). Additionally, August is a busy time with walkers (*guide_kestrelford.md* and *guide_seasons.md*).", "best_distance": 0.3251, "corpus": "city_guides", "question": "When should I visit Kestrelford?", "refused": false, "sources": ["guide_kestrelford.md", "guide_seasons.md"], "threshold": 0.65}, "status_code": 200, "duration_ms": 697.141}
{"timestamp": "2026-11-09T21:27:40.315391+00:00", "request_id": "c16171d7db274b919bea929c1608504d", "method": "POST", "path": "/ask", "corpus": "city_guides", "model": "gemini-3.5-flash-lite", "cache_enabled": false, "usage": {"model_calls": 1, "cache_hits": 0, "usage_complete": true, "prompt_tokens": 716, "output_tokens": 48, "total_tokens": 764}, "input": {"question": "When should I visit Kestrelford?"}, "output": {"answer": "You should visit Kestrelford in late spring and early autumn (guide_kestrelford.md). August is also a time when the town fills with walkers (guide_kestrelford.md and guide_seasons.md).", "best_distance": 0.3251, "corpus": "city_guides", "question": "When should I visit Kestrelford?", "refused": false, "sources": ["guide_kestrelford.md", "guide_seasons.md"], "threshold": 0.65}, "status_code": 200, "duration_ms": 866.875}
```

## What It Costs

**Measured cost:** **766.8 API tokens per generated
question request**, averaged over ten sequential requests to
`gemini-3.5-flash-lite`. The ten calls consumed
**7,668 tokens** in total, consisting of
7,160 input tokens and
508 output tokens. The mean was
716 input tokens and
50.8 output tokens per request.

**Method:** Start the local server with `AI201_CACHE=0`, then run
`tools/measure_cost.py` as documented in `RUNNING.md`. The client sends
`When should I visit Kestrelford?` ten times, matching each response's
`X-Request-ID` to its actual JSONL record. All ten requests returned an answer,
made exactly one API call, had zero local cache hits, and had complete usage
metadata. No measured request was discarded. The two deliberate failure
probes were separate from these ten requests. The average is the sum of the
ten API-reported totals divided by ten, or
`7668 / 10 = 766.8` tokens.

**Location:** `generate.py::_record_tokens` reads the API's `usage_metadata`,
`serve.py::finish_request_record` stores the per-request usage, and
`tools/measure_cost.py::main` computes the totals and arithmetic means. The
sample identifiers, per-run measurements, and computed summary are committed
in [`results/capstone_milestone3_cost.json`](results/capstone_milestone3_cost.json).

**Output:**

```text
Mean API tokens per request: 766.8
Mean server duration: 883.315 ms
Total API tokens: 7668 across 10 requests
```

The mean server elapsed time was 0.883 seconds
per request, including the first answer's model-loading time. It excludes setup,
index building, writing the log entry, and network transfer to the client.
Elapsed time is not CPU time. Tokens are the cost unit here, rather than a
dollar charge inferred from a pricing page. This sample measures one fixed
question and does not establish the average cost of every city-guide question.
It is an operational measurement for Milestone 3, with no capstone acceptance
verdicts assigned. The formal before-and-after evaluation will use the
[Unit 9 criteria](criteria.md#unit-9-capstone-acceptance-criteria) after their
commit checkpoint.

## How I Used AI - Unit 9 Build

**Tool:** Codex.

**Scope planning:** I asked for a simple local capstone extension of Project 1.
Codex inspected the existing server and suggested Shape A with Path B. I agreed
to that direction and asked it to write Milestone 1, with no semicolons.

**Implementation:** I asked Codex to build the scoped extension for Milestone 2
and commit as it went. It added logging, timing, and request-scoped accounting,
then ran synthetic development tests and real HTTP and CLI checks. The clean
checkout exposed an incorrect setup command, which it corrected and reran.

**Instrumentation:** I asked Codex to complete Milestone 3. It tested a new local
checkout, captured two deliberate failure probes and ten uncached API requests,
and calculated the mean token usage from the real structured records. It pasted
the records and method into the README. These measurements are operational
evidence and were not scored against capstone acceptance criteria.

**Criteria:** I gave Codex my priorities of a working local endpoint, expected
error responses, and measurable logs, and agreed to the earlier timing and
accounting focuses. I authorized help drafting the five criteria and chose
the larger of 50 milliseconds or 10 percent for timing accuracy. Codex wrote
the measurement procedures, technical rationales, and self-check, while
preserving the original Project 1 criteria and the chronology of earlier
operational measurements. These criteria were developed with AI assistance.

**Student review and reflection:** Scott still needs to review the code and
describe what he changed or learned. This build record does not supply a
personal reflection on his behalf.
