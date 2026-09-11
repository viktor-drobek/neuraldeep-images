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

- A NeuralDeep API key (`sk-...`). The skill reads it from
  `~/.coddy/providers/neuraldeep/neuraldeep-auth.json` (field `api_key`), or
  falls back to the `NEURALDEEP_API_KEY` environment variable.
- Get a key at <https://neuraldeep.ru> (Hub) or via `coddy providers login neuraldeep`.

## Usage

See [`SKILL.md`](./SKILL.md) for the full API reference, endpoints, request/response
shapes, and worked examples.

## License

[MIT](./LICENSE)
