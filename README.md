# experience-mcp

Give your coding agent a long-term memory. Every time your agent (Claude Code, Cursor, Copilot, etc.) makes a mistake or you teach it something new, `experience-mcp` saves that as a reusable **skill** — so it never forgets again.

---

## Install

```bash
pip install experience-mcp
```

Or directly from GitHub:

```bash
pip install git+https://github.com/bhvsh15/experience-mcp.git
```

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

### MCP tools exposed to the agent

| Tool | Purpose |
|------|---------|
| `create_skill` | Save a new skill |
| `add_skill_file` | Add a supporting file to an existing skill |
| `update_skill` | Refine an existing skill |
| `list_skills` | Show all saved skills |
| `delete_skill` | Remove a skill |

---

## Skill format

Each skill is a folder with a `SKILL.md` file:

```
.claude/skills/
└── validate-user-input/
    └── SKILL.md
```

```markdown
# Skill: Validate User Input

## Rule
Always validate user-facing fields with strict rules.

## Detail
- Phone numbers: exactly 10 digits, numeric only
- Emails: use a proper validator, never assume format
- Always raise HTTP 422 with a clear error message

## Origin
User correction: "you forgot phone number length validation"

## Scope
local
```

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