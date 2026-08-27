#!/usr/bin/env python3
"""Compare a normalized external brewery inventory with OBDB source CSVs."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlsplit


NAME_SUFFIXES = re.compile(
    r"\b(?:brewing company|brewing co|brew co|beer company|beer co|brewing|brewery|llc|inc|ltd)\b"
)
SPACE = re.compile(r"\s+")
NON_ALNUM = re.compile(r"[^a-z0-9]+")
FIELD_ALIASES = {
    "id": ("id",),
    "name": ("name", "brewery_name"),
    "website_url": ("website_url", "website", "url"),
    "address_1": ("address_1", "address", "street", "street_address"),
    "address_2": ("address_2",),
    "address_3": ("address_3",),
    "city": ("city", "locality"),
    "state_province": ("state_province", "state", "province", "region"),
    "postal_code": ("postal_code", "postcode", "zip", "zip_code"),
    "country": ("country",),
    "source_url": ("source_url",),
    "source_id": ("source_id",),
}


def text(value: str | None) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(char for char in value if not unicodedata.combining(char))
    return SPACE.sub(" ", NON_ALNUM.sub(" ", value.casefold())).strip()


def name_key(value: str | None) -> str:
    normalized = text(value)
    without_suffixes = SPACE.sub(" ", NAME_SUFFIXES.sub(" ", normalized)).strip()
    return without_suffixes or normalized


def website_key(value: str | None) -> str:
    value = (value or "").strip().casefold()
    if not value:
        return ""
    parsed = urlsplit(value if "://" in value else "//" + value)
    host = (parsed.hostname or "").removeprefix("www.").rstrip(".")
    return host


def first(row: dict[str, str], field: str) -> str:
    lower = {
        str(key).strip().casefold(): value.strip()
        for key, value in row.items()
        if key is not None and isinstance(value, str)
    }
    return next((lower[alias] for alias in FIELD_ALIASES[field] if lower.get(alias)), "")


def normalize_row(row: dict[str, str], source_file: str, row_number: int) -> dict[str, object]:
    raw = {field: first(row, field) for field in FIELD_ALIASES}
    address_parts = [raw[field] for field in ("address_1", "address_2", "address_3") if raw[field]]
    location_parts = [raw[field] for field in ("city", "state_province", "postal_code", "country") if raw[field]]
    return {
        "record": raw,
        "source_file": source_file,
        "row_number": row_number,
        "keys": {
            "name": name_key(raw["name"]),
            "website": website_key(raw["website_url"]),
            "street": text(" ".join(address_parts)),
            "city": text(raw["city"]),
            "region": text(raw["state_province"]),
            "postal_code": text(raw["postal_code"]),
            "country": text(raw["country"]),
            "full_address": text(" ".join(address_parts + location_parts)),
        },
    }


def read_csv(path: Path, label: str) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"CSV has no header: {path}")
        if not any(alias in {field.strip().casefold() for field in reader.fieldnames} for alias in FIELD_ALIASES["name"]):
            raise ValueError(f"CSV has no name column: {path}")
        for row_number, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(f"row {row_number} has more values than the header: {path}")
            if not any(value.strip() for value in row.values() if isinstance(value, str)):
                continue
            normalized = normalize_row(row, label, row_number)
            if normalized["record"]["name"]:  # type: ignore[index]
                records.append(normalized)
    return records


def agreement(left: str, right: str) -> bool:
    return bool(left and right and left == right)


def compare(external: dict[str, object], dataset: dict[str, object]) -> tuple[float, list[str]]:
    left = external["keys"]
    right = dataset["keys"]
    assert isinstance(left, dict) and isinstance(right, dict)
    reasons: list[str] = []
    score = 0.0

    name_similarity = SequenceMatcher(None, str(left["name"]), str(right["name"])).ratio()
    if agreement(str(left["name"]), str(right["name"])):
        score += 0.48
        reasons.append("normalized name exact")
    elif name_similarity >= 0.9:
        score += 0.38
        reasons.append(f"normalized name similar ({name_similarity:.2f})")
    elif name_similarity >= 0.78:
        score += 0.24
        reasons.append(f"normalized name possibly similar ({name_similarity:.2f})")

    if agreement(str(left["website"]), str(right["website"])):
        score += 0.52
        reasons.append("website host exact")
    if left["street"] and agreement(str(left["full_address"]), str(right["full_address"])):
        score += 0.48
        reasons.append("normalized full address exact")
    elif agreement(str(left["street"]), str(right["street"])):
        score += 0.31
        reasons.append("normalized street exact")
    if agreement(str(left["postal_code"]), str(right["postal_code"])):
        score += 0.14
        reasons.append("postal code exact")
    if agreement(str(left["city"]), str(right["city"])):
        score += 0.10
        reasons.append("city exact")
    if agreement(str(left["region"]), str(right["region"])):
        score += 0.08
        reasons.append("state/province exact")
    if agreement(str(left["country"]), str(right["country"])):
        score += 0.04
        reasons.append("country exact")

    # Location-only matches are leads, not identity claims.
    if name_similarity < 0.5 and not agreement(str(left["website"]), str(right["website"])):
        score = min(score, 0.49)
    return min(score, 1.0), reasons


def represents_location(external: dict[str, object], dataset: dict[str, object]) -> bool:
    """Require location evidence before suppressing a reverse-comparison row."""
    left = external["keys"]
    right = dataset["keys"]
    assert isinstance(left, dict) and isinstance(right, dict)
    if left["street"] and agreement(str(left["full_address"]), str(right["full_address"])):
        return True
    if agreement(str(left["street"]), str(right["street"])) and agreement(str(left["city"]), str(right["city"])) and agreement(str(left["region"]), str(right["region"])):
        return True
    return False


def public_record(record: dict[str, object]) -> dict[str, object]:
    return {
        "record": record["record"],
        "source_file": record["source_file"],
        "row_number": record["row_number"],
    }


def confidence(score: float) -> str:
    if score >= 0.85:
        return "high"
    if score >= 0.62:
        return "medium"
    return "low"


def in_reverse_scope(record: dict[str, object], external: list[dict[str, object]], scope_level: str) -> bool:
    """Limit reverse findings without combining unrelated geographic values."""
    keys = record["keys"]
    assert isinstance(keys, dict)
    external_keys = [item["keys"] for item in external]
    countries = {(str(item.get("country", "")),) for item in external_keys if isinstance(item, dict) and item.get("country")}
    regions = {(str(item.get("country", "")), str(item.get("region", ""))) for item in external_keys if isinstance(item, dict) and item.get("region")}
    cities = {(str(item.get("country", "")), str(item.get("region", "")), str(item.get("city", ""))) for item in external_keys if isinstance(item, dict) and item.get("city")}
    current_country = str(keys.get("country", ""))
    current_region = str(keys.get("region", ""))
    current_city = str(keys.get("city", ""))
    if scope_level == "all":
        return True
    if scope_level == "city" or (scope_level == "auto" and len(cities) == 1):
        return (current_country, current_region, current_city) in cities
    if scope_level == "region" or (scope_level == "auto" and regions):
        return (current_country, current_region) in regions
    return not countries or (current_country,) in countries


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare a normalized external inventory with every dataset data/**/*.csv file; emit JSON to stdout."
    )
    parser.add_argument("inventory_csv", type=Path, help="Normalized external inventory CSV")
    parser.add_argument("dataset_root", type=Path, help="Root of the Open Brewery DB dataset checkout")
    parser.add_argument(
        "--candidate-threshold",
        type=float,
        default=0.35,
        help="Minimum score for a possible match (default: 0.35)",
    )
    parser.add_argument(
        "--reverse-threshold",
        type=float,
        default=0.62,
        help="Score at which a dataset record counts as represented externally (default: 0.62)",
    )
    parser.add_argument("--max-matches", type=int, default=5, help="Maximum candidate matches per external record (default: 5)")
    parser.add_argument("--reverse-scope", choices=("auto", "city", "region", "country", "all"), default="auto", help="Geographic scope for reverse results (default: auto)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not 0 <= args.candidate_threshold <= 1 or not 0 <= args.reverse_threshold <= 1:
        raise ValueError("thresholds must be between 0 and 1")
    if args.max_matches < 1:
        raise ValueError("--max-matches must be at least 1")

    inventory_path = args.inventory_csv.expanduser().resolve()
    dataset_root = args.dataset_root.expanduser().resolve()
    data_root = dataset_root / "data"
    if not inventory_path.is_file():
        raise ValueError(f"inventory CSV not found: {inventory_path}")
    if not data_root.is_dir():
        raise ValueError(f"dataset data directory not found: {data_root}")

    source_paths = sorted(path for path in data_root.rglob("*.csv") if path.is_file())
    if not source_paths:
        raise ValueError(f"no source CSVs found under: {data_root}")

    external = read_csv(inventory_path, str(inventory_path))
    if not external:
        raise ValueError(f"inventory CSV has no brewery records: {inventory_path}")
    dataset: list[dict[str, object]] = []
    for path in source_paths:
        dataset.extend(read_csv(path, str(path.relative_to(dataset_root))))

    represented_dataset_indexes: set[int] = set()
    external_candidates: list[dict[str, object]] = []
    for external_record in external:
        matches: list[tuple[float, list[str], int]] = []
        for index, dataset_record in enumerate(dataset):
            score, reasons = compare(external_record, dataset_record)
            if score >= args.reverse_threshold and represents_location(external_record, dataset_record):
                represented_dataset_indexes.add(index)
            if score >= args.candidate_threshold:
                matches.append((score, reasons, index))
        matches.sort(key=lambda item: item[0], reverse=True)
        top_score = matches[0][0] if matches else 0.0
        top_represents = bool(matches and represents_location(external_record, dataset[matches[0][2]]))
        classification = "likely_match" if top_score >= 0.85 and top_represents else "possible_match" if matches else "unmatched_external"
        external_candidates.append(
            {
                "external": public_record(external_record),
                "classification": classification,
                "top_confidence": confidence(top_score) if matches else "none",
                "matches": [
                    {
                        "score": round(score, 4),
                        "confidence": confidence(score),
                        "reasons": reasons,
                        "dataset": public_record(dataset[index]),
                    }
                    for score, reasons, index in matches[: args.max_matches]
                ],
            }
        )

    reverse_unmatched = [
        public_record(record)
        for index, record in enumerate(dataset)
        if index not in represented_dataset_indexes and in_reverse_scope(record, external, args.reverse_scope)
    ]
    result = {
        "meta": {
            "inventory_csv": str(inventory_path),
            "dataset_root": str(dataset_root),
            "source_csv_count": len(source_paths),
            "external_record_count": len(external),
            "dataset_record_count": len(dataset),
            "candidate_threshold": args.candidate_threshold,
            "reverse_threshold": args.reverse_threshold,
            "reverse_scope": args.reverse_scope,
            "notes": [
                "Scores are triage signals, not identity or eligibility decisions.",
                "Reverse unmatched records may reflect external-source scope and are not deletion recommendations.",
                "Reverse results use exact country/region/city tuples and the selected reverse scope.",
            ],
        },
        "external_candidates": external_candidates,
        "reverse_unmatched_dataset_records": reverse_unmatched,
    }
    json.dump(result, sys.stdout, ensure_ascii=True, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, csv.Error, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
