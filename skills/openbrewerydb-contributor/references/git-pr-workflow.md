# Git & PR workflow

Assumes `gh` is authenticated and the repo has a writable remote for the authenticated account. Check `git remote -v`, `gh api user --jq .login`, and remote ownership rather than assuming `origin` is canonical or writable. Confirm this at step 0 before research.

All npm scripts in the upstream dataset repository are maintainer-only tools, including undocumented or newly added scripts and aliases such as `npm test` or `npm start`. Never run them, invoke their implementation files directly or through another package manager, reproduce their mutating behavior, delegate them, or include their generated output in a contributor commit. Do not run `npm install` in the dataset repository because package lifecycle hooks can execute npm scripts. The maintainer runs these scripts only as part of the merge and publication workflow. See the mandatory maintainer-only npm scripts rule in `SKILL.md`.

## 1. Branch

Create one branch per session/request from the latest `master` of the canonical `openbrewerydb/openbrewerydb` repository. Determine which remote tracks the canonical repository and use it below as `<upstream-remote>`.

Every branch name must use `<epoch-seconds>-<github-username>`. Get the Unix epoch timestamp at branch creation time and the GitHub username from the authenticated `gh` account; do not substitute a descriptive name, date string, display name, or email address.

```bash
git status --short
git checkout master
git pull --ff-only <upstream-remote> master
GITHUB_USERNAME="$(gh api user --jq .login)"
EPOCH_TIMESTAMP="$(date +%s)"
BRANCH_NAME="${EPOCH_TIMESTAMP}-${GITHUB_USERNAME}"
git checkout -b "$BRANCH_NAME"
```

Run `git status --short` before switching branches and stop if it prints anything. Never carry, stash, clean, or discard pre-existing work for this workflow.

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

For an addition, the staged diff must show the new row with an empty `id` (the added line starts with `+,`). Never commit a generated, copied, or placeholder ID; see the ID rule in `SKILL.md`.

Commit only the appropriate per-region source CSV. Do not edit or regenerate root-level `breweries.csv`, `breweries.json`, `breweries.sql`, IDs, statistics, or contributor files; the repository maintainer handles those publication artifacts when merging the changes.

Before pushing, compare the branch with canonical `master` and confirm that the commit count equals the number of additions, deletions, and updates. If a commit contains more than one change, split it before opening the PR.

```bash
git fetch <upstream-remote> master
git rev-list --count HEAD..<upstream-remote>/master
git diff --check <upstream-remote>/master...HEAD
```

If the behind count is not zero, stop and update the branch without discarding user work before opening the PR.

## 3. Push and open the PR against the canonical repository

Push the branch to a writable remote, then explicitly target `openbrewerydb/openbrewerydb:master`. Do not rely on `gh` inferring the base repository from the current remote.

```bash
git push -u <writable-remote> "$BRANCH_NAME"
gh pr create \
  --repo openbrewerydb/openbrewerydb \
  --base master \
  --head "<head-owner>:${BRANCH_NAME}" \
  --title "<short summary>" \
  --body-file <temporary-pr-body-outside-worktree>
```

The PR body must start with these exact paragraphs, preserving their wording and blank lines:

> This pull request includes changes to the OpenBreweryDB dataset. Each change is its own commit and a full log of changes can be found below. Review all the changes to ensure the best data quality.
>
> If you need help or have any questions, join our Discord: https://discord.gg/3G3syaD

Below those paragraphs, add a `## Change log` section with one entry per commit in commit order. Each entry must include the short commit SHA, action (`Add`, `Delete`, or `Update`), brewery name, and a one-line summary. End the body by stating that no npm scripts were run because they are reserved for the maintainer's merge and publication workflow, and that generated artifacts were intentionally not changed.

Create PR body and comment files outside the dataset worktree so they cannot be committed accidentally. After creation, verify the PR URL is under `openbrewerydb/openbrewerydb`, its base is `master`, and only intended source CSVs changed:

```bash
gh pr view <pr-url> --repo openbrewerydb/openbrewerydb --json url,baseRefName,commits,files
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

For additions, include every field and use `(none)` for old values; show the `id` new value as `(blank)` because the maintainer assigns it when merging. For deletions, include every field and use `(none)` for new values. For updates, include only changed fields. Use actual source URLs, not generic source names, and explain any conflicting data or unavailable coordinates.

Post each prepared comment with:

```bash
gh pr comment <pr-url> --repo openbrewerydb/openbrewerydb --body-file <temporary-comment-outside-worktree>
```

Finally, inspect the PR comments and confirm there is exactly one sourced table comment for every change commit. Then inspect GitHub Actions with `gh pr checks <pr-url> --repo openbrewerydb/openbrewerydb --watch`. Report failures and their logs without running the corresponding npm scripts locally. Do not consider the workflow complete until comments are present and checks have reached a terminal state.

Always open a PR — never push directly to `master`, even for trivial one-field updates.
