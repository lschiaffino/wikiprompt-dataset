# Wikiprompt - the open catalog of AI prompts

[**wikiprompt.org**](https://www.wikiprompt.org) is a public, Wikipedia-style encyclopedia of **55,000+ curated AI prompts** for ChatGPT, Claude, Gemini, GPT Image, Midjourney, Seedance, Veo, Kling, Nano Banana, Grok and more - each with a title, description, category, tags, the model used, structured metadata, and (for image/video prompts) the actual generated result.

This repo is the **developer hub**: how to access the catalog programmatically for your own projects. It does **not** contain the website source - it contains the ways in.

> Building something with a giant repo of prompts? You can access ours. Three ways, below.

## TL;DR - three ways to access

| Way | Auth | Gets you | Best for |
|---|---|---|---|
| **Dataset** (`/dataset`) | none | Metadata for every prompt (title, description, category, tags, model, media, canonical URL) - paginated, cached | Discovery, indexing, analysis, building a browser/search |
| **API** (`/api/v1/prompts`) | free API key | The **full prompt text** (content) + metadata, paginated | Actually using the prompts in an app/agent |
| **MCP server** (`mcp.wikiprompt.org/mcp`) | none (read) / key (submit) | Live search + fetch as tools an AI agent can call | Claude / AI agents that pick prompts mid-conversation |

The **dataset is metadata-only and open to everyone**. To get the **prompt bodies themselves**, create a free account and use an **API key** (see [docs/api.md](docs/api.md)). That's the deal: the catalog is open, and signing up unlocks the full content.

---

## 1. Dataset (no key) - metadata for the whole catalog

One endpoint, self-describing. Page 1 returns the manifest (total, fields, license) plus the first page of records; follow `next` until it is `null`.

```bash
curl "https://www.wikiprompt.org/dataset?limit=500"
```

Each record: `slug`, `url` (canonical page - the full prompt lives here), `title`, `description`, `category`, `tags`, `media` (our own `wikiprompt.org/media` links), `model`, `metadata` (media_type, style, aspect ratio, quality assessment, keywords), `author`, `created_at`, `updated_at`.

The prompt **body** is not in the dataset (open the `url`, or use the API). See [docs/dataset.md](docs/dataset.md) and [examples/python/download_dataset.py](examples/python/download_dataset.py).

## 2. API (free key) - the full prompt text

1. Create an account at [wikiprompt.org](https://www.wikiprompt.org).
2. Generate an API key in your [profile](https://www.wikiprompt.org/profile).
3. Fetch prompts **with content**, paginated:

```bash
curl "https://www.wikiprompt.org/api/v1/prompts?page=1&limit=50" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

Params: `page`, `limit` (<=100), `category`, `mine=true` (only your own). You can also **submit** prompts (`POST /api/v1/prompts`). See [docs/api.md](docs/api.md) and [examples/python/fetch_prompts.py](examples/python/fetch_prompts.py).

## 3. MCP server - for AI agents

Connect an agent (e.g. Claude) to the live catalog:

```bash
claude mcp add --transport http wikiprompt https://mcp.wikiprompt.org/mcp
```

Tools: `search_prompts`, `get_prompt`, `list_categories`, `get_featured`, `get_trending`, `get_recent`, `random_prompt`, `get_stats`, `prompts_by_author`, `submit_prompt`, and more. See [docs/mcp.md](docs/mcp.md).

There's also a **Claude Skill** for using prompts: [docs/skill.md](docs/skill.md) (`https://skill.wikiprompt.org`).

---

## License & attribution

The Wikiprompt **compilation, curation, metadata, quality assessments and translations** are licensed **CC BY-SA 4.0** (c) wikiprompt.org - reuse freely with attribution and share-alike. See [LICENSE](LICENSE).

The **prompt bodies themselves** are aggregated from public posts by their **original authors**; wikiprompt.org does not claim ownership of them. When you reuse content, please **cite wikiprompt.org** (and, where shown, the original author).

## Links

- Site: https://www.wikiprompt.org
- Dataset (live, metadata): https://www.wikiprompt.org/dataset
- Hugging Face dataset (static snapshot): https://huggingface.co/datasets/lautaschiaffino/wikiprompt-prompts
- API docs (on-site): https://www.wikiprompt.org/api-docs
- MCP: https://mcp.wikiprompt.org/mcp
- Skill: https://skill.wikiprompt.org
- llms.txt: https://www.wikiprompt.org/llms.txt

Questions or building something cool with it? Open an issue.
