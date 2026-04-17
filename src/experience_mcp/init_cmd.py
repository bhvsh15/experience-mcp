"""
Handles: experience-mcp init <agent> [--local|--global]

1. Copies bundled skill-creator/ into the project's skills dir
2. Injects the MCP server entry into the agent's global config file,
   pinning PROJECT_DIR to the directory where `init` was run —
   i.e. the user's actual project root, not the package install location.
"""

import sys
import json
import shutil
from pathlib import Path
from .config import AGENTS

# The bundled skill-creator ships inside the package so it survives pip install.
# __file__ = src/experience_mcp/init_cmd.py  →  bundled dir is a sibling.
BUNDLED_SKILL_CREATOR = Path(__file__).parent / "skill-creator"


def run_init(agent: str, scope: str = "local") -> None:
    agent = agent.lower().strip()
    scope = scope.lower().strip() if scope else "local"

    if agent not in AGENTS:
        supported = ", ".join(AGENTS.keys())
        print(f"[experience-mcp] ERROR: Unknown agent '{agent}'. Supported: {supported}")
        sys.exit(1)

    agent_cfg = AGENTS[agent]

    # CWD at CLI time = the user's project root (they cd'd here before running init)
    project_dir = Path.cwd()
    skills_dir  = agent_cfg["skills_dir"](project_dir)
    mcp_config  = agent_cfg["mcp_config"]

    print(f"[experience-mcp] Initialising for '{agent}' (scope: {scope})")
    print(f"  Project : {project_dir}")
    print()

    # ── Step 1: Copy skill-creator into the project ───────────────────────────
    skill_creator_dst = skills_dir / "skill-creator"

    if skill_creator_dst.exists():
        print(f"  ✓ skill-creator already at {skill_creator_dst} — skipping.")
    else:
        if not BUNDLED_SKILL_CREATOR.exists():
            print(
                f"[experience-mcp] ERROR: Bundled skill-creator not found at "
                f"{BUNDLED_SKILL_CREATOR}.\n"
                "  Try re-installing:  pip install --force-reinstall experience-mcp"
            )
            sys.exit(1)

        shutil.copytree(BUNDLED_SKILL_CREATOR, skill_creator_dst)
        print(f"  ✓ skill-creator  →  {skill_creator_dst}")

    # ── Step 2: Inject / update MCP server config ─────────────────────────────
    mcp_config.parent.mkdir(parents=True, exist_ok=True)

    if mcp_config.exists():
        try:
            existing = json.loads(mcp_config.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}
    else:
        existing = {}

    existing.setdefault("mcpServers", {})
    server_key = "experience-mcp"

    new_entry = {
        # sys.executable = the python that has experience-mcp installed.
        # -m experience_mcp resolves correctly regardless of venv/path.
        "command": sys.executable,
        "args":    ["-m", "experience_mcp"],
        "env": {
            "AGENT_NAME":         agent,
            "AGENT_SKILLS_SCOPE": scope,
            "PROJECT_DIR":        str(project_dir),   # ← the key fix
        },
    }

    if server_key in existing["mcpServers"]:
        old_env     = existing["mcpServers"][server_key].get("env", {})
        old_project = old_env.get("PROJECT_DIR", "")
        old_scope   = old_env.get("AGENT_SKILLS_SCOPE", "")

        if old_project != str(project_dir) or old_scope != scope:
            existing["mcpServers"][server_key] = new_entry
            mcp_config.write_text(json.dumps(existing, indent=2), encoding="utf-8")
            print(f"  ✓ Updated MCP config  →  {mcp_config}")
        else:
            print(f"  ✓ MCP config already up to date — skipping.")
    else:
        existing["mcpServers"][server_key] = new_entry
        mcp_config.write_text(json.dumps(existing, indent=2), encoding="utf-8")
        print(f"  ✓ MCP config written  →  {mcp_config}")

    # ── Done ──────────────────────────────────────────────────────────────────
    print()
    print("─" * 52)
    print(f"  Done! Restart {agent} to activate experience-mcp.")
    print("─" * 52)
    print()
    print(f"  Skills : {skills_dir}")
    print(f"  Config : {mcp_config}")
    print(f"  Scope  : {scope}")
    print()
    if scope == "local":
        print("  Tip: use --global to share skills across all your projects.")
    else:
        print("  Tip: use --local to make skills specific to this project.")