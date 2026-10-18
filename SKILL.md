---
name: neuraldeep-images
description: >
  Image generation and processing skill powered by NeuralDeep Image API.
  Supports FLUX image generation, 4× upscale, background removal, enhancement,
  and avatar creation. Work asynchronously: submit → poll → download.
  Automatically activates when user asks for image generation, AI art,
  photo processing, or visual asset creation.
metadata:
  version: 1.0.0
  neuraldeep:
    emoji: "🖼️"
    base_url: "https://api.neuraldeep.ru/v1/images"
    endpoints:
      - /v1/images/generate
      - /v1/images/tasks/{uid}
      - /v1/images/tasks/{uid}/result
      - /v1/images/upscale
      - /v1/images/background/remove
      - /v1/images/enhance
      - /v1/images/avatar
---

> **Author:** these skills were authored by the **kimi2.6** and **qwen3.8 27b** models, and are published by **viktor-drobek**.

# NeuralDeep Image API

Use this skill whenever the user needs:
- Generating images from text prompts (FLUX)
- Upscaling existing images 4×
- Removing backgrounds
- Enhancing photos
- Creating avatars from portraits

## Requirements

Python 3.10+ is sufficient; the helper uses only the standard library.
Run commands from this skill's directory. No `curl`, `jq`, or `httpx` is required.

The helper first reads `api_key` from
`${CODDY_HOME:-~/.coddy}/providers/neuraldeep/neuraldeep-auth.json`, then falls
back to `NEURALDEEP_API_KEY` for missing, malformed, null, or empty file values.
It never prints the key. If neither source works, it returns `blocked`; use
`coddy providers login neuraldeep` or supply the environment variable securely.
Do not use `jq -r .api_key` as a presence check: JSON null becomes the string `null`.

Read [Starter and Relay safety](STARTER_RELAY.md) before submitting work.
Every billed operation must pass the helper's live subscription, public-price,
and service-quota checks. A chat `decision.can_request=false` is not a service
quota decision. State files and artifacts are private runtime data, not repo files.

## Base URL

```
https://api.neuraldeep.ru/v1/images
```

---

## 1. Image Generation (FLUX)

### Submit, poll, and save
```bash
printf '%s\n' '{"prompt":"an astronaut cat in neon","options":{"aspect_ratio":"1:1"}}' > request.json
python3 scripts/client.py run generate --payload request.json --state image-state.json --output out.png
```

**Params:**
- `prompt` (string, required) — generation prompt. FLUX understands **English only**.
  - Russian prompts are **auto-translated RU→EN**.
  - Set `translate: false` to disable auto-translation.
- `options.aspect_ratio` (string, optional) — one of:
  - `1:1` (default) · `9:16` · `16:9` · `4:5` · `3:2` · `5:3` · `3:5`
- `width`, `height`, and `size` are unsupported; use `options.aspect_ratio`.

**Response:**
```json
{"task_uid": "<uuid>"}
```

### Poll status
```bash
# Resume the same provider job only after a timeout or transient polling error.
python3 scripts/client.py resume --state image-state.json --output out.png --timeout 300
```

**Response:**
```text
{"task_uid": "...", "status": "pending | processing | finished | failed", ...}
```

**Polling interval:** every 2 seconds, for up to 120 seconds by default; pass
`--timeout SECONDS` to wait longer. GPU queue may occasionally stall.

### Download result
`run` and `resume` download `GET /v1/images/tasks/{uid}/result` only after
`status=finished`. On failure or timeout they leave no new result artifact.

Returns the PNG image as raw binary.

---

## 2. Upscale ×4

```bash
python3 scripts/client.py run upscale --file photo.jpg --state upscale-state.json --output photo-upscaled.png
```

Submit as **multipart/form-data** with `image=@<filename>`.

---

## 3. Background Removal

```bash
python3 scripts/client.py run background/remove --file portrait.png --state background-state.json --output transparent.png
```

---

## 4. Image Enhancement

```bash
python3 scripts/client.py run enhance --file photo.jpg --state enhance-state.json --output enhanced.png
```

All processing examples use the documented multipart `image` field. Each POST returns a task ID, not image bytes; the helper polls and then downloads the binary result.

---

## 5. Avatar Generation

```bash
python3 scripts/client.py run avatar --file selfie.jpg --state avatar-state.json --output avatar.png
```

---

## 6. Quota Check

```bash
python3 scripts/client.py check generate
```

Verified quota structure: top-level `tier`, with `img.day.remaining` and
`img.month.remaining`. Both windows must cover one operation.

---

## Complete Python Example: Generate + Poll + Save

```python
import json
from pathlib import Path
import subprocess
Path("request.json").write_text(json.dumps({"prompt": "an astronaut cat in neon",
                                         "options": {"aspect_ratio": "1:1"}}))
subprocess.run(["python3", "scripts/client.py", "run", "generate", "--payload", "request.json",
                "--state", "python-image-state.json", "--output", "out.png"], check=True)
# out.png exists as a new artifact only after successful polling and download.
```

---

## Cost & Limits

- Counted in **operations** (1 operation = 1 API call).
- Available on **all tariffs** (free, starter, pro).
- Quota endpoint returns remaining ops.
- Status + result downloads do **not** consume quota.

## Error Handling

- `401` — invalid key
- `429` — quota exhausted or rate limited. The helper does not retry or wait for
  `Retry-After`; on submission it reports `reconciliation_required` like any other
  HTTP failure. A new submission is a separate decision after a fresh quota check.
- `500`/`503` — stop; reconcile an uncertain submission instead of retrying it
- Generation queue may stall: keep a timeout when polling.

## Privacy & Security

- Do not upload personal or sensitive images without user consent.
- Prompts leave the local machine; avoid including private data.
- Generated images are stored temporarily; download promptly.
