"""Checks an asset manifest against the schema and the definition of done for its maturity level.

Levels are cumulative: a production asset must also meet everything required of a validated one.

experimental  schema only; anyone can register an idea so it is visible and not built twice
validated     an evaluation with a dataset, a report and thresholds, every metric meeting its threshold;
              a pinned source version; listed safeguards and the human oversight model
production    operations: runbook, dashboard, on-call, risk approval, and a review within REVIEW_DAYS;
              an evaluation run on real (not synthetic) data
deprecated    a reason and a sunset date
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "schema" / "asset.schema.json").read_text(encoding="utf-8"))
REVIEW_DAYS = 180
LEVELS = ["experimental", "validated", "production"]
# Without a format checker, "format": "date" is only an annotation and "soon" would pass.
VALIDATOR = jsonschema.Draft202012Validator(SCHEMA, format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER)


@dataclass
class Problem:
    asset: str
    message: str

    def __str__(self) -> str:
        return f"{self.asset}: {self.message}"


def _dates_to_text(value):
    """YAML reads 2026-10-10 as a date object; the schema and the catalog expect ISO text."""
    if isinstance(value, dict):
        return {k: _dates_to_text(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_dates_to_text(v) for v in value]
    return value.isoformat() if isinstance(value, date) else value


def load(path: Path) -> dict:
    return _dates_to_text(yaml.safe_load(path.read_text(encoding="utf-8")))


def check(asset: dict, today: date | None = None, name: str = "") -> list[Problem]:
    today = today or date.today()
    who = asset.get("id") or name
    problems = [Problem(who, f"schema: {e.message} at {'/'.join(map(str, e.path)) or 'top level'}")
                for e in VALIDATOR.iter_errors(asset)]
    if problems:
        return problems
    level = asset["maturity"]
    if level == "deprecated":
        if not asset.get("deprecation"):
            problems.append(Problem(who, "deprecated requires a deprecation block with a reason and a sunset date"))
        return problems
    rank = LEVELS.index(level)
    if rank >= 1:
        problems += _validated(asset, who)
    if rank >= 2:
        problems += _production(asset, who, today)
    return problems


def _validated(asset: dict, who: str) -> list[Problem]:
    out = []
    ev = asset.get("evaluation")
    if not ev:
        return [Problem(who, "validated requires an evaluation")]
    for metric, rule in ev["thresholds"].items():
        value = ev["metrics"].get(metric)
        if value is None:
            out.append(Problem(who, f"threshold on {metric} but no measured value"))
        elif rule["op"] == ">=" and value < rule["value"] or rule["op"] == "<=" and value > rule["value"]:
            out.append(Problem(who, f"{metric} = {value} does not meet {rule['op']} {rule['value']}"))
    if not ev["thresholds"]:
        out.append(Problem(who, "evaluation has no thresholds"))
    if not asset["source"].get("version"):
        out.append(Problem(who, "validated requires a pinned source version (commit or tag)"))
    if not asset.get("safeguards"):
        out.append(Problem(who, "validated requires the safeguards to be listed"))
    if not asset.get("human_oversight"):
        out.append(Problem(who, "validated requires the human oversight model to be described"))
    return out


def _production(asset: dict, who: str, today: date) -> list[Problem]:
    out = []
    ops = asset.get("operations", {})
    for key in ("runbook", "dashboard", "on_call", "risk_approval", "last_review"):
        if not ops.get(key):
            out.append(Problem(who, f"production requires operations.{key}"))
    if ops.get("last_review"):
        age = (today - date.fromisoformat(ops["last_review"])).days
        if age > REVIEW_DAYS:
            out.append(Problem(who, f"last review was {age} days ago (limit {REVIEW_DAYS})"))
    if (asset.get("evaluation") or {}).get("synthetic", True):
        out.append(Problem(who, "production requires an evaluation on real data (evaluation.synthetic: false)"))
    return out


def check_all(folder: Path, today: date | None = None) -> tuple[list[dict], list[Problem]]:
    assets, problems, seen = [], [], set()
    for path in sorted(folder.glob("*/asset.yaml")):
        asset = load(path)
        problems += check(asset, today, path.parent.name)
        if asset.get("id") != path.parent.name:
            problems.append(Problem(path.parent.name, f"folder name must equal id ({asset.get('id')})"))
        if asset.get("id") in seen:
            problems.append(Problem(asset["id"], "duplicate id"))
        seen.add(asset.get("id"))
        assets.append(asset)
    ids = {a.get("id") for a in assets}
    for a in assets:
        replaced = (a.get("deprecation") or {}).get("replaced_by")
        if replaced and replaced not in ids:
            problems.append(Problem(a["id"], f"replaced_by points to unknown asset {replaced}"))
    return assets, problems
