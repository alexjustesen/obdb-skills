# Geocodio CLI reference

Full docs: https://www.geocod.io/cli · GitHub: https://github.com/Geocodio/geocodio-cli

Assume the CLI is already installed and `GEOCODIO_API_KEY` is already set in the environment. If a command fails with an auth or "command not found" error, tell the user rather than trying to install/configure it yourself.

## Single address

```bash
geocodio geocode "123 Main St, Springfield, IL"
```

Add `--fields` for extra appended data if ever needed (not required for this skill):

```bash
geocodio geocode "123 Main St, Springfield, IL" --fields timezone,cd
```

Use `--json` for machine-readable output or `--agent` for a Markdown table:

```bash
geocodio geocode "123 Main St, Springfield, IL" --json
```

## Synchronous batch

```bash
geocodio geocode --batch addresses.txt
```

The input has one complete address per line. Batch geocoding waits for results and accepts up to 10,000 items. Split larger inputs.

## Asynchronous spreadsheet processing

For a CSV whose first columns are street, city, region, postal code, and country:

```bash
geocodio lists upload data.csv --direction forward --format "{{A}}, {{B}}, {{C}} {{D}}, {{E}}" --watch
```

Without `--watch`, retain the returned list ID and use:

```bash
geocodio lists status <list-id> --watch
geocodio lists download <list-id> --output <results-outside-dataset-repo>.csv
```

Spreadsheet column templates use `{{A}}`, `{{B}}`, and so on, not CSV header names. Spreadsheet jobs are asynchronous; do not use coordinates until the completed result is downloaded and checked.

## Accuracy filtering

Every result includes an accuracy score from 0–1.0 (not 0–10). Only accept results with a score ≥ 0.7. If the top result for an address doesn't clear that bar:
- Don't fall back to a lower-accuracy result just to fill the field.
- Ask the user for the latitude/longitude directly rather than silently leaving the row incomplete. Only leave it blank if they don't have it either, and note that in the diff summary.

Geocodio displays coordinates as latitude, longitude. Map `lat` to CSV `latitude` and `lng` to CSV `longitude`; the OpenBreweryDB CSV header stores `longitude` before `latitude`.

## Coverage, rate limits, and cost

On pay-as-you-go accounts:
- **Rate limit**: 1,000 lookups/minute.
- **Cost**: the first 2,500 lookups each day are free. This is not a request cap; excess usage can be billed unless the account has a usage limit. Get explicit user approval before a job could exceed the free allowance.
- **Country coverage**: pay-as-you-go covers the United States, Canada, and Mexico. UK support requires a UK-enabled paid plan. Confirm current plan coverage before any other country.

### If the brewery's country isn't covered by the current plan

Don't treat this as a data-confidence problem — it's a plan limitation, same category as "Geocodio unavailable" (see `SKILL.md` steps 0 and 6). Skip the API call, and ask the user for the latitude/longitude directly. Only leave it blank if they don't have it, noting in the proposed diff that it's **"not geocoded — country not covered on current Geocodio plan."** Still proceed with the rest of the record either way — coordinates aren't required to open a valid PR.

## Troubleshooting

- "batch size exceeds maximum of 10,000": split the input file into smaller chunks.
- "invalid coordinate format" (reverse geocoding only — not used by this skill): expects `lat,lng`, latitude first.
- Use `--debug` to see the full HTTP request/response if a result looks wrong.
