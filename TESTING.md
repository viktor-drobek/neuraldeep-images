# Test-first verification

No billed endpoint was called during development or verification. Publication is separate from these test results.

## Red/green sequence

1. Added `tests/test_client.py` before `scripts/client.py` existed. Running
   `python3 -B -m unittest discover -s tests` failed with a missing-helper
   `FileNotFoundError` in each of the four service repositories.
2. Implemented the helper. The original nine safety tests passed in each repo.
3. Added six regression/workflow tests. The shared suite exposed two failures:
   result download could start after a just-expired polling deadline, and a
   preflight HTTP error was mislabeled `poll_error` instead of `blocked`.
4. Fixed both branches. Added the fenced-example syntax test before creating
   `STARTER_RELAY.md`; it failed because that required guide did not exist.
5. Created the guide and reran the full suite. Final results are reported below
   only after execution; no live submission/result is claimed by offline tests.

## Coverage

- Credential file and environment fallback, null/empty/missing values, CODDY_HOME.
- Starter subscription/status guard, exact non-premium operation, malformed and
  insufficient service quota, independent chat decision, double-page OCR pro cost.
- HTTP failures and ambiguous submissions with no retry or secret disclosure.
- Durable provider ID before polling; duplicate state creation refused.
- Failed statuses and deadline exhaustion never fetch results; unknown statuses keep polling.
- SHA-256 artifact provenance and untrusted-data labeling.
- Python and Bash fenced examples parsed without execution.

Official documentation and documented read-only quota endpoints were inspected;
only schema structure and public operation classification informed the fixtures.
SpeechCore remaining quota is unverified, so upload remains blocked. No end-to-end
paid test was performed. Artifact formats and submission contracts follow provider
documentation; the tests exercise mocked responses, not a claim of live success.

A further regression test exposed a CLI catch-all that hid sanitized block
reasons; it was fixed. A mocked workflow test covers all five image operations
as asynchronous jobs, including multipart processing rather than direct PNG POSTs.

## Unknown polling status

A live run on 2026-10-17 (four agents, real API) found that every OCR `run extract`
ended `failed` with "returned an unknown status", although the job had finished:
a later `GET /v1/ocr/jobs/{id}` said `completed`, and `resume` fetched the text.
`poll()` treated any status outside its fixed in-progress list as a failure.

Six tests were added first and failed: an unknown intermediate status now keeps
polling, an unknown status until the deadline ends `timed_out` naming it (only a
plain word is echoed), explicit failure statuses still stop at once, a response
without a status is a resumable `poll_error`, and a mocked OCR run passes through
an unknown status to `completed`. Mutations of the failure set, the status check
and the sanitising each fail their own test. **47 tests passed**, both normally
and with `LC_ALL=C PYTHONUTF8=0`, with no EncodingWarnings.

## Transcription models

The shared helper now knows three speech-to-text models for the `whisper`
service: `gigaam-v3` (the default), `whisper-1` and `whisper-podlodka-turbo`,
chosen with `--model`. Each has its own public price ID; the guard checks the
chosen model's row and its block names the model. `--model` is refused for the
other services and for unknown models (exit 2). Five shared tests were added
first; four failed and the fifth guards the new flag. Moving the default from
`whisper-1` to `gigaam-v3` updated the tests pinned to it. Mutations of the
default, the model check and the per-model price ID each fail their own test.
A live read-only `check` (2026-10-17) blocked each model at the quota step, so
all three price rows are present and non-premium. **52 tests passed**, both
normally and with `LC_ALL=C PYTHONUTF8=0`.

## Final results

- `python3 -B -m unittest discover -s tests`: **41 tests passed** in this repo
  (22 original plus 19 added below). The original 22-test shared suite passed in
  all four service repos (88 total); the notes below say what was ported since.
- `python3 -B scripts/client.py --help`: passed, with no network call.
- `git diff --check`: passed.
- Fenced Python examples parsed with `ast.parse`; Bash examples passed `bash -n`.
- Live **read-only** CLI preflights returned `ready` for Search, OCR, and Images.
  SpeechCore exited nonzero with `blocked` and the unverified-quota reason.
  No account values were saved in this repository and no provider job was created.

Additional test-first fixes ensured early failures carry the full handoff fields
and interrupted HTTP response bodies become sanitized request errors rather than
uncaught exceptions. Both regressions were observed failing before their fixes.

Independent review found that an async error body could be saved as a completed
artifact. Added failing regressions, then validated PNG MIME/signature and JSON
MIME/result fields before artifact creation. Invalid or empty results now preserve
the provider ID with `poll_error` and no success artifact. PNG signature checks
are not a full image-decoding or visual-quality audit. Generated bytecode caches
are excluded by `.gitignore`. The full 88-test regression passed after these fixes.

## Safety-path additions and CI

Eight tests were added for paths the original suite did not exercise directly:
the HTTPS host allowlist (scheme, look-alike host, port, userinfo), the bearer key
being omitted from the public prices request, redirects refused by the real
`NoRedirect` handler, `timed_out` through `execute` followed by `resume` from the
saved state with no second POST or preflight, refusal to resume non-resumable or
other-service state (state file left unchanged), the multipart body layout without
the local filename, image submission routing, and SKILL.md polling defaults
matching the helper. A 429 with `Retry-After` was added to the no-retry test.

Each new test was checked by temporarily breaking the guarded behavior in
`scripts/client.py` (following redirects, allowing any host, widening resumable
states, sending the local filename, mislabeling timeouts, changing the poll
interval); the matching test failed every time, and the helper was restored.

A ninth regression test showed that the local file extension was copied into
the multipart `filename` header, so a name containing quotes, `;` or line breaks
could inject header text. It failed before the fix; the helper now keeps only a
short alphanumeric extension and otherwise sends `filename="upload"`. This fix
still needs porting to the other three service repos.

A tenth regression test, ported from neuraldeep-search (cbb6fc3), showed that
`request()` left an `HTTPError` response open until garbage collection. It
failed before the fix; the error is now closed before `RequestError` is raised,
and the suite runs without `ResourceWarning`.

An eleventh test, `test_submission_reads_service_specific_job_id_field`, came
with the per-service job ID mapping ported from neuraldeep-speechcore (400a92d):
each service's job ID field is read, and a field belonging to another service
is rejected.

`.github/workflows/tests.yml` runs the unit suite and `--help` on Python 3.10 and
the latest 3.x, with credentials blanked so no billed endpoint can be reached.

Ported from neuraldeep-ocr: a reused `--state` path now blocks with "State
file already exists" instead of the generic CLI message, makes no HTTP call,
and leaves the existing file untouched. The updated duplicate-state test and the
new `test_existing_state_path_is_refused_with_clear_reason` failed first; the
suite is now **34 tests**.

Ported from neuraldeep-ocr: polling defaults now come from `POLL_INTERVAL = 2`
and `DEFAULT_TIMEOUT = 120` (used by `poll()` and `--timeout`, which gained help
text). `test_polling_defaults_come_from_shared_constants` failed first.
`scripts/client.py` is now identical across all four repos except `SERVICE`;
the suite is now **35 tests**.

## UTF-8 file reads

Added `test_text_files_are_read_as_utf8_on_non_utf8_locales` first. It runs the
helper in a C locale, whose default text encoding is ASCII, and failed: an auth
file with a non-ASCII field was reported as having no credential, and a UTF-8
`--payload` or state file raised `UnicodeDecodeError`. The helper and tests now
read and write text as UTF-8 explicitly. **36 tests passed**, both normally and
with `LC_ALL=C PYTHONUTF8=0`, with no `EncodingWarning` under
`-X warn_default_encoding`.

## Synchronous resume guard

Ported from neuraldeep-search (ac7260d) to keep `scripts/client.py` identical
across repos apart from `SERVICE`. For Search, `resume` of a hand-edited state
(status `submitted`, `timed_out` or `poll_error`) crashed with an uncaught
`UnboundLocalError`; a `SYNCHRONOUS` service set now blocks it up front. Images
never runs as Search, so this was not a live crash here.
`test_resume_of_edited_resumable_state_is_blocked_not_crashed` patches `SERVICE`
and failed first for all three statuses. **37 tests passed**, both normally and
with `LC_ALL=C PYTHONUTF8=0`, with no `EncodingWarning` under
`-X warn_default_encoding`.

## whisper-1 service blocked

Ported from neuraldeep-whisper-1 (36d8bc4) so `scripts/client.py` stays identical
across repos apart from `SERVICE`: the helper now knows a synchronous `whisper`
service (operation `transcribe`, public price ID `whisper-1`). whisper-1 is billed
per minute and has no verified remaining-quota endpoint, so `guard()` and
`submission()` block it like SpeechCore uploads. Images behaviour is unchanged.
`test_whisper_is_blocked_without_verified_quota` failed first. **38 tests
passed**, both normally and with `LC_ALL=C PYTHONUTF8=0`, with no
`EncodingWarning` under `-X warn_default_encoding`.

## Agent guide

Added `AGENTS.md`, the guide for coding agents (Codex, Coddy and others) working
in this repo. `test_fenced_examples_parse_without_execution` now also checks its
fenced examples; it failed first because the file did not exist. The test count
is unchanged at **38**.

## Malformed resume state and whisper coverage

Ported from neuraldeep-speechcore (a9a8073) via neuraldeep-whisper-1 (eda8436):
`resume` of a hand-edited or corrupted state (not an object, or with a
non-string `status` or non-list `errors`) now blocks with "State is not
resumable" instead of crashing. `test_resume_of_malformed_state_is_blocked_not_crashed`
failed first in all five subtests with `TypeError`, `AttributeError` or
`JobError`. Two whisper tests close a coverage gap: removing `"whisper"` from
`SYNCHRONOUS` fails `test_whisper_is_synchronous_and_refuses_resume`, and
removing the `submission()` whisper block fails
`test_whisper_run_is_blocked_before_any_request`. **41 tests passed**, both
normally and with `LC_ALL=C PYTHONUTF8=0`, with no `EncodingWarning` under
`-X warn_default_encoding`.

## Agent rule surfaces

Added `tests/test_agent_rules.py` (10 tests) before any rule file existed; all
10 failed because `.codex/hooks/attach_rules.py`, the rules and `CLAUDE.md` were
missing. Then added Cursor rules (`.cursor/rules/*.mdc`), their Claude Code
mirrors with identical bodies (`.claude/rules/*.md`), the Codex hook that attaches
the Cursor rules (`.codex/hooks.json`, `.codex/hooks/attach_rules.py`),
`CLAUDE.md` as a symlink to `AGENTS.md`, and the Delivery workflow and Rules Sync
sections in `AGENTS.md`. The tests check the pairing and scope mapping, that
every glob matches a file, and the hook itself: always-on rules at session start,
the client rule once per session for patch add, update, delete and rename and for
`Edit` and `Write`, and fail-open on bad input. Eight mutations (a widened or
narrowed scope, `paths` differing from `globs`, body drift, a missing mirror, a
dead glob, `.codex/rules.md`, a copied `CLAUDE.md`) each failed a test. The test
file and `.codex/hooks/` are identical across the neuraldeep-* repositories.
With the five transcription-model tests merged in parallel,
**62 tests passed**, both normally and with `LC_ALL=C PYTHONUTF8=0`, with no
`EncodingWarning` under `-X warn_default_encoding`.
