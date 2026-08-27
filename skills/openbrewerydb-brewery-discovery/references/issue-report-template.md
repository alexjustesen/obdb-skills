# Issue report template

Use this structure by default. Remove instructional placeholders, but keep every category heading. `Approved` stays empty unless a human explicitly approves an item.

```markdown
# Brewery coverage audit: <region/source>

## Scope

- **Region/boundary:** <boundary>
- **Eligibility:** <included and excluded establishment types>
- **Dataset snapshot:** <commit SHA/date>
- **Research completed:** <date>

## Sources

| Source | Publisher/authority | Published or updated | Retrieved | License/reuse | Scope and limitations |
|---|---|---|---|---|---|
| <URL> | <publisher and authority> | <date/unknown> | <date> | <license/terms URL> | <coverage and omissions> |

## Methodology

Compared a normalized external inventory against every `data/**/*.csv` source file using normalized names, website hosts, and addresses. Reviewed possible matches, performed the reverse comparison, researched eligibility/status, and searched all open Open Brewery DB issues and pull requests using name, alias, location, website, and address variants.

## Summary

| Result | Count |
|---|---:|
| External inventory records | <count> |
| Dataset source records scanned | <count> |
| Missing breweries | <count> |
| Additional locations | <count> |
| Renames/rebrands | <count> |
| Relocations/updates | <count> |
| Status verification | <count> |
| Exclusions | <count> |
| Addressed | <count> |
| Approved | 0 unless human-approved |

## Missing breweries

### <brewery name>
- **Proposed category/confidence:** Missing brewery / <high|medium|low>
- **Address:** <address>
- **Website:** <URL>
- **Evidence:** <URLs with dates and what each establishes>
- **Possible dataset matches:** <record/file or none; explain differences>
- **Open issue/PR check:** <queries/date; links or none found>
- **Rationale/unknowns:** <why missing and unresolved facts>

## Additional locations

<Use the candidate fields above and identify the existing sibling record plus the distinct location.>

## Renames/rebrands

<Use the candidate fields above and document continuity from old to new identity.>

## Relocations/updates

<Use the candidate fields above and list likely stale fields; confirm whether the prior location remains active.>

## Status verification

<Use the candidate fields above and state the exact question requiring verification. Include reverse-only dataset records when appropriate.>

## Exclusions

| Entry | Reason | Evidence |
|---|---|---|
| <name> | <ineligible/duplicate/out of scope/etc.> | <URLs> |

## Addressed

| Entry | Existing record or open issue/PR | Match rationale |
|---|---|---|
| <name> | <record/file/GitHub URL> | <reason> |

## Approved

<!-- Leave empty unless a human reviewer explicitly approves candidates. -->

## Reverse comparison notes

<Summarize dataset records absent from the external inventory, source-scope explanations, researched outcomes, and unresolved leads. Absence alone is not evidence for deletion.>

## Limitations

<Source age, licensing constraints, inaccessible evidence, ambiguous identities, and coverage gaps.>
```
