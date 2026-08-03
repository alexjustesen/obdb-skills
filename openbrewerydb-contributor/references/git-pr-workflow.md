# Git & PR workflow

Assumes `gh` (GitHub CLI) is installed and authenticated, and the repo remote is already configured with push access (or a fork remote, if that's how this repo is contributed to — check `git remote -v` if unsure). These should already have been confirmed at step 0 of `SKILL.md` — if you're here and they weren't checked, go back and check first.

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

If the repo's generation script regenerates `breweries.csv` and that regenerated file is meant to be committed too, do that as its own separate commit (e.g. `git commit -m "Regenerate breweries.csv via npm run csv:combine"`) — never fold a hand-edit of `breweries.csv` into a brewery's commit, since it's a build artifact, not something edited directly.

Before any of this, always run `npm run validate` after editing a source CSV and before running `npm run csv:combine` — fix anything it flags first.

## 3. Push and open the PR

```bash
git push -u origin add-breweries-<short-description-or-date>
gh pr create --title "<short summary, e.g. 'Add 3 Connecticut breweries'>" --body "<aggregated diff summary>"
```

The PR body should restate the per-brewery diff summaries already shown to the user in chat (new row contents, or old→new for updates), so the PR is self-documenting for the reviewer — don't make them dig through commits to see what changed.

Always open a PR — never push directly to `master`, even for trivial one-field updates.
