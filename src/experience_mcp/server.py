"""
experience-mcp — MCP server entry point.

Runs as MCP server (called by agent, no args):
  python -m experience_mcp

One-time project setup (CLI):
  experience-mcp init <agent> --local
  experience-mcp init <agent> --global
"""

import sys
from mcp.server.fastmcp import FastMCP
from .config import get_config
from .tools import make_tools


def create_server() -> FastMCP:
    config     = get_config()
    agent      = config["agent"]
    scope      = config["scope"]
    skills_dir = config["skills_dir"]

    skills_dir.mkdir(parents=True, exist_ok=True)

    print(
        f"[experience-mcp] Running — agent={agent}, scope={scope}, skills={skills_dir}",
        file=sys.stderr,
    )

    mcp = FastMCP("experience-mcp", instructions=SERVER_INSTRUCTIONS)

    tools = make_tools(skills_dir=skills_dir, agent=agent, scope=scope)
    for tool in tools:
        mcp.tool()(tool)

    return mcp


SERVER_INSTRUCTIONS = """\
experience-mcp gives you a long-term memory across conversations. Saved skills
(markdown files in the project's skills folder) capture rules, preferences, and
conventions the user has taught you — re-read them on future sessions.

PROACTIVE USE — do not wait to be asked:

Call `create_skill` whenever the user:
  • corrects you ("that's wrong", "no, you missed...", "don't do X")
  • repeats a constraint you forgot
  • states a standing rule ("always use X", "never Y", "we do Z here")
  • praises a specific approach ("perfect, keep doing that")

Flow on a detected signal:
  1. End your current reply with: "💾 Save this as a skill?"
  2. On user confirmation, immediately call `create_skill`.
  3. If the rule extends something already saved, call `update_skill` instead.

Call `list_skills` at the start of a session, or whenever you are unsure
whether the user has a standing rule about the current task. Treat listed
skills as authoritative memory, not optional suggestions.

IMPORTANT — do NOT use the built-in memory/file system for user preferences
or rules. Do not write markdown files directly, do not update MEMORY.md.
For anything the user teaches you (preferences, rules, corrections), the ONLY
correct mechanism is `create_skill`. The built-in memory system is for
session context only — skills are for durable, reusable knowledge.

SKILL.md FORMAT — every file you create must follow this exactly:

---
name: "kebab-case-skill-name"
description: "Use this skill whenever [specific triggers]. [What it enforces]."
---

## Rule
[Core rule in 1-2 sentences]

## Detail
- [Specific guideline]
- [Specific guideline]

## Origin
[How the rule was learned — e.g. "User correction: 'you always forget X'"]

## Scope
[local or global]

Rules for the frontmatter:
  • name: kebab-case, lowercase letters/digits/hyphens only, max 64 chars
  • description: assertive trigger language ("Use this skill whenever…"),
    max 1024 chars, no angle brackets — this is what the agent reads to
    decide when to auto-invoke the skill, so be specific about triggers
  • The frontmatter is required — without it the skill won't be auto-loaded
"""


def cli():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        _print_help()
        sys.exit(0)

    command = args[0]

    if command == "init":
        _cmd_init(args[1:])

    elif command == "serve":
        # explicit serve — same as headless but lets you test it manually
        create_server().run(transport="stdio")

    else:
        print(f"[experience-mcp] Unknown command '{command}'.")
        _print_help()
        sys.exit(1)


def _cmd_init(args: list[str]) -> None:
    # Parse: experience-mcp init <agent> [--local|--global]
    agent_args = [a for a in args if not a.startswith("--")]
    flag_args  = [a for a in args if a.startswith("--")]

    if not agent_args:
        print("[experience-mcp] ERROR: Missing agent name.")
        print("Usage: experience-mcp init <agent> [--local|--global]")
        print("Supported agents: antigravity, claude, cursor, copilot, codegpt")
        sys.exit(1)

    agent = agent_args[0]

    if "--global" in flag_args:
        scope = "global"
    else:
        scope = "local"  # --local is the default

    from .init_cmd import run_init
    run_init(agent, scope=scope)


def _print_help():
    print("""
experience-mcp — give your coding agent a long-term memory via MCP skills

Usage:
  experience-mcp init <agent> [--local|--global]

  --local   Save skills inside this project only  (default)
              e.g. .claude/skills/, .cursor/skills/
  --global  Save skills globally across all projects
              e.g. ~/.agent-skills/<agent>/

Supported agents:
  claude, cursor, copilot, codegpt, antigravity

Examples:
  cd ~/my-fastapi-project
  experience-mcp init claude --local
  experience-mcp init cursor --global
""".strip())


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli()
    else:
        create_server().run(transport="stdio")