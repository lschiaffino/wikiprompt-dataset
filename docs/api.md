# The API (`/api/v1`) - full prompt text, with a free key

The dataset gives you metadata. To get the **actual prompt bodies** programmatically, create a free account and use an API key.

## Get a key (once)

1. Sign up at [wikiprompt.org](https://www.wikiprompt.org).
2. Go to your [profile](https://www.wikiprompt.org/profile) and generate an API key.
3. Send it as `Authorization: Bearer <key>`.

## List prompts (with content)

```
GET https://www.wikiprompt.org/api/v1/prompts
```

```bash
curl "https://www.wikiprompt.org/api/v1/prompts?page=1&limit=50" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

Query params:
- `page` (default 1), `limit` (default 50, max 100)
- `category` - filter (creative, marketing, personal, productivity, coding, education, business, research, other)
- `mine=true` - only prompts you created

Response:

```jsonc
{
  "success": true,
  "page": 1, "limit": 50, "total": 55945, "count": 50,
  "next_page": 2,
  "prompts": [
    {
      "id": "...", "slug": "...", "url": "https://www.wikiprompt.org/...",
      "title": "...", "description": "...",
      "content": "...the full prompt text...",     // <- the part the dataset doesn't have
      "category": "creative", "tags": [...],
      "media_urls": [...], "metadata": {...},
      "created_at": "...", "updated_at": "...",
      "likes_count": 0, "views_count": 0
    }
  ],
  "attribution": "wikiprompt.org - ..."
}
```

Paginate by following `next_page` until it is `null`.

## Submit a prompt

```bash
curl -X POST "https://www.wikiprompt.org/api/v1/prompts" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"title":"...","content":"...","description":"...","category":"creative","tags":["a","b"],"media_urls":[]}'
```

Returns the created prompt (with its slug/url). Rate-limited (HTTP 429 + `Retry-After` when exceeded).

See [examples/python/fetch_prompts.py](../examples/python/fetch_prompts.py). On-site docs: [wikiprompt.org/api-docs](https://www.wikiprompt.org/api-docs).

## Attribution

Prompt bodies belong to their original authors; the compilation/metadata is CC BY-SA 4.0 (c) wikiprompt.org. Cite wikiprompt.org when reusing. See [LICENSE](../LICENSE).
