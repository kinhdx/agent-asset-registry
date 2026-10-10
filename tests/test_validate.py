from __future__ import annotations

import copy
from datetime import date
from pathlib import Path

import pytest

from registry.catalog import render
from registry.validate import check, check_all, load

ASSETS = Path(__file__).resolve().parents[1] / "assets"
TODAY = date(2026, 10, 10)


@pytest.fixture
def validated():
    return load(ASSETS / "complaint-triage" / "asset.yaml")


def codes(problems):
    return [p.message for p in problems]


def test_registered_assets_are_valid():
    assets, problems = check_all(ASSETS, TODAY)
    assert problems == []
    assert {a["maturity"] for a in assets} >= {"validated", "experimental"}


def test_schema_errors_are_reported_with_location(validated):
    validated["kind"] = "chatbot"
    assert any("kind" in m for m in codes(check(validated, TODAY)))


def test_validated_requires_metrics_to_meet_thresholds(validated):
    validated["evaluation"]["metrics"]["fraud_recall"] = 0.9
    assert any("fraud_recall = 0.9 does not meet >= 1.0" in m for m in codes(check(validated, TODAY)))


def test_validated_requires_a_measured_value_for_every_threshold(validated):
    del validated["evaluation"]["metrics"]["urgency_accuracy"]
    assert any("no measured value" in m for m in codes(check(validated, TODAY)))


def test_validated_requires_pinned_version_safeguards_and_oversight(validated):
    del validated["source"]["version"], validated["safeguards"], validated["human_oversight"]
    messages = " ".join(codes(check(validated, TODAY)))
    assert "pinned source version" in messages and "safeguards" in messages and "human oversight" in messages


def test_production_requires_operations_real_data_and_recent_review(validated):
    asset = copy.deepcopy(validated)
    asset["maturity"] = "production"
    messages = " ".join(codes(check(asset, TODAY)))
    assert "operations.runbook" in messages and "real data" in messages

    asset["operations"] = {"runbook": "x", "dashboard": "x", "on_call": "x", "risk_approval": "x",
                           "last_review": "2026-01-02"}
    asset["evaluation"]["synthetic"] = False
    assert codes(check(asset, TODAY)) == ["last review was 281 days ago (limit 180)"]
    asset["operations"]["last_review"] = "2026-09-01"
    assert check(asset, TODAY) == []


def test_experimental_needs_only_the_schema():
    asset = load(ASSETS / "vn-pii-redactor" / "asset.yaml")
    assert "evaluation" not in asset
    assert check(asset, TODAY) == []


def test_deprecated_requires_reason_and_sunset(validated):
    validated["maturity"] = "deprecated"
    validated["deprecation"] = {"reason": "replaced by a fine-tuned classifier"}
    assert any("sunset" in m for m in codes(check(validated, TODAY)))


def test_catalog_lists_every_asset_and_marks_synthetic_evaluations():
    assets, _ = check_all(ASSETS, TODAY)
    text = render(assets)
    for a in assets:
        assert f"assets/{a['id']}/asset.yaml" in text
    assert "(synthetic)" in text
