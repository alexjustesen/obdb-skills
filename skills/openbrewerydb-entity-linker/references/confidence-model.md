# Confidence model

Assign one level to each OBDB-to-external-entity proposition. Explain the decisive evidence; do not average fields into an unexplained score.

## High

Multiple independent attributes agree with no material contradiction. Normally require name/alias compatibility plus at least two strong signals among exact official website host, full address, and premises-consistent coordinates. The entity type and location cardinality must also be correct.

Suitable wording: `High-confidence proposed match; maintainer review requested.`

## Medium

The candidate is probably the same entity, but one strong field is missing, stale, approximate, or only indirectly corroborated. Examples include matching name/address without a website, or matching website/locality with imprecise coordinates.

Suitable wording: `Probable match; verify <specific missing evidence> before adoption.`

## Low

Evidence is sparse or generic, such as name plus city only, and plausible alternatives remain. Keep the candidate for research but do not recommend it as an identifier link.

Suitable wording: `Candidate only; insufficient evidence to link.`

## Conflict

Material evidence indicates different entities or incompatible relationships: different official domains, addresses in different premises, distinct branches sharing a name, organization-versus-venue mismatch, closure/replacement ambiguity, or one-to-many/many-to-one uncertainty.

`Conflict` takes precedence over high similarity. State the competing evidence and the exact maintainer decision or additional source needed. Never force a winner.

## Evidence discipline

- Name alone can never exceed `low`.
- Coordinates alone can never exceed `medium` and should be evaluated against geometry/source precision.
- A shared official website is strong but may cover a chain or parent organization.
- Address agreement is strong only when unit/site distinctions are considered.
- Prefer current first-party evidence; note dates for mutable facts.
- Reused or copied data across directories is not independent corroboration.
