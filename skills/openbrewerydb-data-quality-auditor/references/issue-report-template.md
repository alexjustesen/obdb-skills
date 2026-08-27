# Issue report template

Use this structure for the default deliverable. Remove empty sections rather than inventing evidence.

```markdown
## Summary

<One concise, evidence-backed description of the data-quality problem.>

## Audit scope

- Dataset revision: `<commit SHA if available, otherwise state unknown>`
- Modes: `<structural|identity|completeness|geospatial|status>`
- Source scope: `data/**/*.csv`
- Audit date: `<YYYY-MM-DD>`

## Findings

| Severity | Confidence | File | Row | ID | Check | Evidence |
|---|---|---|---:|---|---|---|
| `<severity>` | `<confidence>` | `<source-relative path>` | `<row>` | `<id or (blank)>` | `<check>` | `<observed values>` |

## External verification

<For status/geospatial/identity claims, list current sources, access dates, and what each source establishes. Distinguish facts from inference.>

## Related open issues and PRs

- `<URL>` - `<relationship, or "None found" plus search terms used>`

## Suggested resolution

<Describe the expected data outcome for maintainer review. Do not include or apply a dataset patch.>

## Audit safety

This was a read-only audit. No dataset files were changed, no npm command was run, and no upstream script implementation was invoked.
```

Keep one issue focused on one coherent defect or tightly related set of rows. If evidence is incomplete, title and describe it as a verification request rather than asserting that the dataset is wrong.
