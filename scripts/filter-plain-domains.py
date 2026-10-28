#!/usr/bin/env python3
"""Reject whitespace inside records from a one-domain-per-line source.

This is not a parser for domain-list-community rules: those may legitimately
contain attributes or regular expressions. Apply it only to the raw domain feed.
"""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--rejected", required=True, type=Path)
    args = parser.parse_args()
    paths = [path.resolve() for path in (args.source, args.output, args.rejected)]
    if len(set(paths)) != len(paths):
        parser.error("source, output and rejected report must be different files")

    args.rejected.parent.mkdir(parents=True, exist_ok=True)
    kept = rejected = 0
    with (
        args.source.open(encoding="utf-8") as source,
        args.output.open("w", encoding="utf-8") as output,
        args.rejected.open("w", encoding="utf-8") as report,
    ):
        for number, raw in enumerate(source, 1):
            record = raw.strip()
            if not record or record.startswith("#"):
                continue
            if any(char.isspace() for char in record):
                rejected += 1
                report.write(json.dumps({
                    "source": str(args.source),
                    "line": number,
                    "reason": "whitespace inside domain record",
                    "record": raw.rstrip("\r\n"),
                }) + "\n")
                print(f"::warning::{args.source}:{number}: rejected domain record "
                      f"containing whitespace; see {args.rejected}")
                continue
            output.write(record + "\n")
            kept += 1

    print(f"{args.source}: kept {kept} records, rejected {rejected}")
    if kept == 0:
        raise SystemExit("No domain records remain; refusing to build an empty list")


if __name__ == "__main__":
    main()
