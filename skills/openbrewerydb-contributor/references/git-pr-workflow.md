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

## 3. Open the PR with the `openbrewerydb-pull-request` skill

Once every change is committed and the branch is current with canonical `master`, hand off to the `openbrewerydb-pull-request` skill. It pushes the branch, targets `openbrewerydb/openbrewerydb:master` explicitly, titles the PR `data: <short description>`, and writes a body with a summary plus one section per changed record containing the old/new attribute table, sources, and notes. It then verifies the PR and watches GitHub Actions.

Always open a PR — never push directly to `master`, even for trivial one-field updates.
