#!/usr/bin/env python3
"""Copy requested domain lists and their recursive includes for the generator."""

import argparse
from pathlib import Path
import re
import shutil

NAME = re.compile(r"[a-z0-9][a-z0-9_.!-]*\Z")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("categories", type=Path)
    parser.add_argument("community", type=Path)
    parser.add_argument("additional", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    requested = []
    for raw in args.categories.read_text(encoding="utf-8").splitlines():
        name = raw.strip().lower()
        if name and not name.startswith("#"):
            if not NAME.fullmatch(name) or name in requested:
                parser.error(f"invalid or duplicate category: {name}")
            requested.append(name)
    if not requested:
        parser.error("category list is empty")

    args.output.mkdir(parents=True, exist_ok=False)
    pending, seen = requested[:], set()
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        seen.add(name)
        source = args.additional / name
        if not source.is_file():
            source = args.community / name
        if not source.is_file():
            parser.error(f"missing domain list: {name}")
        for line in source.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if line.startswith("include:"):
                dependency = line[len("include:"):].split("@", 1)[0].strip().lower()
                if not NAME.fullmatch(dependency):
                    parser.error(f"invalid include in {source}: {dependency}")
                pending.append(dependency)
        shutil.copyfile(source, args.output / name)
    print(f"Prepared {len(seen)} domain lists for {len(requested)} categories")


if __name__ == "__main__":
    main()
