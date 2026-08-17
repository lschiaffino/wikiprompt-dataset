# The Dataset (`/dataset`) - metadata, no key

The full public catalog as a single, self-describing, edge-cached JSON endpoint. **Metadata only** - the prompt body is not here (open the record's `url`, or use the [API](api.md) for content).

## Endpoint

```
GET https://www.wikiprompt.org/dataset
```

- **Page 1** (no cursor) returns the manifest (`total_prompts`, `record_fields`, `license`, `pagination`) **plus** the first page of records.
- Follow the `next` URL in each response (it stays on `/dataset`) until it is `null`.
- Keyset pagination: `?after=<cursor>&limit=<n>` (limit up to 500, default 200).
- CORS enabled, heavily cached (`s-maxage=3600`). No auth.

## Record shape

```jsonc
{
  "slug": "cinematic-portrait-...",
  "url": "https://www.wikiprompt.org/cinematic-portrait-...", // canonical page; full prompt text lives here
  "title": "...",
  "description": "...",
  "category": "creative",
  "tags": ["portrait", "cinematic", "..."],
  "media": ["https://www.wikiprompt.org/media/tw/....jpg"],   // our own media links
  "model": "GPT Image 2",
  "metadata": { "media_type": "image", "style": [...], "aspect_ratio": "...", "assessment": {...}, "keywords": [...] },
  "author": { "username": "twitter:...", "name": "..." },
  "created_at": "...",
  "updated_at": "..."
}
```

## Example

```bash
# first page (manifest + records)
curl "https://www.wikiprompt.org/dataset?limit=500"
# next page
curl "https://www.wikiprompt.org/dataset?after=<next_cursor>&limit=500"
```

See [examples/python/download_dataset.py](../examples/python/download_dataset.py) for a full pagination loop that dumps every record to a local file.

## When to use which

- **Dataset** (this): discovery, search indexes, analysis, "which models/styles/topics exist", building a browsing UI. Metadata for all ~55k in a few hundred cached requests.
- **[API](api.md)** (key): when you need the actual prompt text to run.
