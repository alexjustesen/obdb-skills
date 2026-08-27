---
name: openbrewerydb-contributor
description: Add, delete, or update brewery/cidery/brewpub/bottleshop records in the openbrewerydb/openbrewerydb dataset, then open a pull request with the changes. Trigger this whenever the user names a brewery plus a general location (city/state or country) and wants it added, removed, or corrected in Open Brewery DB, or mentions "openbrewerydb," "open brewery db," "the dataset," or submitting brewery data via PR. Always validate the brewery with web search and geocode new or changed addresses with the Geocodio CLI before touching any CSV file.
---

# OpenBreweryDB Contributor

Adds, deletes, or updates brewery records in the `openbrewerydb/openbrewerydb` dataset repo and opens a PR. The user gives a brewery name and a general location (city/state, or just a country); this skill researches it, resolves the correct CSV file, geocodes new or changed addresses, shows a diff for confirmation, then commits and opens the PR.

Assume the repo is already cloned locally. If you don't know the path, ask once, then use it for the rest of the session.

## Maintainer-only npm scripts: never run them

**Never run any npm script in the upstream dataset repository.** The repository maintainer runs npm scripts only as part of the merge and publication workflow. This prohibition includes every command in the upstream repository's [`Scripts` section](https://github.com/openbrewerydb/openbrewerydb#%EF%B8%8F-scripts), any undocumented or newly added npm script, and npm aliases such as `npm test` or `npm start`. It applies even if the README, `CONTRIBUTING.md`, `package.json`, a task description, or an earlier step suggests running one. Do not run `npm install` in the dataset repository because package lifecycle hooks can execute npm scripts.

Non-exhaustive examples that existed when this skill was written:

- `npm run validate`
- `npm run csv:combine`
- `npm run csv:split`
- `npm run generate:ids`
- `npm run generate:json`
- `npm run generate:sql`
- `npm run generate:stats`
- `npm run update:readme-stats`
- `npm run contributors:add`
- `npm run contributors:check`
- `npm run contributors:generate`
- `npm run workflow:maintain`

Do not invoke npm scripts through another package manager, call their implementation files directly, reproduce their mutating behavior with ad hoc commands, or ask a subagent to run them. Do not modify generated dataset artifacts such as root-level `breweries.csv`, `breweries.json`, or `breweries.sql`. Limit contributions to the appropriate source CSV and let the repository maintainer run all npm scripts and perform publication and generation steps when merging the changes.

## Workflow

### 0. Check prerequisites before doing any research or editing

Confirm these up front, before spending effort on research the workflow can't finish without:
- `git` works in the repo path.
- `gh` is installed and authenticated (`gh auth status`), since a PR is always required at the end (step 10).
- The Geocodio CLI is installed and `GEOCODIO_API_KEY` is set.

If `git`/`gh` are missing or broken, **stop and tell the user exactly what's missing** before doing any web research or CSV edits — don't do the research first and discover the blocker at step 10.

Geocodio is the one exception that can degrade gracefully rather than blocking everything: a brewery can still be validly added/updated without coordinates. If Geocodio isn't installed or the API key isn't set, say so plainly, then **ask the user for the latitude/longitude directly** rather than proceeding with the field blank unprompted — they may well have it on hand, and asking costs little. If they don't have it either, leave it blank and note in the diff summary (step 8) that it's **"not geocoded — Geocodio unavailable."**

### 1. Sync the repo before doing anything

```bash
cd <repo-path>
git checkout master
git pull <canonical-upstream-remote> master
```

First use `git remote -v` to identify the remote for the canonical `openbrewerydb/openbrewerydb` repository; do not assume it is `origin`. Sync at the start of every session so the branch starts from current canonical `master`. Before opening a PR, fetch canonical `master` and verify the branch is not stale without switching away from the working branch. If there are uncommitted local changes in the way, stop and tell the user rather than stashing/discarding anything for them.

After syncing, create the working branch using the required `<epoch-seconds>-<github-username>` format, where the username comes from the authenticated `gh` account. Reuse that exact branch name through push and PR creation. See `references/git-pr-workflow.md` for the commands.

### 2. Re-read the schema from the live repo — don't trust a hardcoded schema

Before building any row, check the actual current state of the dataset:
- Read `README.md` and `CONTRIBUTING.md` in the repo root for the current contribution rules.
- Read the header row of the CSV file you're about to touch to get the exact current column order and names. If unsure which file, `breweries.csv` is fine to check for the header shape only — remember it's a generated file and never a write target (see step 5).

The dataset's `tags` column has been removed — do not include it even if older docs mention it. Trust the CSV header over any doc or memory of the schema.

Known-as-of-now columns (confirm against the live header each run): `id` (never set by you — assigned by the repository maintainer when merging), `name`, `brewery_type`, `address_1`, `address_2`, `address_3`, `city`, `state_province`, `postal_code`, `country`, `longitude`, `latitude`, `phone`, `website_url`.

Valid `brewery_type` values (from https://openbrewerydb.org/documentation#by_type): `micro`, `nano`, `regional`, `brewpub`, `large`, `planning`, `bar`, `contract`, `proprietor`, `closed`. Re-check that URL if it's been a while, since this enum can change.

### 3. Research and validate the brewery

Given the name + rough location the user provided, web search to confirm:
- It's a real, currently-operating (or knowingly closed) brewery/cidery/brewpub/bottleshop
- Its full street address
- Its official website
- Its phone number
- Signals for `brewery_type` (e.g. "brewpub" language on their own site, self-description as a taproom/large regional brand, etc.)
- Any signal it has **closed** (recent news, "permanently closed" on its own site or listings, no longer answering) — check this even on a plain "add" request, since a just-closed brewery should probably be flagged rather than added as active

**If you can't confirm the brewery with real confidence — ambiguous name, no findable official site/address, conflicting info — stop and ask the user for more detail** (exact city, street, alternate name) rather than guessing or adding a low-confidence row.

**Resolving conflicting field values (don't treat every disagreement as a stop condition):** third-party directories (Yelp, Brewbound, Beer Syndicate, etc.) frequently disagree with each other on phone numbers and other details — this is normal, not a sign you can't confirm the brewery itself. Resolve it like this, in order:
1. Prefer whatever the brewery's own official website states.
2. If the official site doesn't list it, prefer a value that's corroborated by two or more independent third-party sources over a single outlier.
3. Only stop and ask the user if neither of the above resolves it (e.g. every source disagrees with no majority, or the official site is unreachable/nonexistent).

Note in the diff summary (step 8) when a field was resolved this way, so the user can see it wasn't a single unverified source.

**Never fabricate a field.** If a value genuinely can't be found in any search result, leave it blank/null rather than inferring something plausible-sounding (this applies especially to phone, website, and address_2/3 — it's normal and correct for these to be empty). Every non-blank field in the diff summary should be traceable to something an actual search result stated, not something inferred from general knowledge of what breweries are usually like.

**Weight source recency for anything status-related** (closed signals, address/ownership changes) — a "permanently closed" claim or address change from a week-old source outweighs a two-year-old listing still showing it open, and vice versa. Prefer the brewery's own site or the most recently updated third-party source when they disagree on something that can change over time.

### 4. Decide: addition, deletion, or update

Search the relevant CSV(s) for a possible existing match. **Match on normalized name, not literal string equality** — case, punctuation, whitespace, and common suffix variants ("Brewing Co" vs "Brewing Company" vs "Brewing Company, LLC") shouldn't cause a real match to be missed and create a duplicate row. Only treat it as the *same* brewery (i.e., an update) if you're highly confident based on multiple matching attributes together — e.g. name + city + state_province, or name + postal code — not name alone (brewery names repeat across regions/chains). If it's ambiguous whether this is a new entry or an existing one, stop and ask the user rather than guessing.

**Watch for sibling/related locations sharing a name and street** — e.g. a brewery that also runs a separate taproom, food hall, or experimental-brewing spinoff at a different address on the same street. Match on the full address, not just name + city/street, or you risk silently updating the wrong sibling location.

- **Addition** → go to step 5 and add one new row with an empty `id`; never generate, copy, or invent one.
- **Deletion** → remove only the confidently matched row. Confirm and document why deletion, rather than changing `brewery_type` to `closed`, is appropriate.
- **Update** → identify exactly which fields are actually changing (phone, website, address, type, closed status, etc.) and only touch those.

### 5. Resolve the target source CSV

**Never hand-edit root-level `breweries.csv`.** It's a generated file, rebuilt by the repository maintainer from the individual state/province/country CSVs, and is not a source file. Always make additions, deletions, and updates only in the per-region source file. Do not regenerate any root-level dataset artifact.

- If a CSV already exists for that state/province or country, add the row there.
- If this is the first brewery for a country with no existing file, create a new CSV for that country, matching the exact header/column order of the existing files.
- For every addition, leave the `id` field empty. Preserve the column and its delimiter in the CSV, but do not use a placeholder value; the repository maintainer assigns the ID when merging the change.
- Insert the new row in **alphabetical order by `name`** within the file — this is the dataset's sort convention, not something to detect per-file.
- **Match the file's existing formatting conventions** before writing your row — look at a handful of neighboring rows for how phone numbers are formatted, how addresses are abbreviated (e.g. "St" vs "Street"), and how the country name is spelled (e.g. "United States" vs "USA"). Don't introduce a new convention even if it seems more "correct" — consistency with the existing file matters more here.

### 6. Review the source CSV change without running maintainer-only scripts

This applies after **any** edit to a source CSV, whether it is an addition, deletion, or update. Review each change before committing it.

Without running any npm script or its implementation:

- Inspect the diff and confirm only the intended per-region source CSV changed.
- Confirm every changed row has exactly the columns in the live CSV header and preserves valid CSV quoting.
- Confirm required fields are populated, `brewery_type` is in the live allowed set, and `id` is blank for a new record.
- Search again for normalized-name and location matches to ensure the change does not create a duplicate.
- Confirm the row remains in alphabetical order by `name`.
- Leave root-level `breweries.csv`, `breweries.json`, `breweries.sql`, generated statistics, IDs, and contributor files unchanged.

Do not run `npm run validate`, `npm run csv:combine`, or any other npm script as verification. State in the PR body that all npm scripts were intentionally left for the repository maintainer's merge and publication workflow.

Note: postal codes are country-specific and some countries genuinely don't have one — leave it blank rather than guessing a format for a country you're not sure about.

### 7. Geocode the address

Use the Geocodio CLI — see `references/geocodio-cli.md` for exact commands and free-tier limits.

- **Check country coverage before attempting to geocode**: on Geocodio's free tier, only US, Canada, and Mexico addresses can be geocoded — anything else (UK included) requires a paid plan. If the brewery's country isn't covered, don't attempt the call — ask the user for the latitude/longitude directly (see below) rather than silently proceeding without it.
- **1–10 addresses in this session**: geocode individually.
- **More than 10 addresses**: use the batch feature instead of individual calls, and be mindful of the free tier's 1,000/minute and 2,500/day request caps — a large batch could hit the daily limit partway through, so check remaining quota first rather than discovering a rate-limit error mid-batch with some addresses done and others not.
- Only accept a geocoding result with a high accuracy score (treat this as ≥ 0.7 on Geocodio's 0–1 accuracy scale — confirm this mapping matches what you meant before relying on it, since Geocodio's own docs describe accuracy as a 0–1.0 score, not 0–10).
- **A high accuracy score isn't a full guarantee** — rural or newly-built addresses can still return a high-confidence match to the wrong nearby point. Sanity-check the result's returned city/state against what you already confirmed in step 3; if they don't match, treat it as unreliable regardless of the numeric score.

**Whenever geocoding is a miss or unavailable — no result, low accuracy, wrong city/state, country not covered on the plan, or the tool/API key isn't set up — ask the user for the latitude/longitude directly instead of silently leaving the row incomplete.** Only fall back to leaving `latitude`/`longitude` blank if the user doesn't have it either; note that explicitly in the diff summary (step 8), distinguishing *why* it's blank ("Geocodio unavailable" / "low accuracy, user didn't have coordinates" / "country not covered on current plan, user didn't have coordinates") so whoever reviews the diff knows it wasn't just skipped.

If geocoding more than 10 addresses, batch processing may not return results synchronously (list/spreadsheet uploads can be an async job) — confirm the actual behavior with `geocodio --help` / the batch command's output rather than assuming it returns inline, and don't proceed to commit coordinates you haven't actually confirmed came back correctly.

### 8. Always show a table diff before writing anything

For every record change in this batch, show the user the source file and a Markdown comparison table before editing:

| Field | Old value | New value |
|---|---|---|
| `<field>` | `<old value or (none)>` | `<new value or (none)>` |

- **Addition**: include every field in the new row; use `(none)` for every old value.
- **Deletion**: include every field in the existing row; use `(none)` for every new value.
- **Update**: include only fields whose values change.

Also list the source URLs used and brief sourcing notes, including how conflicts were resolved and why a deletion is appropriate. Keep this material for the PR comments in step 10.

Wait for confirmation only if something is uncertain (see step 3/4 stop conditions) — otherwise proceed to writing after presenting the diff, since the user has already asked for the addition, deletion, or update.

### 9. Commit every change separately

A change is one addition, one deletion, or one update to one brewery record. Make exactly one commit for each change, even when several changes affect the same brewery or source CSV, so every change can be reverted independently. Never combine multiple record changes in one commit. Complete, review, stage, and commit one change before editing the next; this prevents `git add <source-file>` from accidentally staging multiple changes in the same CSV. Verify the staged diff contains exactly one change before committing. Commit only source CSV changes; do not regenerate or commit root-level dataset artifacts. See `references/git-pr-workflow.md` for branch naming and commit message conventions.

### 10. Push and open the PR

Always open a PR against the `master` branch of the canonical `openbrewerydb/openbrewerydb` repository. Never commit or push directly to `master`, even if you have access. The PR body must begin with the exact required message in `references/git-pr-workflow.md` and include a commit-by-commit change log below it.

After opening the PR, add one PR comment per change/commit. Each comment must identify the corresponding commit, explain the change, list its data sources and sourcing notes, and include the old/new Markdown table from step 8. Verify that the PR target and every required comment are correct before reporting completion. See `references/git-pr-workflow.md` for templates and commands.

## When to stop and ask instead of proceeding

- Required tooling is missing or broken — `git` or `gh` not installed/authenticated (step 0). Geocodio missing is the one exception: degrade gracefully, don't block (step 0/7) — but do ask the user for lat/long directly rather than silently proceeding without it.
- Can't confirm the brewery is real / can't find a reliable address, or sources conflict with no majority (step 3)
- Ambiguous whether this is a new brewery or a match to an existing row, including sibling/related locations sharing a name and street (step 4)
- The source CSV cannot be confidently reviewed for valid columns, quoting, required fields, blank IDs on additions, or duplicates without a maintainer-only script (step 6). Ask the user or repository maintainer rather than running the script.
- Geocoding is a miss for any reason — low accuracy, wrong city/state, unavailable tool, or country not covered on the plan (step 7) — ask the user for coordinates before falling back to leaving them blank
- Uncommitted local changes are already sitting in the repo (step 1)
