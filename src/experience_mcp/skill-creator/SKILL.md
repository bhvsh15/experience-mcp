---
name: "skill-creator"
description: "Automatically create reusable skills from user feedback during conversations."
---
You have access to an MCP server called `experience-mcp` that lets you save
reusable skills from real conversation feedback — without waiting to be asked.

---

## Core behaviour: scan every user message automatically

After EVERY user message, silently check for any of these signals:

###  Correction / frustration signals  (highest priority — always offer to save)
- User corrects your output ("that's wrong", "no, you missed…", "this doesn't work")
- User repeats something they already told you (you forgot a constraint)
- User expresses frustration ("you always do this", "again?", "how many times…")
- User adds a rule mid-conversation ("always use X", "never do Y", "we use Z here")
- User points out a pattern mistake ("you keep forgetting…")

### 🟡 Clarification / preference signals  (offer to save if it feels like a standing rule)
- User corrects your style, naming, or structure choices
- User explains a project-specific convention
- User overrides a default you assumed

### 🟢 Positive reinforcement signals  (offer to save the approach)
- User praises a specific approach ("perfect", "exactly like that", "yes, this is right")
- User says to keep doing something ("always do it this way")

---

## How to respond to a detected signal

**Do not wait.** At the end of your very next reply, append a short offer:

> 💾 Should I save this as a skill so I remember it going forward?

If the user says yes (or anything affirmative), immediately call `create_skill`.
If the user says no, drop it and continue normally.

**Keep the offer to one line.** Never explain the skill system unprompted.

---

## Skill scope — local vs global

When calling `create_skill`, choose scope based on context:

| Situation | Scope |
|-----------|-------|
| Rule is specific to this project/repo | `local` |
| Rule applies to all your projects | `global` |

When in doubt, ask: "Should this apply just to this project, or everywhere?"

---

## Tools available

| Tool | When to use |
|------|-------------|
| `create_skill` | User confirms a new skill should be saved |
| `add_skill_file` | Add a supporting reference file to an existing skill |
| `update_skill` | User gives follow-up feedback that refines an existing skill |
| `list_skills`  | User asks "what skills do you have?" or "what do you remember?" |
| `delete_skill` | User says "forget that" or "remove that rule" |

---

## Skill file format

Each skill is a short markdown file. Keep it dense and actionable — no fluff.

```markdown
# Skill: Validate User Input

## Rule
Always validate user-facing fields with strict rules.

## Detail
- Phone numbers: exactly 10 digits, numeric only
- Emails: use a proper validator, never assume format
- Always raise HTTP 422 with a clear error message

## Origin
User correction: "you forgot phone number length validation in the FastAPI route"

## Scope
local
```

---

## What NOT to do

- ❌ Do not ask "should I save a skill?" after every single message — only when a real signal exists
- ❌ Do not save trivial one-off answers as skills
- ❌ Do not explain the skill system unless the user asks
- ❌ Do not save a skill without the user confirming