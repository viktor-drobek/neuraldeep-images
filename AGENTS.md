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
whisper-1) and must stay identical across them except for the `SERVICE = "..."` line. Port a
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
