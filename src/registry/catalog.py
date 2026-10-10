"""Renders the registry as CATALOG.md (for people) and catalog.json (for tools and dashboards)."""
from __future__ import annotations

import json
from pathlib import Path

ORDER = {"production": 0, "validated": 1, "experimental": 2, "deprecated": 3}


def render(assets: list[dict]) -> str:
    rows = sorted(assets, key=lambda a: (ORDER[a["maturity"]], a["id"]))
    lines = ["# Catalog", "", "Generated from `assets/*/asset.yaml` by `registry catalog`. Do not edit by hand.", "",
             "| Asset | Kind | Maturity | Owner | Models | Data | Key metrics |", "|---|---|---|---|---|---|---|"]
    for a in rows:
        metrics = ", ".join(f"{k} {v:g}" for k, v in list((a.get("evaluation") or {}).get("metrics", {}).items())[:3])
        synthetic = " (synthetic)" if (a.get("evaluation") or {}).get("synthetic") else ""
        lines.append(f"| [{a['name']}](assets/{a['id']}/asset.yaml) | {a['kind']} | {a['maturity']} | {a['owner']} "
                     f"| {', '.join(a['models'])} | {a['data_classification']} | {metrics or '-'}{synthetic if metrics else ''} |")
    counts = {level: sum(a["maturity"] == level for a in assets) for level in ORDER}
    lines += ["", "Totals: " + ", ".join(f"{level} {n}" for level, n in counts.items())]
    return "\n".join(lines) + "\n"


def render_json(assets: list[dict]) -> str:
    return json.dumps(sorted(assets, key=lambda a: a["id"]), ensure_ascii=False, indent=1, default=str)


def write(assets: list[dict], root: Path) -> None:
    (root / "CATALOG.md").write_text(render(assets), encoding="utf-8", newline="\n")
    (root / "catalog.json").write_text(render_json(assets), encoding="utf-8", newline="\n")


def stale(assets: list[dict], root: Path) -> list[str]:
    """Names of the committed catalog files that differ from what the manifests would generate."""
    def read(name: str) -> str:
        path = root / name
        return path.read_text(encoding="utf-8") if path.exists() else ""
    out = []
    if read("CATALOG.md") != render(assets):
        out.append("CATALOG.md")
    try:
        if json.loads(read("catalog.json") or "null") != json.loads(render_json(assets)):
            out.append("catalog.json")
    except json.JSONDecodeError:
        out.append("catalog.json")
    return out
