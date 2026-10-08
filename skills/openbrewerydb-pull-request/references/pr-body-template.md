# PR body template

Copy the opening paragraphs exactly, including the blank line between them. Replace every `<placeholder>` and remove any that don't apply. Repeat the `###` change section once per commit, in commit order.

```markdown
This pull request includes changes to the OpenBreweryDB dataset. Each change is its own commit and a full log of changes can be found below. Review all the changes to ensure the best data quality.

If you need help or have any questions, join our Discord: https://discord.gg/3G3syaD

## Summary

<What changed and where, why it changed, and how it was researched. End with the counts, for example: "2 additions, 1 update, 0 deletions.">

## Changes

### Add: <Brewery Name>

**Commit:** `<short-sha>`
**Source file:** `<data/country/region.csv>`

<One or two sentences on this record: why it is being added and anything notable about it.>

| Field | Old value | New value |
|---|---|---|
| `id` | (none) | (blank) |
| `name` | (none) | <value> |
| `brewery_type` | (none) | <value> |
| `<every remaining column in header order>` | (none) | <value or (blank)> |

**Sources**

- <URL>: <what it verifies>

**Notes:** <conflict resolution, geocoding accuracy, missing values and why>

### Update: <Brewery Name>

**Commit:** `<short-sha>`
**Source file:** `<data/country/region.csv>`

<One or two sentences on what changed and why.>

| Field | Old value | New value |
|---|---|---|
| `<changed field only>` | <old value or (blank)> | <new value or (blank)> |

**Sources**

- <URL>: <what it verifies>

**Notes:** <reviewer-relevant details>

### Delete: <Brewery Name>

**Commit:** `<short-sha>`
**Source file:** `<data/country/region.csv>`

<Why deletion is correct here rather than setting `brewery_type` to `closed`.>

| Field | Old value | New value |
|---|---|---|
| `id` | <existing id> | (none) |
| `<every remaining column in header order>` | <value or (blank)> | (none) |

**Sources**

- <URL>: <what it verifies>

**Notes:** <reviewer-relevant details>

## Reviewer notes

- No npm scripts were run; they are reserved for the maintainer's merge and publication workflow.
- Generated artifacts (`breweries.csv`, `breweries.json`, `breweries.sql`), statistics, and contributor files were intentionally left unchanged.
- New rows have a blank `id` for the maintainer to assign when merging.
```

## Value conventions

| Meaning | Write |
|---|---|
| The field did not exist before (addition) or will not exist after (deletion) | `(none)` |
| The field exists and is intentionally empty, including a new brewery's `id` | `(blank)` |

Escape a literal pipe character in a value with a backslash so it doesn't split the table cell.
