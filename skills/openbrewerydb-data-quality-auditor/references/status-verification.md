# Status verification

Status auditing combines the helper's deterministic candidate queue with current web evidence. A `closed` or `planning` CSV value is only a reason to investigate.

## Evidence order

1. Brewery-owned website, location page, or dated announcement
2. Recent official social account announcement
3. Current government/business registry or property notice where applicable
4. Recent, reputable local reporting
5. Multiple current third-party listings

Search snippets, undated directory pages, and a single map status are leads, not sufficient evidence by themselves. Record each URL, publication/update date, access date, and the exact claim it supports.

## Procedure

1. Identify the exact location using name, full address, ID, and official URL. Avoid conflating a production brewery, taproom, or sibling location.
2. Search for current operating, closure, relocation, ownership, and planning/opening evidence.
3. Prefer newer first-party evidence when sources conflict. Explain conflicts rather than silently choosing one.
4. Classify the result as `confirmed current`, `likely stale`, `conflicting`, or `insufficient evidence`.
5. Search open issues and PRs using the ID, name, city, and status terms before recommending a new issue.
6. Report the observed CSV value and evidence-backed expected value. Do not edit the row or open an implementation PR.

## Confidence

- High: dated first-party statement or multiple recent authoritative sources identify the exact location.
- Medium: multiple recent independent sources agree, but no current first-party statement exists.
- Low: one directory, ambiguous location identity, stale evidence, or unresolved conflict.

Closure dates matter. A brewery may announce a future closure while still operating, and an old closure may be followed by reopening under the same or a different identity. Never infer `closed` merely because a website is unavailable.
