#!/usr/bin/env python3
"""Select complete GeoIPList/GeoSiteList entries without rewriting their payloads.

Both formats store categories as repeated field 1 messages, whose field 1 is
the category code. Keeping the original encoded message preserves domain rule
types, attributes, CIDRs, reverse_match and unknown protobuf fields.
"""

import argparse
import os
from pathlib import Path
import re
import tempfile


def varint(data, offset):
    value = 0
    for shift in range(0, 70, 7):
        if offset >= len(data):
            raise ValueError("truncated protobuf varint")
        byte = data[offset]
        offset += 1
        if shift == 63 and byte > 1:
            raise ValueError("protobuf varint exceeds 64 bits")
        value |= (byte & 0x7f) << shift
        if byte < 0x80:
            return value, offset
    raise ValueError("invalid protobuf varint")


def fields(data):
    offset = 0
    while offset < len(data):
        start = offset
        tag, offset = varint(data, offset)
        number, wire = tag >> 3, tag & 7
        if not 0 < number < 2**29:
            raise ValueError("invalid protobuf field number")
        payload_start = offset
        if wire == 0:
            _, end = varint(data, offset)
        elif wire in (1, 5):
            end = offset + (8 if wire == 1 else 4)
        elif wire == 2:
            length, payload_start = varint(data, offset)
            end = payload_start + length
        else:
            raise ValueError(f"unsupported protobuf wire type {wire}")
        if end > len(data):
            raise ValueError("truncated protobuf field")
        yield number, wire, data[payload_start:end], data[start:end]
        offset = end


def category_code(entry):
    code = None
    for number, wire, value, _ in fields(entry):
        if number == 1:
            if wire != 2 or code is not None:
                raise ValueError("invalid or repeated category code")
            code = bytes(value).decode("utf-8").lower()
    if not code:
        raise ValueError("category has no code")
    return code


def select(source, requested):
    selected, seen, found = [], set(), set()
    for number, wire, payload, encoded in fields(memoryview(source)):
        if number != 1:
            selected.append(encoded)
            continue
        if wire != 2:
            raise ValueError("category entry is not a protobuf message")
        code = category_code(payload)
        if code in seen:
            raise ValueError(f"duplicate category in source: {code}")
        seen.add(code)
        if code in requested:
            selected.append(encoded)
            found.add(code)
    missing = requested - found
    if missing:
        raise ValueError("missing required categories: " + ", ".join(sorted(missing)))
    return selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--categories", required=True, type=Path)
    args = parser.parse_args()
    paths = [p.resolve() for p in (args.source, args.output, args.categories)]
    if len(set(paths)) != len(paths):
        parser.error("source, output and category list must be different files")

    requested = set()
    for number, line in enumerate(args.categories.read_text(encoding="utf-8").splitlines(), 1):
        code = line.strip().lower()
        if not code or code.startswith("#"):
            continue
        if not re.fullmatch(r"[a-z0-9][a-z0-9_.!-]*", code):
            parser.error(f"{args.categories}:{number}: expected a category name without a prefix or attributes")
        if code in requested:
            parser.error(f"{args.categories}:{number}: duplicate category {code}")
        requested.add(code)
    if not requested:
        parser.error("category list is empty")

    try:
        source = args.source.read_bytes()
        selected = select(source, requested)
    except (OSError, ValueError) as error:
        parser.exit(1, f"{args.source}: {error}\n")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=args.output.parent, prefix=args.output.name + ".", delete=False) as output:
            temporary = Path(output.name)
            for entry in selected:
                output.write(entry)
        os.replace(temporary, args.output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    size = args.output.stat().st_size
    print(f"{args.output}: {len(requested)} categories, {size} bytes (source: {len(source)} bytes)")


if __name__ == "__main__":
    main()
