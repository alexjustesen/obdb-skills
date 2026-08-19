# Git & PR workflow

Assumes `gh` (GitHub CLI) is installed and authenticated, and the repo remote is already configured with push access (or a fork remote, if that's how this repo is contributed to — check `git remote -v` if unsure). These should already have been confirmed at step 0 of `SKILL.md` — if you're here and they weren't checked, go back and check first.

The npm commands in the upstream repository's [`Scripts` section](https://github.com/openbrewerydb/openbrewerydb#%EF%B8%8F-scripts) are owner-only publication tools. Never run them, invoke their implementation files directly, reproduce their mutating behavior, or include their generated output in a contributor commit. This includes `npm run validate`, `npm run csv:combine`, and every generation, contributor, and maintenance command listed there. See the mandatory owner-only scripts rule in `SKILL.md`.

## 1. Branch

Create one branch per session/request, off freshly-pulled `master`:

```bash
git checkout master
git pull origin master
git checkout -b add-breweries-<short-description-or-date>
```

Use a descriptive branch name based on what's being added/updated, e.g. `add-fox-farm-brewery-ct` or `update-ct-breweries-phone-numbers`.

## 2. One commit per brewery

For each brewery in this session, stage only the file(s) touched for that brewery and commit separately, so the maintainer can review or revert each one independently:

```bash
git add <path-to-csv>
git commit -m "Add <Brewery Name> to <state_or_country>.csv"
```

or for updates:

```bash
git add <path-to-csv>
git commit -m "Update <Brewery Name>: <what changed, e.g. phone, website>"
```

Keep messages specific about what changed, not just "update csv."

Commit only the appropriate per-region source CSV. Do not edit or regenerate root-level `breweries.csv`, `breweries.json`, `breweries.sql`, IDs, statistics, or contributor files; the repository owner handles those publication artifacts after merge.

## 3. Push and open the PR

```bash
git push -u origin add-breweries-<short-description-or-date>
gh pr create --title "<short summary, e.g. 'Add 3 Connecticut breweries'>" --body "<aggregated diff summary>"
```

The PR body should restate the per-brewery diff summaries already shown to the user in chat (new row contents, or old→new for updates), so the PR is self-documenting for the reviewer — don't make them dig through commits to see what changed. State that owner-only publication scripts were intentionally not run and generated artifacts were intentionally not changed.

Always open a PR — never push directly to `master`, even for trivial one-field updates.
