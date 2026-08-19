# Git & PR workflow

Assumes `gh` (GitHub CLI) is installed and authenticated, and the repo has a writable remote (the canonical repository or a fork). Check `git remote -v` rather than assuming `origin` points to the canonical repository. These should already have been confirmed at step 0 of `SKILL.md`; if they were not, go back and check first.

The npm commands in the upstream repository's [`Scripts` section](https://github.com/openbrewerydb/openbrewerydb#%EF%B8%8F-scripts) are owner-only publication tools. Never run them, invoke their implementation files directly, reproduce their mutating behavior, or include their generated output in a contributor commit. This includes `npm run validate`, `npm run csv:combine`, and every generation, contributor, and maintenance command listed there. See the mandatory owner-only scripts rule in `SKILL.md`.

## 1. Branch

Create one branch per session/request from the latest `master` of the canonical `openbrewerydb/openbrewerydb` repository. Determine which remote tracks the canonical repository and use it below as `<upstream-remote>`.

Every branch name must use `<epoch-seconds>-<github-username>`. Get the Unix epoch timestamp at branch creation time and the GitHub username from the authenticated `gh` account; do not substitute a descriptive name, date string, display name, or email address.

```bash
git checkout master
git pull <upstream-remote> master
GITHUB_USERNAME="$(gh api user --jq .login)"
EPOCH_TIMESTAMP="$(date +%s)"
BRANCH_NAME="${EPOCH_TIMESTAMP}-${GITHUB_USERNAME}"
git checkout -b "$BRANCH_NAME"
```

For example, an epoch timestamp of `1787145600` and GitHub username `alexjustesen` produce `1787145600-alexjustesen`. Keep `BRANCH_NAME` unchanged for the entire workflow.

## 2. One commit per change

A change is exactly one record addition, one record deletion, or one update to one record. Every change gets its own commit so it can be reverted independently. If the same record needs two independently requested updates, keep those changes separate as well. Never put changes to multiple records in one commit.

Edit, review, stage, and commit one change before editing the next. Do not accumulate changes, especially when multiple records share a source CSV, because staging the file would combine them. Inspect the staged diff and proceed only when it contains exactly one change:

```bash
git add <path-to-csv>
git diff --cached
git commit -m "Add <Brewery Name> to <state_or_country>.csv"
```

or for updates:

```bash
git add <path-to-csv>
git diff --cached
git commit -m "Update <Brewery Name>: <what changed, e.g. phone, website>"
```

or for deletions:

```bash
git add <path-to-csv>
git diff --cached
git commit -m "Remove <Brewery Name> from <state_or_country>.csv"
```

Keep messages specific about what changed, not just "update csv."

Commit only the appropriate per-region source CSV. Do not edit or regenerate root-level `breweries.csv`, `breweries.json`, `breweries.sql`, IDs, statistics, or contributor files; the repository owner handles those publication artifacts after merge.

Before pushing, compare the branch with canonical `master` and confirm that the commit count equals the number of additions, deletions, and updates. If a commit contains more than one change, split it before opening the PR.

## 3. Push and open the PR against the canonical repository

Push the branch to a writable remote, then explicitly target `openbrewerydb/openbrewerydb:master`. Do not rely on `gh` inferring the base repository from the current remote.

```bash
git push -u <writable-remote> "$BRANCH_NAME"
gh pr create \
  --repo openbrewerydb/openbrewerydb \
  --base master \
  --head "<head-owner>:${BRANCH_NAME}" \
  --title "<short summary>" \
  --body-file <pr-body-file>
```

The PR body must start with these exact paragraphs, preserving their wording and blank lines:

> This pull request includes changes to the OpenBreweryDB dataset. Each change is it's own commit and a full log of changes can be found below. Review all the changes to ensure the best data quality
>
> If you need help or have any questions, join our Discord: https://discord.gg/3G3syaD

Below those paragraphs, add a `## Change log` section with one entry per commit in commit order. Each entry must include the short commit SHA, action (`Add`, `Delete`, or `Update`), brewery name, and a one-line summary. End the body by stating that owner-only publication scripts were intentionally not run and generated artifacts were intentionally not changed.

After creation, verify the PR URL is under `openbrewerydb/openbrewerydb` and its base branch is `master`:

```bash
gh pr view <pr-url> --repo openbrewerydb/openbrewerydb --json url,baseRefName,commits
```

## 4. Add one sourced diff comment per change

Add one separate PR comment for every change/commit, in the same order as the commits. Use this Markdown structure:

```markdown
## <Add|Delete|Update>: <Brewery Name>

**Commit:** `<short-sha>`
**Source file:** `<path-to-source-csv>`

| Field | Old value | New value |
|---|---|---|
| `<field>` | `<old value or (none)>` | `<new value or (none)>` |

### Sources

- <source URL and what it verifies>

### Notes

<Sourcing notes, conflict resolution, geocoding details, and reason for the change.>
```

For additions, include every field and use `(none)` for old values. For deletions, include every field and use `(none)` for new values. For updates, include only changed fields. Use actual source URLs, not generic source names, and explain any conflicting data or unavailable coordinates.

Post each prepared comment with:

```bash
gh pr comment <pr-url> --repo openbrewerydb/openbrewerydb --body-file <change-comment-file>
```

Finally, inspect the PR comments and confirm there is exactly one sourced table comment for every change commit. Do not consider the workflow complete until all comments are present.

Always open a PR — never push directly to `master`, even for trivial one-field updates.
