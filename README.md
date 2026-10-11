# agent-asset-registry

A registry of reusable prompts, agents, workflows and tools, where each entry states what it does, who owns
it, how it was measured and how much it can be trusted. The maturity level is not a label someone picks: the
validator checks that the evidence for that level is in the manifest, and CI fails when it is not.

See [CATALOG.md](CATALOG.md) for the current entries.

## Maturity levels

| Level | Meaning | What the validator requires |
|---|---|---|
| experimental | Registered so it can be found; no quality claim | schema: owner, description, models, data classification, source |
| validated | Measured and safe to reuse in a pilot | evaluation with dataset, report, thresholds, every metric meeting its threshold; source pinned to a commit; safeguards; human oversight model |
| production | In use | evaluation on real data; runbook, dashboard, on-call, risk approval; review within 180 days |
| deprecated | Being retired | reason and sunset date; `replaced_by` must point to a registered asset |

The full checklist, including the items a reviewer checks by hand, is in
[docs/definition-of-done.md](docs/definition-of-done.md). How an entry is submitted and reviewed:
[docs/intake.md](docs/intake.md).

## A manifest

```yaml
id: complaint-triage
kind: prompt
maturity: validated
owner: ai-coe
models: [claude-haiku-5-5]
data_classification: confidential
source: {repository: https://github.com/kinhdx/llm-service-starter, path: prompts/triage.md, version: 2b0e8f7}
evaluation:
  dataset_size: 40
  synthetic: true
  metrics:    {category_accuracy: 0.95, fraud_recall: 1.0}
  thresholds: {category_accuracy: {op: ">=", value: 0.85}, fraud_recall: {op: ">=", value: 1.0}}
safeguards: [identifiers redacted before the model call, fraud routing enforced in code]
human_oversight: Fraud and legal-threat complaints are always handled by a person.
```

The schema is [schema/asset.schema.json](schema/asset.schema.json).

## Commands

```bash
uv sync
uv run registry validate          # schema + definition of done for each entry's level
uv run registry catalog           # regenerate CATALOG.md and catalog.json
uv run registry catalog --check   # fail if the committed catalog is stale (CI)
uv run pytest -q
```

CI runs all of these on every pull request and weekly on `main`. The weekly run is what catches a production
entry whose review has lapsed.

## Current entries

Every validated entry points to the repository where it is built and to its evaluation report at a pinned
commit. The three service entries were measured on synthetic data, which is why none of them can be marked
production: the validator rejects `maturity: production` while `evaluation.synthetic` is true.

The three coding-agent entries come from [coding-agent-trial](https://github.com/kinhdx/coding-agent-trial):
the same harness configuration, sandbox and tasks for each. dsh met every threshold but stays experimental,
because the version measured is a release candidate and it runs tools without asking for permission.
