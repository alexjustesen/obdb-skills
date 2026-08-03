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

For machine-readable output you can parse programmatically, check `geocodio geocode --help` for the current JSON/agent output flag (the CLI supports human-readable, JSON, and an `--agent` markdown mode) — confirm the exact flag name at run time since it may change between CLI versions, then parse the accuracy score out of that output.

## Batch (use this whenever geocoding more than 10 addresses in one session)

```bash
geocodio geocode --batch addresses.txt
```

or, for a CSV of addresses:

```bash
geocodio lists upload data.csv --direction forward --format "{{address_1}}, {{city}}, {{state_province}}"
```

Batch requests accept up to 10,000 items; if you ever exceed that, split into chunks.

## Accuracy filtering

Every result includes an accuracy score from 0–1.0 (not 0–10). Only accept results with a score ≥ 0.7. If the top result for an address doesn't clear that bar:
- Don't fall back to a lower-accuracy result just to fill the field.
- Ask the user for the latitude/longitude directly rather than silently leaving the row incomplete. Only leave it blank if they don't have it either, and note that in the diff summary.

## Free tier limits

If the account is on Geocodio's free tier:
- **Rate limit**: 1,000 requests/minute, 2,500 requests/day. A single brewery is one request; a batch counts each address in it. If a session's batch would push the day's total past 2,500 (rare for typical single/handful-of-brewery requests, but possible for a large batch add), check remaining quota before firing it off rather than discovering a rate-limit error partway through and leaving some addresses geocoded and others not.
- **Country coverage**: only **United States, Canada, and Mexico** are geocodable on the free tier. Any other country — UK included — requires a paid plan and will fail or return no result on free tier.

### If the brewery's country isn't covered by the current plan

Don't treat this as a data-confidence problem — it's a plan limitation, same category as "Geocodio unavailable" (see `SKILL.md` step 0/7). Skip the API call, and ask the user for the latitude/longitude directly. Only leave it blank if they don't have it, noting in the diff summary that it's **"not geocoded — country not covered on current Geocodio plan."** Still proceed with the rest of the record either way — coordinates aren't required to open a valid PR.

## Troubleshooting

- "batch size exceeds maximum of 10,000": split the input file into smaller chunks.
- "invalid coordinate format" (reverse geocoding only — not used by this skill): expects `lat,lng`, latitude first.
- Use `--debug` to see the full HTTP request/response if a result looks wrong.
