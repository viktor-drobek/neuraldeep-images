# Agent guide for neuraldeep-images

Instructions for AI coding agents (Codex, Coddy, Claude Code and others) working **inside this
repository**. To *use* the skill, read [SKILL.md](SKILL.md) and [STARTER_RELAY.md](STARTER_RELAY.md).

## What lives here

- `SKILL.md`: the skill manifest and API reference that the agent loads at run time.
- `STARTER_RELAY.md`: the spending guard, private job state, recovery, and the Relay envelope.
- `scripts/client.py`: the only code, a standard-library CLI with `check`, `run` and `resume`.
- `tests/`: offline unit tests (`test_client.py`) and documentation checks (`test_examples.py`).
- `TESTING.md`: the record of test-first changes and the current test count.

## The shared helper

`scripts/client.py` is shared by every neuraldeep-* repo (images, search, ocr, speechcore,
transcriptions) and must stay identical across them except for the `SERVICE = "..."` line. Port a
change to every sibling repo, each through its own PR. Check a port against a sibling checkout:

```bash
diff <(grep -v '^SERVICE = ' scripts/client.py) <(grep -v '^SERVICE = ' ../neuraldeep-search/scripts/client.py)
```

It must print nothing. Treat other repos' checkouts as read-only unless you were asked to work there.

## Tests

Tests are offline: HTTP is mocked and no billed endpoint is called. Run them with credentials
blanked so a real key can never be read:

```bash
env -u NEURALDEEP_API_KEY CODDY_HOME=/nonexistent python3 -B -m unittest discover -s tests
```

Before opening a PR, also run the suite under a non-UTF-8 locale and with encoding warnings on:

```bash
env -u NEURALDEEP_API_KEY CODDY_HOME=/nonexistent LC_ALL=C PYTHONUTF8=0 python3 -B -m unittest discover -s tests
```

```bash
env -u NEURALDEEP_API_KEY CODDY_HOME=/nonexistent python3 -X warn_default_encoding -B -m unittest discover -s tests
```

- Work test-first: add the regression test, watch it fail, then fix. Say so in the commit.
- Update the count in TESTING.md "Final results" and add a short note for each change.
- Pass `encoding="utf-8"` to every text read and write, in code and tests.
- CI (`.github/workflows/tests.yml`) runs the suite and `--help` on Python 3.10 and the latest 3.x.

## Safety rules

- Never run `run` or `resume` against the live API while developing or testing; they spend quota.
  `check` is read-only, but run it only when the user asks.
- Never add, print, or commit credentials, state files, inputs or result artifacts.
- Keep the guard fail-closed: unknown schemas, premium operations, unverified quotas and
  ambiguous submissions must block. Never add POST retries, redirects, or a fallback that resubmits.
- Errors must stay sanitized (no keys, no provider response bodies), and every failure must still
  print the JSON envelope.

## Delivery workflow

Work RED-GREEN-REFACTOR: start a feature with a test that describes the observable result and a
bug fix with a regression test, watch it fail for the intended reason, make the smallest change
that passes, and refactor only with the suite green. Then run the full offline matrix above.

Inside `scripts/client.py`, implement from lower dependencies upward: constants and parsing,
credentials and approved-origin transport, the fail-closed guard, durable state and artifacts,
provider jobs and polling, then `execute()` and the CLI. Lower layers must not depend on CLI
parsing or provider job state.

Update `README.md`, `SKILL.md`, `STARTER_RELAY.md` and `TESTING.md` in the same change when
behavior, CLI output, safety assumptions or documented shapes change.

## Rules Sync

This file is the common policy for every agent, and `CLAUDE.md` is a symlink to it. Scoped detail
lives in native rules with identical bodies:

| Rule | Scope | Cursor | Claude Code |
|---|---|---|---|
| `workflow` | always on | `.cursor/rules/workflow.mdc` | `.claude/rules/workflow.md` |
| `client` | `scripts/**/*.py`, `tests/test_client.py` | `.cursor/rules/client.mdc` | `.claude/rules/client.md` |
| `documentation` | `README.md`, `SKILL.md`, `STARTER_RELAY.md`, `TESTING.md`, `tests/test_examples.py` | `.cursor/rules/documentation.mdc` | `.claude/rules/documentation.md` |

- Cursor reads `.cursor/rules/`; Claude Code reads `CLAUDE.md` and `.claude/rules/`.
- Codex reads this file, and the project hook in `.codex/hooks.json` with
  `.codex/hooks/attach_rules.py` attaches the Cursor rules: always-on rules at session start,
  scoped rules before an edit to a matching file. Run `/hooks` in Codex once per clone and again
  after changing either hook file. The hook is a fail-open convenience, not a security boundary;
  the safety rules here, the helper and the tests still enforce them.
- Never copy rule bodies under `.codex` or create `.codex/rules.md`.
- Change a rule and its counterpart together. `tests/test_agent_rules.py` checks the pairing, the
  scopes and the hook; it and `.codex/hooks/` are identical across the neuraldeep-* repositories.

## Releases

A release is a `vX.Y.Z` tag on `main` with a GitHub release. `metadata.version` in the `SKILL.md`
frontmatter is the version Coddy shows and uses to decide whether an installed copy is older, so
it must equal the tag without the `v`:

1. In a PR, bump `metadata.version` (semantic versioning) and note the change in `TESTING.md`.
2. After the PR is merged and CI is green, tag the merge commit and publish the release, for
   example `gh release create v1.0.0 --target main --title v1.0.0 --notes-file NOTES.md`.
3. CI runs on the tag push; `tests/test_release.py` fails the build if the tag and
   `metadata.version` differ. It is identical across the neuraldeep-* repositories.

## Git and PRs

- Work on a branch and open a PR; do not push to `main`. Merging is the repository owner's call.
- Do not add AI attribution to commits or PRs: no `Co-Authored-By` trailer for an AI model and no
  "Generated with" line.
- Do not rewrite or force-push shared history without the owner's explicit approval.

## Codex

- Codex reads this file automatically. Its default sandbox blocks network access and writes
  outside the workspace, which is all the offline tests need.
- A live `check` needs the network and reads the key from `~/.coddy`, outside the workspace. Ask
  the user before requesting broader sandbox access; never widen it to spend quota.

## Coddy

- The skill reads the key from `${CODDY_HOME:-~/.coddy}/providers/neuraldeep/neuraldeep-auth.json`
  (field `api_key`), then falls back to `NEURALDEEP_API_KEY`. Sign in with
  `coddy providers login neuraldeep`; never ask the user to paste a key into the chat.
- Run skill commands from the skill directory, and keep state files and results in a private
  directory outside the checkout.
