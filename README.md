# experience-mcp

Give your coding agent a long-term memory. Every time your agent (Claude Code, Cursor, Copilot, etc.) makes a mistake or you teach it something new, `experience-mcp` saves that as a reusable **skill** — so it never forgets again.

---

## Install

```bash
pip install git+https://github.com/bhvsh15/experience-mcp.git
```

> Once published to PyPI: `pip install experience-mcp`

---

## Setup (one time per project)

`cd` into your project, then run:

```bash
# Skills saved inside this project only (.claude/skills/, .cursor/skills/, etc.)
experience-mcp init claude --local

# Skills saved globally, shared across all your projects
experience-mcp init claude --global
```

Then **restart your agent**. That's it.

> `init` registers the MCP server in your agent's global config and copies the `skill-creator` skill into your project — no manual config needed.

---

## Supported agents

| Agent | Skills folder (local) | Global config |
|-------|----------------------|---------------|
| `claude` | `.claude/skills/` | `~/.claude/mcp.json` |
| `cursor` | `.cursor/skills/` | `~/.cursor/mcp.json` |
| `copilot` | `.copilot/skills/` | `~/.copilot/mcp-config.json` |
| `codegpt` | `.codegpt/skills/` | `~/.codegpt/mcp_config.json` |
| `antigravity` | `.agents/skills/` | `~/.gemini/antigravity/mcp_config.json` |

---

## How it works

After init, your agent gets a `skill-creator` skill injected into its skills folder. This teaches the agent to:

- **Auto-detect feedback** — corrections, frustration, praise, new rules — from the natural flow of conversation
- **Offer to save** with a one-line prompt: `💾 Should I save this as a skill?`
- **Save skills** as markdown files in your project (local) or home dir (global)
- **Apply skills automatically** — on the next session, the agent reads saved skills and follows their rules without being reminded

### MCP tools exposed to the agent

| Tool | Purpose |
|------|---------|
| `create_skill` | Save a new skill |
| `add_skill_file` | Add a supporting file to an existing skill |
| `update_skill` | Refine an existing skill |
| `list_skills` | Show all saved skills |
| `delete_skill` | Remove a skill |

---

## Example

Here's a real workflow. The agent writes a FastAPI query the wrong way. You correct it once — and it never happens again.

**1. You ask the agent to add a filter:**
> *"add a category filter to the /posts endpoint"*

The agent adds the parameter but filters rows in Python after fetching everything from the database.

**2. You correct it:**
> *"don't fetch everything and filter in Python — always push filters to the database using `.where()`. That's the rule for all queries in this project."*

The agent fixes the code, then offers:
> *"💾 Should I save this as a skill?"*

**3. You say yes.** The agent calls `create_skill` and saves:

```
.cursor/skills/
└── push-query-filters-to-database/
    └── SKILL.md
```

```markdown
---
name: "push-query-filters-to-database"
description: "Use this skill whenever writing or reviewing data-access queries
in this project. Enforce database-side filtering and aggregation instead of
Python-side post-processing."
---

## Rule
Always push filtering, counting, and selection constraints into SQL queries.
Do not fetch broad result sets and filter/count them in Python.

## Detail
- Apply query filters with `.where(...)` on the SQL query before execution
- Use DB-side aggregates like `func.count()` instead of `len(...all())` patterns
- Keep pagination and filtering combined in one query path when possible
- Treat Python-side filtering of fetched rows as a bug unless explicitly required

## Origin
User rule: "don't fetch everything and filter in Python — always push filters
to the database using .where(). That's the rule for all queries in this project."

## Scope
local
```

**4. Next session** — the agent reads the skill automatically and applies the rule before you say anything.

---

## Skill format

Each skill is a folder with a `SKILL.md` file:

```
.claude/skills/
└── push-query-filters-to-database/
    └── SKILL.md
```

Every `SKILL.md` starts with YAML frontmatter:

```markdown
---
name: "kebab-case-skill-name"
description: "Use this skill whenever [triggers]. [What it enforces]."
---

## Rule
[Core rule in 1-2 sentences]

## Detail
- [Specific guideline]

## Origin
[How the rule was learned]

## Scope
local
```

The `description` field is what the agent reads to decide when to auto-invoke the skill — make it specific about triggers.

---

## CLI reference

```
experience-mcp init <agent> [--local|--global]

  --local    Save skills inside this project (default)
  --global   Save skills globally (~/.agent-skills/<agent>/)

experience-mcp --help
```

---

## License

MIT
