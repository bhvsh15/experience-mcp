"""
MCP tool implementations for mcp-experience.
Each skill is a folder under <project>/<agent-dir>/skills/<skill-name>/
with SKILL.md as the main entry point.

`scope` is passed in from config ("local" or "global") and surfaced in
list_skills output and the SKILL.md template so the agent knows what
it's working with.
"""

import re
import shutil
from pathlib import Path
from datetime import datetime, timezone


def _slug(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def make_tools(skills_dir: Path, agent: str, scope: str = "local"):

    def create_skill(
        name: str,
        content: str,
        supporting_files: dict = None,
    ) -> dict:
        """
        Save a new reusable skill the user has just taught you.

        CALL THIS PROACTIVELY — do not wait to be asked. Trigger it whenever
        the user corrects you, states a standing rule ("always X", "never Y",
        "we do Z here"), or praises a specific approach worth repeating.

        Before calling, end your prior reply with "💾 Save this as a skill?"
        and call on user confirmation. If the rule refines something already
        saved, call `update_skill` instead to avoid duplicates — check with
        `list_skills` if unsure.

        The `content` MUST start with YAML frontmatter:

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
            [local or global]

        Frontmatter rules:
          - name: kebab-case, max 64 chars, lowercase/digits/hyphens only
          - description: assertive trigger language, max 1024 chars, no angle brackets
          - Without frontmatter the skill won't be auto-loaded by the agent

        Args:
            name:             Short kebab-case folder name, e.g. "validate-user-input"
            content:          Full SKILL.md content including frontmatter (see above)
            supporting_files: Optional {filename: content} for extra .md files,
                              e.g. {"examples.md": "# Examples\\n..."}
        """
        folder = skills_dir / _slug(name)

        if folder.exists():
            return {
                "success": False,
                "error": f"Skill '{name}' already exists. Use update_skill to modify it.",
            }

        folder.mkdir(parents=True, exist_ok=True)

        skill_md = folder / "SKILL.md"
        skill_md.write_text(content, encoding="utf-8")

        written = ["SKILL.md"]
        if supporting_files:
            for filename, file_content in supporting_files.items():
                if not filename.endswith(".md"):
                    filename = filename + ".md"
                (folder / filename).write_text(file_content, encoding="utf-8")
                written.append(filename)

        return {
            "success": True,
            "message": f"Skill '{name}' created ({scope}).",
            "folder":  str(folder),
            "files":   written,
            "agent":   agent,
            "scope":   scope,
        }

    def add_skill_file(name: str, filename: str, content: str) -> dict:
        """
        Attach a supporting reference file (examples, edge cases, longer
        context) to an existing skill folder. Use this when a skill needs
        more detail than fits cleanly in SKILL.md.

        Args:
            name:     Existing skill folder name
            filename: New file name, e.g. "examples.md"
            content:  Markdown content for the file
        """
        folder = skills_dir / _slug(name)

        if not folder.exists():
            return {
                "success": False,
                "error": f"Skill '{name}' not found. Create it first with create_skill.",
            }

        if not filename.endswith(".md"):
            filename = filename + ".md"

        filepath = folder / filename

        if filepath.exists():
            return {
                "success": False,
                "error": f"File '{filename}' already exists in skill '{name}'. Use update_skill to modify it.",
            }

        filepath.write_text(content, encoding="utf-8")

        return {
            "success":  True,
            "message":  f"File '{filename}' added to skill '{name}'.",
            "filepath": str(filepath),
        }

    def update_skill(name: str, filename: str, content: str) -> dict:
        """
        Refine an existing skill when the user gives follow-up feedback that
        extends or corrects a rule you already saved. PREFER THIS OVER
        `create_skill` when a related skill already exists — don't create
        duplicates. Check `list_skills` first if unsure.

        Args:
            name:     Existing skill folder name
            filename: File to update, e.g. "SKILL.md" or "examples.md"
            content:  New full markdown content (replaces the file)
        """
        folder = skills_dir / _slug(name)

        if not folder.exists():
            return {
                "success": False,
                "error": f"Skill '{name}' not found.",
            }

        if not filename.endswith(".md"):
            filename = filename + ".md"

        filepath = folder / filename
        filepath.write_text(content, encoding="utf-8")

        return {
            "success":  True,
            "message":  f"'{filename}' updated in skill '{name}'.",
            "filepath": str(filepath),
        }

    def list_skills() -> dict:
        """
        List all saved skills for this project/scope. CALL THIS at the start
        of a session, or whenever you are unsure whether the user already has
        a standing rule about the current task. Treat returned skills as
        authoritative memory — read them before acting.
        """
        if not skills_dir.exists():
            return {
                "agent":  agent,
                "scope":  scope,
                "skills": [],
                "count":  0,
                "note":   "Skills folder not found. Run `mcp-experience init` first.",
            }

        folders = sorted([f for f in skills_dir.iterdir() if f.is_dir()])
        skills  = []

        for folder in folders:
            files    = sorted([f.name for f in folder.glob("*.md")])
            skill_md = folder / "SKILL.md"
            preview  = ""

            if skill_md.exists():
                for line in skill_md.read_text(encoding="utf-8").splitlines():
                    line = line.strip().lstrip("#").strip()
                    if line:
                        preview = line
                        break

            skills.append({
                "name":    folder.name,
                "files":   files,
                "preview": preview,
            })

        return {
            "agent":       agent,
            "scope":       scope,
            "skills_path": str(skills_dir),
            "skills":      skills,
            "count":       len(skills),
        }

    def delete_skill(name: str) -> dict:
        """
        Permanently delete a skill folder and all its files. Call this only
        when the user explicitly says "forget that", "remove that rule", or
        similar. Never delete on your own judgment.

        Args:
            name: Skill folder name to delete
        """
        folder = skills_dir / _slug(name)

        if not folder.exists():
            return {
                "success": False,
                "error":   f"Skill '{name}' not found.",
            }

        shutil.rmtree(folder)

        return {
            "success": True,
            "message": f"Skill '{name}' deleted.",
            "scope":   scope,
        }

    return create_skill, add_skill_file, update_skill, list_skills, delete_skill