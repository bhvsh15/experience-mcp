"""
Resolves agent config paths from env vars.

Env vars:
  AGENT_NAME           — required, e.g. "claude", "cursor"
  AGENT_SKILLS_SCOPE   — "local" (default) or "global"
  PROJECT_DIR          — absolute path to the user's project root.
                         Defaults to CWD if not set, but should always
                         be set explicitly in the agent's MCP config so
                         skills land in the right project, not the
                         mcp-experience repo itself.
"""

import os
import sys
from pathlib import Path

AGENTS = {
    "antigravity": {
        "skills_dir":  lambda base: base / ".agents" / "skills",
        "mcp_config":  Path.home() / ".gemini" / "antigravity" / "mcp_config.json",
    },
    "claude": {
        "skills_dir":  lambda base: base / ".claude" / "skills",
        "mcp_config":  Path.home() / ".claude" / "mcp.json",
    },
    "cursor": {
        "skills_dir":  lambda base: base / ".cursor" / "skills",
        "mcp_config":  Path.home() / ".cursor" / "mcp.json",
    },
    "copilot": {
        "skills_dir":  lambda base: base / ".copilot" / "skills",
        "mcp_config":  Path.home() / ".copilot" / "mcp-config.json",
    },
    "codegpt": {
        "skills_dir":  lambda base: base / ".codegpt" / "skills",
        "mcp_config":  Path.home() / ".codegpt" / "mcp_config.json",
    },
}

# Global fallback — agent-agnostic, lives in the user's home dir
GLOBAL_SKILLS_DIR = Path.home() / ".agent-skills"


def get_config() -> dict:
    agent = os.environ.get("AGENT_NAME", "").lower().strip()
    scope = os.environ.get("AGENT_SKILLS_SCOPE", "local").lower().strip()

    # PROJECT_DIR must be set by the agent's MCP config to the actual project
    # root. We do NOT fall back to CWD because CWD at MCP server startup is
    # the mcp-experience repo, not the user's project.
    project_dir_env = os.environ.get("PROJECT_DIR", "").strip()
    if project_dir_env:
        project_dir = Path(project_dir_env).expanduser().resolve()
    else:
        # Hard fallback: warn loudly, use CWD (likely wrong in production)
        project_dir = Path.cwd()
        print(
            "[experience-mcp] WARNING: PROJECT_DIR env var is not set. "
            f"Falling back to CWD ({project_dir}). "
            "Set PROJECT_DIR in your agent's MCP config to fix this.",
            file=sys.stderr,
        )

    if not agent:
        print(
            "[experience-mcp] ERROR: AGENT_NAME env var is not set.",
            file=sys.stderr,
        )
        sys.exit(1)

    if agent not in AGENTS:
        supported = ", ".join(AGENTS.keys())
        print(
            f"[experience-mcp] ERROR: Unknown agent '{agent}'. Supported: {supported}",
            file=sys.stderr,
        )
        sys.exit(1)

    agent_cfg = AGENTS[agent]

    if scope == "global":
        skills_dir = GLOBAL_SKILLS_DIR / agent
    else:
        # local — relative to the user's actual project, not the MCP repo
        skills_dir = agent_cfg["skills_dir"](project_dir)

    return {
        "agent":      agent,
        "scope":      scope,
        "skills_dir": skills_dir,
        "mcp_config": agent_cfg["mcp_config"],
        "project_dir": project_dir,
    }