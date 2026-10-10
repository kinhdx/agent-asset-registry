"""`registry validate` checks every manifest; `registry catalog` regenerates CATALOG.md and catalog.json;
`registry catalog --check` fails when the committed catalog is out of date (used in CI)."""
from __future__ import annotations

import argparse
import sys

from registry import catalog
from registry.validate import ROOT, check_all

ASSETS = ROOT / "assets"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="registry")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    c = sub.add_parser("catalog")
    c.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    assets, problems = check_all(ASSETS)
    if args.command == "validate":
        for p in problems:
            print(p)
        print(f"{len(assets)} assets, {len(problems)} problems")
        return 1 if problems else 0
    if problems:
        print("fix validation problems first (registry validate)")
        return 1
    if args.check:
        current = (ROOT / "CATALOG.md").read_text(encoding="utf-8") if (ROOT / "CATALOG.md").exists() else ""
        if current != catalog.render(assets):
            print("CATALOG.md is out of date: run `registry catalog` and commit the result")
            return 1
        print("catalog up to date")
        return 0
    catalog.write(assets, ROOT)
    print(f"wrote CATALOG.md and catalog.json ({len(assets)} assets)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
