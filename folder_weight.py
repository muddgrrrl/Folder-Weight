#!/usr/bin/env python3
"""Show which immediate children account for a folder's apparent size."""
import argparse
import json
import os
from pathlib import Path
import stat
import sys


def size_tree(start, errors):
    total = 0
    pending = [start]
    while pending:
        path = pending.pop()
        try:
            mode = path.lstat()
            if stat.S_ISREG(mode.st_mode):
                total += mode.st_size
            elif stat.S_ISDIR(mode.st_mode):
                with os.scandir(path) as entries:
                    pending.extend(Path(entry.path) for entry in entries)
        except OSError as error:
            errors.append(str(error))
    return total


def human(count):
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    number = float(count)
    for unit in units:
        if number < 1024 or unit == units[-1]:
            return f"{int(number)} B" if unit == "B" else f"{number:.1f} {unit}"
        number /= 1024


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, nargs="?", default=Path.cwd())
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.top < 1:
        parser.error("--top must be positive")
    errors = []
    try:
        items = sorted(((child.name, size_tree(child, errors)) for child in args.directory.iterdir()),
                       key=lambda item: (-item[1], item[0]))
    except OSError as error:
        parser.error(str(error))
    total = sum(size for _, size in items)
    if args.json:
        print(json.dumps({"total_bytes": total, "entries": [
            {"name": name, "bytes": size} for name, size in items[:args.top]
        ], "errors": errors}, indent=2))
    else:
        print(f"Total: {human(total)}")
        for name, size in items[:args.top]:
            width = round(20 * size / total) if total else 0
            print(f"{human(size):>11}  {'█' * width:<20}  {name!r}")
        if errors:
            print(f"{len(errors)} paths could not be read; totals are partial.", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
