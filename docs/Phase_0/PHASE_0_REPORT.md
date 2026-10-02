# Kriva — Phase 0 Report (Pilot)

**Question.** Can a cheap or local model complete real software-engineering tasks well enough that routing between models saves premium-model usage without hurting success — and can the result be verified automatically?

**Short answer.** The pilot is directionally positive but too small to prove the benchmark exit criterion. On 18 verified tasks from two projects, a 7B local model solved 5 and a 550B hosted model solved 10 (of 17 completed runs). The two models solved different tasks. A "try cheap, verify with tests, escalate on failure" cascade solved 11 of 18 using 13 premium calls, against 10 of 18 for always-premium using 18 calls: **28% fewer premium calls with no loss in success**, below the roadmap's 40% bar. A simple rule router (easy tasks to the cheap model, everything else to premium) used 14 premium calls (22% fewer) and solved 10 of 18. Both figures were computed after the fact on single attempts, and both depend on a test being available to verify each answer.

---

## 1. Method

- **Projects and task sources.**
  - *hcl-challenge:* 73 non-merge commits triaged into task cards (instruction, acceptance criteria, difficulty label, verifier). 22 were not tasks, 42 were single tasks and 9 were bundles split into sub-tasks.
  - *glassboard:* 45 task cards were triaged. 15 were usable benchmark candidates (10 tier A, 5 tier B), 22 were lower-confidence tier C and 8 were dropped.
- **Oracle validation.** A task counts only if its test **fails on the parent commit and passes on the real fix**.
  - *hcl-challenge:* 5 validated tasks out of 73 commits (about 7%). Two had native tests, three used tests borrowed from a later commit, and one borrowed test was rejected because it already passed on the parent.
  - *glassboard:* all 15 candidates had native tests from the same commit. 13 validated and 2 were excluded (see Limitations). The first validation pass in the benchmark harness showed 9 valid and 6 invalid; four of the six were harness bugs (a required `JWT_SECRET_KEY` environment variable was missing in temp worktrees) and were recovered once the variable was set.
  - **Total: 18 validated tasks** (4 easy, 10 medium, 4 hard).
- **Models and setup.** `qwen2.5-coder:7b` (local, Ollama, temperature 0) and `nvidia/nemotron-3-ultra-550b-a55b` (550B total / 55B active, NVIDIA-hosted API, default sampling, max 32k output tokens). Both receive the task, the acceptance criteria and the current content of the relevant files, and must return complete updated files. Oracle tests are hidden from the model and copied in after its edit. One attempt per task. "Frontier" in this report means Nemotron 3 Ultra via NVIDIA's endpoint, not a closed commercial model.
- **Run validity check.** Every counted run was required to show `baseline_exit = 1` (the oracle fails on the unmodified parent for the right reason). Runs with a different baseline were environment errors and were rerun, not counted.
- **Task contracts.** The hcl-challenge cards were rewritten (v2) to state interface details the tests assert (function names, exact strings, IDs). The glassboard cards were used as authored; their acceptance criteria already quote the exact test names, strings and IDs, but they were not rewritten.

## 2. Results

<div align="center">
<table>
<thead>
<tr>
<th style="background-color:#1f2937;color:#ffffff;padding:6px 14px;">Task</th>
<th style="background-color:#1f2937;color:#ffffff;padding:6px 14px;">Difficulty</th>
<th style="background-color:#1f2937;color:#ffffff;padding:6px 14px;">qwen2.5-coder 7B</th>
<th style="background-color:#1f2937;color:#ffffff;padding:6px 14px;">Nemotron 3 Ultra 550B</th>
</tr>
</thead>
<tbody>
<tr><td colspan="4"><i>hcl-challenge</i></td></tr>
<tr><td>AI Engineer taxonomy</td><td align="center">medium</td><td align="center">fail</td><td align="center">pass*</td></tr>
<tr><td>Goal-confidence handling</td><td align="center">medium</td><td align="center">fail</td><td align="center">fail</td></tr>
<tr><td>Password hashing</td><td align="center">medium</td><td align="center">pass</td><td align="center">pass</td></tr>
<tr><td>Learner ownership / 404</td><td align="center">hard</td><td align="center">pass</td><td align="center">fail</td></tr>
<tr><td>Roadmap deletion lifecycle</td><td align="center">medium</td><td align="center">fail</td><td align="center">pass</td></tr>
<tr><td colspan="4"><i>glassboard</i></td></tr>
<tr><td>Board task API</td><td align="center">medium</td><td align="center">fail</td><td align="center">fail</td></tr>
<tr><td>Vercel CORS origin</td><td align="center">medium</td><td align="center">fail</td><td align="center">pass</td></tr>
<tr><td>Root endpoint</td><td align="center">easy</td><td align="center">pass</td><td align="center">pass</td></tr>
<tr><td>Auto-seed on startup</td><td align="center">easy</td><td align="center">fail</td><td align="center">fail</td></tr>
<tr><td>Health DB ping</td><td align="center">easy</td><td align="center">fail</td><td align="center">fail</td></tr>
<tr><td>HEAD on root / health</td><td align="center">easy</td><td align="center">pass</td><td align="center">pass</td></tr>
<tr><td>AI evidence check</td><td align="center">medium</td><td align="center">fail</td><td align="center">fail</td></tr>
<tr><td>Challenge-failure verdict</td><td align="center">medium</td><td align="center">pass</td><td align="center">pass</td></tr>
<tr><td>Propose-task filter</td><td align="center">medium</td><td align="center">fail</td><td align="center">pass</td></tr>
<tr><td>Invalid task column</td><td align="center">medium</td><td align="center">fail</td><td align="center">pass</td></tr>
<tr><td>Downstream regression</td><td align="center">hard</td><td align="center">fail</td><td align="center">pass</td></tr>
<tr><td>Invariant audit rollback</td><td align="center">hard</td><td align="center">fail</td><td align="center">fail</td></tr>
<tr><td>Board authorization</td><td align="center">hard</td><td align="center">fail</td><td align="center">no result†</td></tr>
<tr><td><b>Total</b></td><td></td><td align="center"><b>5 / 18</b></td><td align="center"><b>10 / 17 completed<br>(10 / 18 if the missing run counts as a fail)</b></td></tr>
</tbody>
</table>
</div>

<p align="center"><b>Table 1.</b> Pass/fail per task, single attempt. *The first Nemotron run of the taxonomy task was discarded as an environment error (pytest collection failure) and rerun in isolation. †Board authorization: the Nemotron call failed three times with provider errors (HTTP 504, then two connection resets) and never returned a result. It is neither a pass nor a fail and is excluded from the 17 completed runs.</p>

<div align="center">
<table>
<thead>
<tr>
<th style="background-color:#1f2937;color:#ffffff;padding:6px 14px;">Difficulty</th>
<th style="background-color:#1f2937;color:#ffffff;padding:6px 14px;">Tasks</th>
<th style="background-color:#1f2937;color:#ffffff;padding:6px 14px;">qwen 7B</th>
<th style="background-color:#1f2937;color:#ffffff;padding:6px 14px;">Nemotron 550B</th>
</tr>
</thead>
<tbody>
<tr><td>Easy</td><td align="center">4</td><td align="center">2 / 4</td><td align="center">2 / 4</td></tr>
<tr><td>Medium</td><td align="center">10</td><td align="center">2 / 10</td><td align="center">7 / 10</td></tr>
<tr><td>Hard</td><td align="center">4</td><td align="center">1 / 4</td><td align="center">1 / 3 completed</td></tr>
<tr><td><b>All</b></td><td align="center"><b>18</b></td><td align="center"><b>5 / 18</b></td><td align="center"><b>10 / 17</b></td></tr>
</tbody>
</table>
</div>

<p align="center"><b>Table 2.</b> Results by difficulty label. The easy row is only 4 tasks; the medium gap is the clearest signal in the data.</p>

<div align="center">
<table>
<thead>
<tr>
<th style="background-color:#1f2937;color:#ffffff;padding:6px 14px;">Approach</th>
<th style="background-color:#1f2937;color:#ffffff;padding:6px 14px;">Tasks solved</th>
<th style="background-color:#1f2937;color:#ffffff;padding:6px 14px;">Premium calls</th>
<th style="background-color:#1f2937;color:#ffffff;padding:6px 14px;">Premium calls saved</th>
<th style="background-color:#1f2937;color:#ffffff;padding:6px 14px;">Mean latency / task</th>
<th style="background-color:#1f2937;color:#ffffff;padding:6px 14px;">Tokens (in / out)</th>
</tr>
</thead>
<tbody>
<tr><td>Cheap only (qwen 7B)</td><td align="center">5 / 18</td><td align="center">0</td><td align="center">—</td><td align="center">262 s (local)</td><td align="center">62,419 / 37,451</td></tr>
<tr><td>Premium only (Nemotron)</td><td align="center">10 / 18</td><td align="center">18</td><td align="center">baseline</td><td align="center">200 s</td><td align="center">66,100 / 70,420</td></tr>
<tr><td>Rule router: easy to qwen, rest to Nemotron (post hoc)</td><td align="center">10 / 18</td><td align="center">14</td><td align="center">22%</td><td align="center">not measured</td><td align="center">not measured</td></tr>
<tr><td>Cascade: qwen first, escalate on failed test (post hoc)</td><td align="center">11 / 18</td><td align="center">13</td><td align="center">28%</td><td align="center">not measured</td><td align="center">not measured</td></tr>
</tbody>
</table>
</div>

<p align="center"><b>Table 3.</b> Per-approach comparison. The router and cascade rows are derived from Table 1 after the fact, not run as live systems. Premium-only counts the one run without a result as unsolved, and its latency and tokens cover the 17 completed runs. If that run had passed, premium-only and the two derived rows would each gain one solved task and the call counts would not change. Cost in currency is not reported: the local model has no per-call cost and the hosted endpoint's pricing varies by provider, so token counts are given instead.</p>

## 3. Findings

1. **Verifiable tasks are scarce.** Only about 7% of hcl-challenge commits produced a usable oracle (that project has no frontend tests), and 15 of 45 glassboard cards were benchmark candidates. A real router cannot assume tests exist and needs weaker signals (build, typecheck, lint) as fallbacks.
2. **The gap is at medium difficulty, not on easy tasks.** On easy tasks both models solved 2 of 4. On medium tasks the 7B model solved 2 of 10 and the 550B model 7 of 10. This is the pattern routing relies on, but the easy sample is 4 tasks, so H1 (cheap models handle a large share of easy tasks) gets only a weak test.
3. **Success does not track model size on every task.** Qwen solved the hcl-challenge "hard" ownership task that Nemotron failed, and Nemotron failed two of the four easy tasks. A router picking by size or price alone would miss this, but with single attempts some of it is noise.
4. **Verification enables the saving.** The cascade works only because a test can say "this answer failed, escalate." It solved one more task than always-premium (11 vs 10), entirely from the ownership task, and used 5 fewer premium calls. This supports H3 and motivates the verify-and-escalate loop planned for later phases.
5. **Whole-file rewrites cause collateral damage in both models.** Of qwen's 10 glassboard failures, 4 were structural: two dropped an `import os` while rewriting several files, one dropped a `datetime` import (at 16k context; at 8k the same task failed on a broken import) and one produced an invalid Pydantic decorator that failed at collection. Nemotron's 2 structural failures invented project structure: it wrote a `backend/config.py` that imports an unneeded `pydantic_settings` package, and imported a nonexistent `backend.models.board`. Output formats that edit less than a whole file are worth testing.
6. **Some failures are format failures, not ability failures.** Qwen returned no parseable file blocks on 2 hard glassboard tasks (board authorization, invariant audit rollback), producing 25 and 137 output tokens. A stricter output contract or a retry might change these.
7. **Results are noisy and the hosted endpoint is unreliable.** Nemotron passed one task in one run and failed it in another under default sampling. It also returned 503/504 overloads and, on board authorization, three failed calls that never produced a result. One attempt per task is not reliable evidence.

## 4. Limitations

- **Small sample.** 18 tasks from two projects, one attempt each, against a roadmap target of about 100. One task is about 5.6 percentage points, so the "at most 5 points lost" test cannot be resolved. No confidence intervals can be given and percentages should not be quoted as results.
- **One missing result.** Nemotron produced no result on glassboard board authorization after three provider failures. It is reported as "no result" and handled both ways in Table 3.
- **Two tasks excluded.** `glassboard-17-auth-hardening` and `glassboard-20-username-onboarding` still fail oracle validation on the real fix because their tests need a database bootstrap (table creation and seeding) that the benchmark harness does not run in temp worktrees. They are excluded, not failed.
- **qwen context size.** The hcl-challenge runs used a 16k context window. The first glassboard qwen batch's setting was not recorded; the later reruns used 8k. Because the downstream-regression prompt plus output was about 8.4k tokens, that task was rerun at 16k and failed again (a different dropped-import error), so context size did not explain the failure. The 16k run is the one counted in the tables. The other qwen failures had small outputs.
- **Only 4 easy tasks.** Easy-task claims are weak. The hard tasks (4) are also few and are exactly where the models disagree most.
- **No live router was run.** The rule router and cascade are hindsight calculations from single-attempt results, not measured systems. Latency and tokens for them are not measured.
- **Mixed task contracts.** The two projects used different card-writing procedures (see Method). The results are not strictly comparable across projects.
- **Labels are model-generated.** Difficulty labels and task instructions came from an LLM agent, spot-checked but not fully reviewed. The "hard" label did not predict model outcomes cleanly.

## 5. Exit-criteria assessment

The roadmap's benchmark criterion asks for at least 40% fewer premium calls with at most a 5-point loss in success.

- **Cascade:** 28% fewer premium calls (13 vs 18), one more task solved (11 vs 10). The loss condition is met; the 40% call reduction is **not met**.
- **Rule router (easy to cheap, rest to premium):** 22% fewer calls (14 vs 18), same success (10 vs 10). The 40% reduction is **not met**.
- **Why savings are limited:** only 4 of 18 tasks are easy, and qwen's wins outside the easy tier were 2 medium tasks and 1 hard task, which only the cascade can exploit.

The criterion is not formally met, and at n = 18 with single attempts it cannot be tested precisely. The result is consistent with the thesis that cheap models handle some tasks and verification can catch the rest, and it gives no reason to stop. The honest status is "proceed, with the claim still to be proven at scale in the evaluation harness, and with a more realistic expectation that savings depend on how many tasks in the target workload are easy."

## 6. Implications for Phase 1 and beyond

- Log, per run: the model, the task text, the test verdict, token counts, `baseline_exit`, any provider errors or retries, and whether the oracle was borrowed or native, so later phases can compute escalation and failure rates and exclude environment errors automatically.
- Make the harness environment explicit and identical for oracle validation and every model run (required environment variables, database setup, dependency install), and fail loudly if a run's baseline does not match.
- Keep the provider interface generic for local, hosted and OpenAI-compatible models (the Phase 0 harness already does this), and add retry-with-backoff and a distinct "provider error" status so infrastructure failures are never read as model failures.
- Build the larger benchmark (target 30 or more tasks per project, including more easy tasks, with repeated attempts per task and written interface contracts), reusing the task-card pipeline and oracle-validation step.
- Test edit-style output formats (diffs, targeted patches) and a parse-failure retry, since whole-file rewrites and unparseable responses caused a large share of the 7B model's failures.
- Treat test-based verification as a first-class component, with build/lint/typecheck as fallbacks when no test exists.
