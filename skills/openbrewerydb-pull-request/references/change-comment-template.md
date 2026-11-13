# Change comment template

Post one comment per commit, in commit order. Use the section that matches the commit's action, replace every `<placeholder>`, and remove any that don't apply. Each comment must stand on its own: a reviewer may read it without the PR body.

## Add

```markdown
## Add: <Brewery Name>

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
```

## Update

```markdown
## Update: <Brewery Name>

**Commit:** `<short-sha>`
**Source file:** `<data/country/region.csv>`

<One or two sentences on what changed and why.>

| Field | Old value | New value |
|---|---|---|
| `<changed field only>` | <old value or (blank)> | <new value or (blank)> |

**Sources**

- <URL>: <what it verifies>

**Notes:** <reviewer-relevant details>
```

## Delete

```markdown
## Delete: <Brewery Name>

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
```

## Value conventions

| Meaning | Write |
|---|---|
| The field did not exist before (addition) or will not exist after (deletion) | `(none)` |
| The field exists and is intentionally empty, including a new brewery's `id` | `(blank)` |

Escape a literal pipe character in a value with a backslash so it doesn't split the table cell.
