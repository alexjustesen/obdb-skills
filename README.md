# obdb-skills

A collection of [Agent Skills](https://agentskills.io) used across the [Open Brewery DB](https://github.com/openbrewerydb/openbrewerydb) project. Each skill packages instructions (and any supporting scripts/reference docs) that an AI agent loads automatically when a task matches — this follows the open `SKILL.md` standard, so these work across any tool that implements it (Claude Code, claude.ai, the Claude API, and other compatible coding agents), not just one specific product.

## Structure

```
.claude/skills/
└── <skill-name>/
    ├── SKILL.md            # required — frontmatter (name, description) + instructions
    └── references/         # optional — docs read only when needed
```

Skills live under `.claude/skills/` so they're versioned with the rest of the repo. That path is what Claude Code watches by convention, but the `SKILL.md` files themselves are plain-standard and portable — other agent tools that support the same standard can point at this directory (or the same folder copied/symlinked wherever that tool expects skills) without any changes to the files.

## Skills in this repo

| Skill | What it does |
|---|---|
| [`openbrewerydb-contributor`](.claude/skills/openbrewerydb-contributor/SKILL.md) | Adds, deletes, or updates brewery/cidery/brewpub/bottleshop records in the [openbrewerydb/openbrewerydb](https://github.com/openbrewerydb/openbrewerydb) dataset, creates one commit per change, and opens a PR with sourced old/new comparison tables. |

## Owner-only dataset scripts

Skills in this repository must never run any command listed in the upstream dataset repository's [`Scripts` section](https://github.com/openbrewerydb/openbrewerydb#%EF%B8%8F-scripts). Those scripts are run only by the repository owner when publishing a dataset. Skills must not invoke their implementation files indirectly, reproduce their mutating behavior, delegate them to a subagent, or modify the generated root-level dataset artifacts they produce.

## Installing a skill

The recommended way to pull a skill from this repo into an agent's config is the [`skills` CLI](https://www.npmjs.com/package/skills) (`npx skills`), which works across Claude Code, Cursor, Codex, OpenCode, and other compatible tools — it detects which agents you have installed and drops the skill into the right directory for each:

```bash
# Install a specific skill from this repo
npx skills add alexjustesen/obdb-skills --skill openbrewerydb-contributor

# Install to a specific agent only
npx skills add alexjustesen/obdb-skills --skill openbrewerydb-contributor -a claude-code

# Install every skill in this repo, non-interactively
npx skills add alexjustesen/obdb-skills --all -y

# List what's in this repo before installing
npx skills add alexjustesen/obdb-skills --list
```

By default it installs at project scope (committed alongside your other project files); add `-g` for a global, cross-project install instead.

If a tool you're using doesn't support the `skills` CLI yet, you can always place the skill folder manually:
- **Claude Code**: copy into `.claude/skills/<skill-name>/` (project) or `~/.claude/skills/<skill-name>/` (personal, global).
- **claude.ai**: zip the individual skill folder and upload it under Settings → Features.
- **Claude API**: reference via the Skills API (`/v1/skills`) if you want it available to API-driven workflows.

## Adding a new skill

1. Scaffold it: `npx skills init <skill-name>` (creates `.claude/skills/<skill-name>/SKILL.md` with the right frontmatter shape), or `mkdir -p .claude/skills/<skill-name>` and write `SKILL.md` by hand:
   ```yaml
   ---
   name: <skill-name>
   description: What it does, and when an agent should reach for it — be specific here, since this description is the main thing an agent sees before deciding whether to use the skill.
   ---
   ```
2. Write the workflow as numbered steps. Keep `SKILL.md` itself under ~500 lines; move anything long or reference-y (API docs, CLI cheat sheets, schema notes) into `references/` and point to it from the relevant step.
3. Call out prerequisites and failure modes explicitly — what tools/env vars the skill needs, and what the agent should do (ask the user, degrade gracefully, or stop) when something's missing, ambiguous, or conflicting, rather than guessing.
4. Enforce the owner-only dataset script rule above in every skill that operates on `openbrewerydb/openbrewerydb`; never use an upstream publication script for implementation or verification.
5. Test it against a few real prompts before committing, and add the entry to the table above.
6. Commit under `.claude/skills/<skill-name>/` and push. Anyone can then pull it with `npx skills add alexjustesen/obdb-skills --skill <skill-name>` — no separate publish step needed.
7. Stick to plain Markdown + the standard frontmatter fields where possible, rather than product-specific syntax — that's what keeps a skill portable across tools instead of tied to one.

## Requirements

Skills in this repo may assume certain CLIs are already installed and configured on whatever machine runs them, regardless of which agent tool is executing the skill — check each skill's `SKILL.md` for specifics (e.g. `openbrewerydb-contributor` expects `git`, `gh` (authenticated), and the [Geocodio CLI](https://www.geocod.io/cli) with `GEOCODIO_API_KEY` set).
