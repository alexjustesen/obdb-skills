# obdb-skills

A collection of [Agent Skills](https://agentskills.io) used across the [Open Brewery DB](https://github.com/openbrewerydb/openbrewerydb) project. Each skill packages instructions (and any supporting scripts/reference docs) that an AI agent loads automatically when a task matches — this follows the open `SKILL.md` standard, so these work across any tool that implements it (Claude Code, claude.ai, the Claude API, and other compatible coding agents), not just one specific product.

## Structure

```
skills/
└── <skill-name>/
    ├── SKILL.md            # required — frontmatter (name, description) + instructions
    ├── references/         # optional — docs read only when needed
    └── scripts/            # optional — self-contained helpers
```

Skills live under `skills/` so compatible installers can discover them directly from the repository. The `SKILL.md` files use the portable Agent Skills standard and can also be copied or symlinked into a tool-specific skill directory.

## Skills in this repo

| Skill | What it does |
|---|---|
| [`openbrewerydb-contributor`](skills/openbrewerydb-contributor/SKILL.md) | Researches and submits an explicit add, update, close, reopen, relocate, or delete request for known brewery records. This is the only skill that normally edits source CSVs. |
| [`openbrewerydb-data-quality-auditor`](skills/openbrewerydb-data-quality-auditor/SKILL.md) | Audits source CSV structure, identities, completeness, coordinates, and operating status, then produces an issue-ready report without changing the dataset. |
| [`openbrewerydb-brewery-discovery`](skills/openbrewerydb-brewery-discovery/SKILL.md) | Compares a regional, guild, regulator, or licensed inventory against all source CSVs to identify coverage gaps and produce a review inventory. |
| [`openbrewerydb-entity-linker`](skills/openbrewerydb-entity-linker/SKILL.md) | Researches candidate Wikidata and OpenStreetMap links for existing records and reports confidence and conflicts without writing external IDs. |

## Skill routing

| Request | Skill |
|---|---|
| Change one or more known brewery records | `openbrewerydb-contributor` |
| Audit existing records or stale statuses | `openbrewerydb-data-quality-auditor` |
| Discover missing breweries or regional coverage gaps | `openbrewerydb-brewery-discovery` |
| Match existing records to Wikidata or OpenStreetMap | `openbrewerydb-entity-linker` |

The auditor, discovery, and entity-linker skills are read-only and return issue-ready Markdown by default. Confirmed and explicitly approved record changes can be handed to the contributor skill.

## Maintainer-only dataset scripts

Skills in this repository must never run any npm script in the upstream dataset repository, including undocumented or newly added scripts and aliases such as `npm test` or `npm start`. Do not run `npm install` there because package lifecycle hooks can execute npm scripts. These scripts are run only by the repository maintainer as part of the merge and publication workflow. Skills must not invoke their implementation files directly or through another package manager, reproduce their mutating behavior, delegate them to a subagent, or modify the generated root-level dataset artifacts they produce.

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

1. Scaffold it with `npx skills init <skill-name>`, move the resulting directory under `skills/` if needed, or create `skills/<skill-name>/SKILL.md` by hand:
   ```yaml
   ---
   name: <skill-name>
   description: What it does, and when an agent should reach for it — be specific here, since this description is the main thing an agent sees before deciding whether to use the skill.
   ---
   ```
2. Write the workflow as numbered steps. Keep `SKILL.md` itself under ~500 lines; move anything long or reference-y (API docs, CLI cheat sheets, schema notes) into `references/` and point to it from the relevant step.
3. Call out prerequisites and failure modes explicitly — what tools/env vars the skill needs, and what the agent should do (ask the user, degrade gracefully, or stop) when something's missing, ambiguous, or conflicting, rather than guessing.
4. Enforce the maintainer-only npm script rule above in every skill that operates on `openbrewerydb/openbrewerydb`; never use an upstream npm script for implementation or verification.
5. Test it against a few real prompts before committing, and add the entry to the table above.
6. Commit under `skills/<skill-name>/` and push. Anyone can then pull it with `npx skills add alexjustesen/obdb-skills --skill <skill-name>` — no separate publish step needed.
7. Stick to plain Markdown + the standard frontmatter fields where possible, rather than product-specific syntax — that's what keeps a skill portable across tools instead of tied to one.

## Requirements

Skills in this repo may assume certain CLIs are already installed and configured. Check each `SKILL.md`: the contributor expects `git`, authenticated `gh`, and the [Geocodio CLI](https://www.geocod.io/cli) with `GEOCODIO_API_KEY`; the auditor and discovery helpers require Python 3 and use only its standard library.
