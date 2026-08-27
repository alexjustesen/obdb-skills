# Audit checks

Run only against source files under `data/**/*.csv`. Root-level combined exports and generated JSON/SQL files are outside scope.

## Modes

### Structural

- CSV parse/read errors
- Empty files or missing headers
- Headers that differ from the most common source-file header
- Missing required columns: `id`, `name`, `brewery_type`, `city`, `state_province`, `postal_code`, and `country`
- Rows whose value count differs from the header
- Blank IDs, duplicate non-blank IDs, and non-UUID IDs
- Values outside the live brewery type enum from `src/config.ts`
- Non-blank website values that are not absolute URLs
- Whole-file normalized name ordering

Header inconsistency is a repository-wide comparison, not proof that the modal header is authoritative. Confirm against current project documentation before filing.

### Identity

- Duplicate non-blank IDs
- Exact normalized identity signals across rows

The helper normalizes case, whitespace, and punctuation and compares name plus available location fields (`address_1`, `city`, `state_province`, `postal_code`, `country`). A match is a candidate, not proof: chains, taprooms, and sibling locations can legitimately resemble each other.

### Completeness

- Blank required values for `name`, `brewery_type`, `city`, `state_province`, `postal_code`, and `country`
- Values shorter than the live schema minimums for city, state/province, postal code, and country
- Per-file and dataset-wide populated/blank counts for every observed column

An empty value can be legitimate. Prioritize required fields and patterns suggesting one file or region differs substantially from peers.

### Geospatial

- Latitude or longitude present without its pair
- Non-numeric coordinates
- Latitude outside `-90..90` or longitude outside `-180..180`
- Zero latitude or longitude, including `(0, 0)`

Zero coordinates are review signals rather than confirmed errors. Verify the address and map location before recommending a correction.

### Status

- Rows marked `closed` or `planning` are queued for current external verification

The helper cannot determine real-world operating status. Complete the process in `status-verification.md`; never change status based only on the generated candidate.

## Triage

Suggested interpretation of helper metadata:

| Severity | Meaning |
|---|---|
| `error` | Strong schema, uniqueness, parse, or coordinate validity problem |
| `warning` | Likely inconsistency requiring context |
| `info` | Review queue or summary signal, not a defect claim |

| Confidence | Meaning |
|---|---|
| `high` | Directly observable invariant violation |
| `medium` | Deterministic signal with plausible legitimate exceptions |
| `low` | Requires substantial external verification |

Confirm a representative sample and check related open issues and PRs before drafting an issue. Do not combine unrelated defect classes merely because one audit run found them together.
