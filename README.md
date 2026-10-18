# 🖼️ neuraldeep-images

Image generation and processing: FLUX generation, 4× upscale, background removal, enhancement, and avatar creation (async submit → poll → download).

A [Coddy](https://coddy.dev) / AI-agent skill for the **NeuralDeep Image API**.

## Author

These skills were authored by the **kimi2.6** and **qwen3.8 27b** models, and are published by **viktor-drobek**.

## Install

```bash
# via the skillsbd catalog
npx skillsbd add viktor-drobek/neuraldeep-images/neuraldeep-images

# or directly from this repo
npx skillsbd add https://github.com/viktor-drobek/neuraldeep-images --skill neuraldeep-images
```

## Requirements

- A NeuralDeep API key (`sk-...`) in this skill's own variable `NEURALDEEP_IMAGES_API_KEY` (several
  keys may be separated by commas), or the shared `NEURALDEEP_API_KEY`, set in the
  environment or in `${CODDY_HOME:-~/.coddy}/.env`:

  ```bash
  echo 'NEURALDEEP_IMAGES_API_KEY=sk-...' >> ~/.coddy/.env
  ```
- Python 3.10+ (standard library only).
- Get a key at <https://neuraldeep.ru> (Hub).

## Usage

See [`SKILL.md`](./SKILL.md) for the full API reference, endpoints, request/response
shapes, and worked examples.

## Starter guard and Relay handoff

See [STARTER_RELAY.md](./STARTER_RELAY.md) for guarded commands, private job
state, timeout recovery, and the optional artifact-based Relay envelope.
The helper checks live service quota rather than hard-coding daily limits.

Run offline tests: `python3 -B -m unittest discover -s tests`.

AI coding agents (Codex, Coddy and others) working on this repository should read
[AGENTS.md](./AGENTS.md) first.

## License

[MIT](./LICENSE)
