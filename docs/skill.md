# Claude Skill - use Wikiprompt prompts from Claude

Wikiprompt publishes a [Claude Skill](https://www.anthropic.com/news/skills) so Claude can find and apply prompts from the catalog for you.

## Install / reference

- Landing + install: **https://skill.wikiprompt.org**
- Raw skill: **https://skill.wikiprompt.org/SKILL.md**

The skill teaches Claude to search wikiprompt (via the MCP server / API), pick a relevant prompt, and use it - e.g. "give me a good cinematic portrait prompt and run it", "find a Wikiprompt template for product photography".

## Under the hood

The skill leans on the same public surfaces documented here:
- the [MCP server](mcp.md) for live search/fetch, and
- the [dataset](dataset.md) / [API](api.md) for bulk or content access.

So anything the skill does, you can do directly from your own agent or app.
