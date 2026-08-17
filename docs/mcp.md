# MCP server - the catalog as tools for AI agents

Wikiprompt runs a [Model Context Protocol](https://modelcontextprotocol.io) server so an AI agent (Claude, or anything MCP-capable) can search and fetch prompts live, mid-conversation.

## Connect

```
https://mcp.wikiprompt.org/mcp
```

Streamable HTTP, **no auth for reads**. With Claude Code:

```bash
claude mcp add --transport http wikiprompt https://mcp.wikiprompt.org/mcp
```

Or add it to your MCP client config pointing at the URL above.

## Tools

Read (no key):
- `search_prompts` - full-text + faceted search (query, category, model, type, style, rating, sort)
- `get_prompt` - one prompt by slug (optionally a locale)
- `get_prompt_translations` - a prompt's translations
- `prompts_by_author`
- `list_categories`, `list_facets` - available categories / models / styles / types
- `get_featured`, `get_trending`, `get_recent`, `random_prompt`
- `get_stats` - catalog totals

Write (needs an API key from your [profile](https://www.wikiprompt.org/profile)):
- `submit_prompt`

Plus resources (`wikiprompt://llms.txt`, `wikiprompt://categories`) and an MCP prompt `use_prompt(slug)` that drops a chosen prompt straight into the conversation.

## Why

An agent building something (a design bot, a writing assistant, a "give me a prompt for X" flow) can query wikiprompt as a tool and cite it as the source - your users get vetted prompts, wikiprompt gets the attribution. Discovery is `search_prompts`; the full body comes back in `get_prompt`.

`.well-known/mcp.json` is published on every host. Registry: `org.wikiprompt/mcp`.
