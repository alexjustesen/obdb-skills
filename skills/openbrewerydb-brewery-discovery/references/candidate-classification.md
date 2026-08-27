# Candidate classification

The comparison helper provides triage signals. A human-readable classification requires source research and inspection of possible dataset matches.

## Identity rules

- Never identify a business by normalized name alone when names are common or multiple locations exist.
- Strong identity signals are an exact official website host, full street address, postal code, and a matching name/location combination.
- Treat taprooms, production facilities, brewpubs, and food-hall locations separately when they have distinct public addresses.
- Legal company names, licensees, and customer-facing brewery names may differ. Record aliases and explain the relationship.
- A low helper score is not proof of absence; a high score is not proof of identity.

## Report categories

### Missing breweries

An eligible brewery operation has no matching Open Brewery DB record at any location/name variant. Require current evidence of the establishment and its public location.

### Additional locations

The brand exists in the dataset, but an independently eligible public location does not. Cite both the existing record and distinct address. Do not collapse nearby sibling locations.

### Renames/rebrands

The same operation and location continues under a changed customer-facing name. Establish continuity with official announcements, ownership/location evidence, or other reliable sources. A similar address alone can represent a replacement business.

### Relocations/updates

The dataset likely represents the same operation but has a stale address, website, phone, locality, or other field. Separate a move from an additional location: verify whether the old premises remains active.

### Status verification

Evidence is conflicting, old, incomplete, or indicates planning, temporary closure, permanent closure, acquisition, or an unclear operating model. State the exact unresolved question and best next source.

### Exclusions

Not actionable because the entry is ineligible, duplicate, outside the audit boundary, source-only administrative premises, wholesale-only without an eligible location, or unsupported. Give a reason and evidence so it is not repeatedly rediscovered.

### Addressed

Already represented by a matching dataset record or covered by an open issue/pull request. Include the record identifier/source file or GitHub URL and the matching rationale.

### Approved

Candidates explicitly approved by a human reviewer for later contributor work. Leave this section empty unless a human actually approves an item. Do not infer approval from confidence, evidence quality, an open issue/PR, or silence.

## Confidence

- **High:** identity and category supported by authoritative, current evidence with no material conflict.
- **Medium:** likely identity/category, but one material fact needs confirmation or relies on secondary evidence.
- **Low:** plausible lead with ambiguous identity, eligibility, location, or status.

Only report confidence alongside reasons and evidence. Keep medium/low findings visible rather than silently promoting or dropping them.

## Reverse comparison

A dataset record absent from the external list is not automatically stale or closed. First test whether the external source excludes nonmembers, certain license classes, new openings, closed businesses, border localities, or additional locations. Classify reverse-only records as `Status verification`, `Exclusions`, or `Addressed` after research; never recommend deletion from absence alone.
