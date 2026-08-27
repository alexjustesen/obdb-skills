#!/usr/bin/env python3
"""Read-only, deterministic audits for OpenBreweryDB source CSV files."""

import argparse
import csv
import json
import re
import sys
import uuid
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlsplit


MODES = ("structural", "identity", "completeness", "geospatial", "status")
REQUIRED_COLUMNS = ("id", "name", "brewery_type", "city", "state_province", "postal_code", "country")
REQUIRED_VALUES = ("name", "brewery_type", "city", "state_province", "postal_code", "country")
LOCATION_FIELDS = ("address_1", "city", "state_province", "postal_code", "country")
SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}
FALLBACK_BREWERY_TYPES = {
    "alt prop", "bar", "beer brand", "brewpub", "cidery", "closed", "contract",
    "large", "location", "micro", "nano", "office only location", "planning",
    "proprietor", "regional", "taproom", "beergarden",
}


def normalized(value):
    return re.sub(r"[^a-z0-9]+", "", (value or "").casefold())


def finding(check, message, file="", row=None, record_id="", severity="warning", confidence="medium"):
    return {
        "check": check,
        "severity": severity,
        "confidence": confidence,
        "file": file,
        "row": row,
        "id": record_id or "",
        "message": message,
    }


def read_sources(root):
    data_root = root / "data"
    paths = sorted(path for path in data_root.rglob("*.csv") if path.is_file()) if data_root.is_dir() else []
    files = []
    read_findings = []
    for path in paths:
        relative = path.relative_to(root).as_posix()
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.reader(handle, strict=True)
                rows = list(reader)
        except (OSError, UnicodeError, csv.Error) as exc:
            read_findings.append(finding("csv_read_error", str(exc), relative, severity="error", confidence="high"))
            continue
        header = rows[0] if rows else []
        records = []
        for physical_row, values in enumerate(rows[1:], start=2):
            if not values or not any(value.strip() for value in values):
                continue
            record = {column: values[index].strip() if index < len(values) else "" for index, column in enumerate(header)}
            records.append((physical_row, values, record))
        files.append({"path": relative, "header": header, "records": records})
    return paths, files, read_findings


def read_brewery_types(root):
    """Read the live string enum without importing or executing upstream code."""
    config_path = root / "src" / "config.ts"
    try:
        config = config_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return FALLBACK_BREWERY_TYPES, "fallback snapshot"
    match = re.search(r"BREWERY_TYPES\s*=\s*\[(.*?)\]", config, re.DOTALL)
    if not match:
        return FALLBACK_BREWERY_TYPES, "fallback snapshot"
    values = set(re.findall(r'["\']([^"\']+)["\']', match.group(1)))
    return (values, "src/config.ts") if values else (FALLBACK_BREWERY_TYPES, "fallback snapshot")


def structural_findings(files, read_findings, brewery_types, brewery_types_source):
    results = list(read_findings)
    live_types = brewery_types_source == "src/config.ts"
    if not live_types:
        results.append(finding("brewery_type_source_unavailable", "Could not parse src/config.ts; type checks use the bundled snapshot and require confirmation.", severity="warning", confidence="high"))
    headers = Counter(tuple(item["header"]) for item in files if item["header"])
    modal_header = min(headers, key=lambda value: (-headers[value], value)) if headers else ()
    seen_ids = defaultdict(list)
    for item in files:
        path = item["path"]
        header = item["header"]
        if not header:
            results.append(finding("missing_header", "File is empty or has no header.", path, severity="error", confidence="high"))
            continue
        if tuple(header) != modal_header:
            results.append(finding("header_inconsistency", "Header differs from the most common source header.", path, row=1, severity="warning", confidence="high"))
        missing = [column for column in REQUIRED_COLUMNS if column not in header]
        if missing:
            results.append(finding("missing_required_columns", "Missing columns: " + ", ".join(missing), path, row=1, severity="error", confidence="high"))
        for row_number, values, record in item["records"]:
            record_id = record.get("id", "")
            if len(values) != len(header):
                results.append(finding("column_count_mismatch", f"Row has {len(values)} values for {len(header)} columns.", path, row_number, record_id, "error", "high"))
            if "id" in header and not record_id:
                results.append(finding("blank_id", "Existing source row has a blank ID; confirm whether it is a pending contribution.", path, row_number, severity="warning", confidence="medium"))
            elif record_id:
                try:
                    uuid.UUID(record_id)
                except ValueError:
                    results.append(finding("invalid_id", "Non-blank ID is not a valid UUID.", path, row_number, record_id, "error", "high"))
            brewery_type = record.get("brewery_type", "")
            if brewery_type and brewery_type not in brewery_types:
                source_label = "live allowed set" if live_types else "bundled type snapshot"
                severity, confidence = ("error", "high") if live_types else ("warning", "medium")
                results.append(finding("invalid_brewery_type", f"Type '{brewery_type}' is not in the {source_label}.", path, row_number, record_id, severity, confidence))
            website = record.get("website_url", "")
            if website:
                parsed = urlsplit(website)
                if not parsed.scheme or (parsed.scheme in {"http", "https"} and not parsed.netloc):
                    results.append(finding("invalid_website_url", "Non-blank website_url is not an absolute URL.", path, row_number, record_id, "error", "high"))
            if record_id:
                seen_ids[record_id].append((path, row_number))
        names = [normalized(record.get("name")) for _row, _values, record in item["records"]]
        if names != sorted(names):
            results.append(finding("name_sort_order", "Rows are not alphabetically ordered by normalized name.", path, severity="warning", confidence="high"))
    for record_id, locations in sorted(seen_ids.items()):
        if len(locations) > 1:
            location_text = ", ".join(f"{path}:{row}" for path, row in locations)
            for path, row in locations:
                results.append(finding("duplicate_id", f"ID also occurs at: {location_text}.", path, row, record_id, "error", "high"))
    return results


def identity_findings(files):
    groups = defaultdict(list)
    seen_ids = defaultdict(list)
    for item in files:
        for row_number, _values, record in item["records"]:
            record_id = record.get("id", "")
            if record_id:
                seen_ids[record_id].append((item["path"], row_number))
            name = normalized(record.get("name"))
            location = tuple(normalized(record.get(field)) for field in LOCATION_FIELDS)
            if name and sum(bool(value) for value in location) >= 2:
                groups[(name, location)].append((item["path"], row_number, record_id))
    results = []
    for record_id, locations in sorted(seen_ids.items()):
        if len(locations) > 1:
            location_text = ", ".join(f"{path}:{row}" for path, row in locations)
            for path, row in locations:
                results.append(finding("duplicate_id", f"ID also occurs at: {location_text}.", path, row, record_id, "error", "high"))
    for _key, locations in sorted(groups.items()):
        if len(locations) > 1:
            location_text = ", ".join(f"{path}:{row}" for path, row, _record_id in locations)
            for path, row, record_id in locations:
                results.append(finding("duplicate_identity", f"Normalized name and location signals also occur at: {location_text}.", path, row, record_id, "warning", "medium"))
    return results


def completeness_findings(files):
    results = []
    for item in files:
        for row_number, _values, record in item["records"]:
            for column in REQUIRED_VALUES:
                if column in item["header"] and not record.get(column, ""):
                    results.append(finding("missing_required_value", f"Required field '{column}' is blank.", item["path"], row_number, record.get("id", ""), "warning", "high"))
            for column, minimum in (("city", 2), ("state_province", 2), ("postal_code", 3), ("country", 2)):
                value = record.get(column, "")
                if value and len(value) < minimum:
                    results.append(finding("required_value_too_short", f"Field '{column}' has fewer than {minimum} characters.", item["path"], row_number, record.get("id", ""), "error", "high"))
    return results


def geospatial_findings(files):
    results = []
    for item in files:
        for row_number, _values, record in item["records"]:
            latitude = record.get("latitude", "")
            longitude = record.get("longitude", "")
            record_id = record.get("id", "")
            if bool(latitude) != bool(longitude):
                results.append(finding("coordinate_pair_missing", "Latitude and longitude must be populated together.", item["path"], row_number, record_id, "warning", "high"))
                continue
            if not latitude:
                continue
            try:
                lat_value = float(latitude)
                lon_value = float(longitude)
            except ValueError:
                results.append(finding("coordinate_not_numeric", f"Coordinates are not numeric: ({latitude}, {longitude}).", item["path"], row_number, record_id, "error", "high"))
                continue
            if not -90 <= lat_value <= 90 or not -180 <= lon_value <= 180:
                results.append(finding("coordinate_out_of_range", f"Coordinates are outside valid ranges: ({latitude}, {longitude}).", item["path"], row_number, record_id, "error", "high"))
                if abs(lat_value) > 90 and abs(lat_value) <= 180 and abs(lon_value) <= 90:
                    results.append(finding("coordinate_possible_swap", "Coordinates become range-valid if latitude and longitude are swapped; verify against the stated location.", item["path"], row_number, record_id, "warning", "medium"))
            if lat_value == 0 or lon_value == 0:
                results.append(finding("coordinate_zero", f"Coordinate contains zero: ({latitude}, {longitude}).", item["path"], row_number, record_id, "warning", "medium"))
    return results


def status_findings(files):
    results = []
    for item in files:
        for row_number, _values, record in item["records"]:
            brewery_type = record.get("brewery_type", "").casefold()
            if brewery_type in {"closed", "planning"}:
                results.append(finding("status_verification", f"'{brewery_type}' status requires current external verification.", item["path"], row_number, record.get("id", ""), "info", "low"))
    return results


def completeness_summary(files):
    dataset = defaultdict(lambda: {"populated": 0, "blank": 0})
    per_file = []
    for item in files:
        columns = {column: {"populated": 0, "blank": 0} for column in item["header"]}
        for _row_number, _values, record in item["records"]:
            for column in item["header"]:
                key = "populated" if record.get(column, "") else "blank"
                columns[column][key] += 1
                dataset[column][key] += 1
        per_file.append({"file": item["path"], "rows": len(item["records"]), "columns": columns})
    return {"dataset": dict(sorted(dataset.items())), "files": per_file}


def sort_findings(results):
    unique = {tuple(item.items()): item for item in results}
    return sorted(unique.values(), key=lambda item: (item["file"], item["row"] if item["row"] is not None else 0, SEVERITY_ORDER[item["severity"]], item["check"], item["id"], item["message"]))


def markdown_report(report):
    lines = ["# OpenBreweryDB data quality audit", "", "## Scope", "", f"- Dataset root: `{report['dataset_root']}`", f"- Modes: `{', '.join(report['modes'])}`", f"- Source files: {report['source_file_count']}", f"- Source rows: {report['source_row_count']}", "- Mutation policy: read-only; output written to stdout", "", "## Findings", ""]
    if report["findings"]:
        lines.extend(["| Severity | Confidence | File | Row | ID | Check | Evidence |", "|---|---|---|---:|---|---|---|"])
        for item in report["findings"]:
            values = [item["severity"], item["confidence"], item["file"] or "(dataset)", str(item["row"] or ""), item["id"] or "(blank)", item["check"], item["message"]]
            lines.append("| " + " | ".join(value.replace("|", "\\|").replace("\n", " ") for value in values) + " |")
    else:
        lines.append("No findings for the selected modes.")
    if "completeness" in report["modes"]:
        lines.extend(["", "## Completeness summary", "", "| Field | Populated | Blank |", "|---|---:|---:|"])
        for column, counts in report["completeness"]["dataset"].items():
            lines.append(f"| {column} | {counts['populated']} | {counts['blank']} |")
    lines.extend(["", "## Related open issues and PRs", "", "Not checked by this offline helper. Search open issues and PRs by ID, brewery name, source file, and check before filing.", "", "## Audit safety", "", "This report was generated read-only. No dataset files were changed, no npm command was run, and no upstream implementation was invoked."])
    return "\n".join(lines) + "\n"


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Read-only audit of OpenBreweryDB data/**/*.csv source files.")
    parser.add_argument("dataset_root", type=Path, help="Path to the OpenBreweryDB dataset repository")
    parser.add_argument("--mode", action="append", choices=MODES, help="Audit mode; repeat for multiple modes (default: all)")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format (default: markdown)")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    root = args.dataset_root.expanduser().resolve()
    modes = list(dict.fromkeys(args.mode or MODES))
    paths, files, read_findings = read_sources(root)
    if not (root / "data").is_dir():
        print(f"error: dataset root has no data directory: {root}", file=sys.stderr)
        return 2
    if not paths:
        print(f"error: no source CSV files found under: {root / 'data'}", file=sys.stderr)
        return 2
    brewery_types, brewery_types_source = read_brewery_types(root)
    selected = []
    if "structural" in modes:
        selected.extend(structural_findings(files, read_findings, brewery_types, brewery_types_source))
    elif read_findings:
        selected.extend(read_findings)
    if "identity" in modes:
        selected.extend(identity_findings(files))
    if "completeness" in modes:
        selected.extend(completeness_findings(files))
    if "geospatial" in modes:
        selected.extend(geospatial_findings(files))
    if "status" in modes:
        selected.extend(status_findings(files))
    report = {
        "dataset_root": str(root),
        "modes": modes,
        "source_file_count": len(paths),
        "source_row_count": sum(len(item["records"]) for item in files),
        "brewery_types_source": brewery_types_source,
        "findings": sort_findings(selected),
        "completeness": completeness_summary(files),
    }
    if args.format == "json":
        json.dump(report, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(markdown_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
