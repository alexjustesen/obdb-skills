# Wikidata matching

## Candidate discovery

1. Search by brewery name plus city/country using Wikidata entity search or direct entity lookup.
2. Inspect candidate labels, aliases, descriptions, `instance of`, location/address, official website, coordinates, and identifiers that point to authoritative sources.
3. Use the Wikidata Query Service (WDQS) only when direct lookup is insufficient. Constrain by known QIDs, geography, class, or a small `VALUES` list; set a reasonable `LIMIT`.
4. Save the QID, entity URL, retrieval time, and the exact query or request URL.

Avoid unconstrained label scans, expensive property paths, repeated label-service calls, and queries intended to enumerate all breweries. Split a justified batch into small requests, cache responses, identify the client with a descriptive user agent where supported, and back off on `429`, timeout, or `5xx`. Follow current WDQS usage guidance if it is stricter than this document.

## Evidence

Strong evidence combines several independent fields:

- Exact official website host, allowing documented redirects or brand domains
- Street address and locality/postcode alignment
- Coordinates consistent with the same premises
- Name or alias alignment, including former names
- Entity type and description consistent with a brewery or the specific venue

Reject or downgrade candidates representing only a beer brand, parent company, building, event, or different branch. Treat copied directory data as one signal, not independent corroboration.

Wikidata may model an organization separately from its physical brewery locations. State which entity type the proposed link represents; do not equate organization and venue QIDs silently.

## Provenance and reuse

Wikidata structured data is CC0, but retain entity links, retrieval dates, and query provenance for auditability and useful attribution. Link to relevant statements and their references when a conclusion depends on them. This workflow reads Wikidata only and never edits statements.
