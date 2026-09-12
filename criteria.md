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
