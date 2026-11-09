# Capstone submission audit

Audit time: 2026-11-09T23:14:18.519482+00:00

**Local verdict:** The local write-up and saved evidence cover the supplied
capstone milestones and required features. This is an audit of the local
repository, not confirmation of a portal submission or a grading outcome.

| Check | Result | Evidence |
|---|---|---|
| Same existing project and repository | PASS | Original Project 1 repository and URL retained |
| Shape and scope declared | PASS | README.md: The Shape and Out of Scope |
| Single local startup command and environment | PASS | RUNNING.md: local command, Python, dependencies, index setup, and model sizes |
| Exact dependency pins | PASS | requirements-lock.txt contains exact versions |
| Installed environment matches the lock | PASS | Installed package versions match every pinned dependency |
| Clean-checkout run records | PASS | Committed clean-checkout and Milestone 3 transcripts |
| At least ten exact structured records pasted | PASS | README.md: Instrumentation contains 12 original JSONL entries |
| Failure records included | PASS | Missing-index and blank-input errors are preserved |
| Five capstone targets and rationales | PASS | criteria.md: five active criteria, fixed inputs, and self-check, with historical criteria below |
| Extension and bad-path coverage | PASS | All five cover operational extension behavior, including six deliberate failure cases |
| Criteria precede formal results | PASS | Criteria f7d1fb1 and cleanup e036e3a predate first formal results aac22e1 |
| before has three trials | PASS | results/capstone_before_verified/manifest.json and summary.json |
| before run log pasted | PASS | Five rows with three trial columns and verdicts |
| after has three trials | PASS | results/capstone_after/manifest.json and summary.json |
| after run log pasted | PASS | Five rows with three trial columns and verdicts |
| 102 complete formal request records | PASS | 51 before and 51 after, with matching responses and unique request identifiers |
| Original miss and diagnosis retained | PASS | README.md: baseline diagnosis and original four-attempt evidence |
| One measured application improvement | PASS | Pacing only, with unchanged criteria, evaluator, retrieval, corpus, and prompts |
| All final criteria called MET | PASS | All five after-run targets hold in all three trials |
| Before and after plus tradeoff | PASS | Side-by-side verdicts and the measured increase in answer time |
| Ten-run cost and hundred-person arithmetic | PASS | 7,668 / 10 = 766.8 tokens per uncached question, then 100 * 766.8 = 76,680 tokens per day |
| Remaining limitations and reason for stopping | PASS | Answer focus, claim support, single configured HTTP corpus, and bounded scope |
| Two-sentence next priority | PASS | Claim-to-source verification first, with a reason for prioritizing it |
| Two specific AI-use examples | PASS | Implementation collaboration and extra unit checks plus formal criterion testing |
| Meaningful commit history | PASS | Capstone scope, implementation, criteria, evaluation, improvement, and result commits |
| Capstone file links resolve | PASS | All relative links in capstone prose point to existing files |
| Credentials and local runtime data excluded | PASS | .env is untracked, runtime directories are ignored, and tracked content contains no detected credential values |
| Unpublished history checked for credentials | PASS | No detected key values in the local commits beyond the verified remote main |
| New prose follows writing constraints | PASS | No new semicolons or third-person references in the final write-up |

## Chronology and measurement boundaries

The development checks and Milestone 3 cost records precede the capstone
criteria. The criteria precede the formal before-and-after acceptance runs.
This sequence is disclosed in criteria.md and the README. No claim is made
that the criteria preceded every operational observation. Criteria wording
was developed with AI assistance, as described in the final AI-use section.

The ten-request cost sample was measured before the pacing improvement.
Its token arithmetic remains the recorded sample, and the separate formal
retest reports the increased response time after pacing. The 100-person
projection assumes one comparable uncached question per person each day.
It is not a test of concurrent users or a dollar-price estimate.

The two incomplete evaluator attempts are retained with their explanations.
Only the three complete before and three complete after trials are used for
the comparison. The current runtime still matches the successful after-run
fingerprints. No additional model calls were needed for these documentation
changes and artifact checks.

## Publication and submission snapshot

Repository URL: https://github.com/phamhscott/ai201-project1-unofficial-guide-starter-v2026

Read-only GitHub checks confirmed PUBLIC visibility, default branch main,
and remote main at `97717b4e697e38bfabd78bd498b21811d2558c92`.
The local results commit before this final write-up is `9584567`.
The capstone work has not been pushed during this collaboration.
Publishing the final local main branch is still pending confirmation of the
destination. Two older unpublished local commits, `c3ede33` and `9241335`,
also precede the capstone commits and remain in the branch history.

Portal submission has not been performed or verified. No authenticated
CodePath submission tool is connected in this session. The repository URL
must be submitted through the Unit 9 Deliverables Checklist after the final
repository contents have been published.
