---
author: kimi2.6 & qwen3.8 27b (published by viktor-drobek)
name: neuraldeep-images
description: >
  Image generation and processing skill powered by NeuralDeep Image API.
  Supports FLUX image generation, 4× upscale, background removal, enhancement,
  and avatar creation. Work asynchronously: submit → poll → download.
  Automatically activates when user asks for image generation, AI art,
  photo processing, or visual asset creation.
metadata:
  neuraldeep:
    emoji: "🖼️"
    requires_file: "~/.coddy/providers/neuraldeep/neuraldeep-auth.json"
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

### Primary key source
```bash
~/.coddy/providers/neuraldeep/neuraldeep-auth.json
```
Extract: `jq -r '.api_key' ~/.coddy/providers/neuraldeep/neuraldeep-auth.json`

### Fallback
```bash
${NEURALDEEP_API_KEY}
```

### Resolve key helper
```bash
ND_KEY=$(jq -r '.api_key' ~/.coddy/providers/neuraldeep/neuraldeep-auth.json 2>/dev/null)
[ -z "$ND_KEY" ] && ND_KEY="${NEURALDEEP_API_KEY}"
```
If empty → return `BLOCKED` + suggest `coddy providers login neuraldeep`.

## Base URL

```
https://api.neuraldeep.ru/v1/images
```

---

## 1. Image Generation (FLUX)

### Submit task
```bash
ND_KEY=$(jq -r '.api_key' ~/.coddy/providers/neuraldeep/neuraldeep-auth.json 2>/dev/null || echo "${NEURALDEEP_API_KEY}")
ND_TASK=$(curl -sS https://api.neuraldeep.ru/v1/images/generate \
  -H "Authorization: Bearer ${ND_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"кот-космонавт, неон","options":{"aspect_ratio":"1:1"}}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['task_uid'])")
```

**Params:**
- `prompt` (string, required) — generation prompt. FLUX understands **English only**.
  - Russian prompts are **auto-translated RU→EN**.
  - Set `translate: false` to disable auto-translation.
- `options.aspect_ratio` (string, optional) — one of:
  - `1:1` (default) · `9:16` · `16:9` · `4:5` · `3:2` · `5:3` · `3:5`
- `options` may also contain `style`, `negative_prompt` depending on model support.

**Response:**
```json
{"task_uid": "<uuid>"}
```

### Poll status
```bash
curl -sS "https://api.neuraldeep.ru/v1/images/tasks/${ND_TASK}" \
  -H "Authorization: Bearer ${ND_KEY}"
```

**Response:**
```json
{"task_uid": "...", "status": "pending | processing | finished | failed", ...}
```

**Polling interval:** every 1 second up to 120 seconds. GPU queue may occasionally stall.

### Download result
```bash
curl -sS "https://api.neuraldeep.ru/v1/images/tasks/${ND_TASK}/result" \
  -H "Authorization: Bearer ${ND_KEY}" \
  -o out.png
```

Returns the PNG image as raw binary.

---

## 2. Upscale ×4

```bash
ND_KEY=$(jq -r '.api_key' ~/.coddy/providers/neuraldeep/neuraldeep-auth.json 2>/dev/null || echo "${NEURALDEEP_API_KEY}")
curl -sS https://api.neuraldeep.ru/v1/images/upscale \
  -H "Authorization: Bearer ${ND_KEY}" \
  -F "image=@photo.jpg" \
  -o photo_upscaled.png
```

Submit as **multipart/form-data** with `image=@<filename>`.

---

## 3. Background Removal

```bash
curl -sS https://api.neuraldeep.ru/v1/images/background/remove \
  -H "Authorization: Bearer ${ND_KEY}" \
  -F "image=@portrait.png" \
  -o transparent.png
```

---

## 4. Image Enhancement

```bash
curl -sS https://api.neuraldeep.ru/v1/images/enhance \
  -H "Authorization: Bearer ${ND_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/photo.jpg"}' \
  -o enhanced.png
```

Also supports multipart: `-F "image=@photo.jpg"`.

---

## 5. Avatar Generation

```bash
curl -sS https://api.neuraldeep.ru/v1/images/avatar \
  -H "Authorization: Bearer ${ND_KEY}" \
  -F "image=@selfie.jpg" \
  -o avatar.png
```

---

## 6. Quota Check

```bash
curl -sS "https://api.neuraldeep.ru/v1/images/quota" \
  -H "Authorization: Bearer ${ND_KEY}"
```

---

## Complete Python Example: Generate + Poll + Save

```python
import time, httpx, json, os

BASE = "https://api.neuraldeep.ru/v1"
KEY = json.load(open(os.path.expanduser(
    "~/.coddy/providers/neuraldeep/neuraldeep-auth.json"
)))["api_key"]
H = {"Authorization": f"Bearer {KEY}"}

# 1. Submit generation job
job = httpx.post(
    f"{BASE}/images/generate",
    headers=H,
    json={"prompt": "кот-космонавт в стиле киберпанк", "options": {"aspect_ratio": "1:1"}},
).json()
uid = job["task_uid"]

# 2. Poll (max 120s)
for _ in range(120):
    st = httpx.get(f"{BASE}/images/tasks/{uid}", headers=H).json()
    if st["status"] == "finished":
        break
    if st["status"] == "failed":
        raise RuntimeError("Image generation failed")
    time.sleep(1)

# 3. Download PNG
img = httpx.get(f"{BASE}/images/tasks/{uid}/result", headers=H).content
open("out.png", "wb").write(img)
```

---

## Cost & Limits

- Counted in **operations** (1 operation = 1 API call).
- Available on **all tariffs** (free, starter, pro).
- Quota endpoint returns remaining ops.
- Status + result downloads do **not** consume quota.

## Error Handling

- `401` — invalid key
- `429` — quota exhausted → `Retry-After`
- `500`/`503` — GPU queue is full → retry after a delay
- Generation queue may stall: keep a timeout when polling.

## Privacy & Security

- Do not upload personal or sensitive images without user consent.
- Prompts leave the local machine; avoid including private data.
- Generated images are stored temporarily; download promptly.
