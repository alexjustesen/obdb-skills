# PR body template

The body summarizes the whole pull request. Each record's attribute table, sources, and notes go in its own comment instead; see `change-comment-template.md`.

Copy the opening paragraphs exactly, including the blank line between them. Replace every `<placeholder>` and remove any that don't apply. Add one row to the changes table per commit, in commit order.

```markdown
This pull request includes changes to the OpenBreweryDB dataset. Each change is its own commit and a full log of changes can be found below. Review all the changes to ensure the best data quality.

If you need help or have any questions, join our Discord: https://discord.gg/3G3syaD

## Summary

<What changed and where, why it changed, and how it was researched. End with the counts, for example: "2 additions, 1 update, 0 deletions.">

## Changes

Each change below has its own comment on this pull request with the full attribute table, sources, and notes.

| # | Action | Brewery | Location | Commit |
|---|---|---|---|---|
| 1 | Add | <Brewery Name> | <City, State> | `<short-sha>` |
| 2 | Update | <Brewery Name> | <City, State> | `<short-sha>` |

## Reviewer notes

- No npm scripts were run; they are reserved for the maintainer's merge and publication workflow.
- Generated artifacts (`breweries.csv`, `breweries.json`, `breweries.sql`), statistics, and contributor files were intentionally left unchanged.
- New rows have a blank `id` for the maintainer to assign when merging.
```

Escape a literal pipe character in a value with a backslash so it doesn't split the table cell.
