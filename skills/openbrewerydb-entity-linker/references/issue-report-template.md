# Issue report template

Use this structure for the returned issue-ready Markdown draft. This read-only skill does not post it. Remove instructional placeholders, but retain sections that have no matches by writing `None`.

```markdown
Title: External entity linkage audit: <bounded scope>

## Scope

- OBDB records: <IDs, names, and API/source URLs>
- External sources: <Wikidata, OSM, or both>
- Retrieved: <UTC timestamp>
- Scope boundary: <city/region/explicit ID list>

## Existing work

- Open issues searched: <queries and links/results>
- Open PRs searched: <queries and links/results>
- Duplicate assessment: <new, already tracked, or related>

## Proposed links

| OBDB ID | OBDB record | External entity | Relationship | Confidence | Decisive evidence |
|---|---|---|---|---|---|
| `<id>` | `<name and URL>` | `<QID URL or OSM type/id URL>` | `<same location / organization / related venue>` | `<high / medium / low / conflict>` | `<brief evidence>` |

## Evidence details

### <OBDB ID> ↔ <QID or OSM type/id>

| Field | OpenBreweryDB | External source | Assessment |
|---|---|---|---|
| Name/aliases | `<value>` | `<value>` | `<match/difference>` |
| Address | `<value>` | `<value>` | `<match/difference>` |
| Website | `<value>` | `<value>` | `<match/difference>` |
| Coordinates | `<lat, lon>` | `<lat, lon or geometry>` | `<distance/context>` |

Sources: <direct URLs and retrieval dates>

## Rejected candidates

| Candidate | Reason rejected |
|---|---|
| `<URL>` | `<specific contradictory evidence>` |

## Cardinality and conflicts

<Describe one-to-many, many-to-one, branch, brand, organization, venue, duplicate, or unresolved relationships.>

## Query provenance

- OBDB: `<request URL/parameters>`
- Wikidata: `<entity requests and exact SPARQL/query URL, if used>`
- OSM: `<object URLs and exact bounded Nominatim/Overpass request or query, if used>`
- Rate-limit handling/cache: `<what was done>`

## Maintainer decision requested

<Ask for review of the linkage analysis or a future schema/interoperability discussion. Do not request direct external-ID writes because the current schema has no fields for them.>

## Attribution and policy notes

- Wikidata links and retrieval provenance retained; Wikidata structured data is CC0.
- OSM data, if used: © OpenStreetMap contributors, https://www.openstreetmap.org/copyright (ODbL).
- Public service policies and rate limits were observed; no bulk scraping or writes were performed.
- No dataset/schema files, external entities, generated artifacts, or identifiers were modified.
- No npm install, npm scripts, package-manager equivalents, or upstream implementations were run.
```
