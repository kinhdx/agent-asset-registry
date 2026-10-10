# Catalog

Generated from `assets/*/asset.yaml` by `registry catalog`. Do not edit by hand.

| Asset | Kind | Maturity | Owner | Models | Data | Key metrics |
|---|---|---|---|---|---|---|
| [Customer complaint triage](assets/complaint-triage/asset.yaml) | prompt | validated | ai-coe | claude-haiku-5-5 | confidential | category_accuracy 0.95, urgency_accuracy 0.775, fraud_recall 1 (synthetic) |
| [Loan dossier extraction and gating](assets/loan-dossier-extraction/asset.yaml) | workflow | validated | ai-coe | claude-haiku-5-5, claude-sonnet-5-5 | confidential | decision_accuracy_standard_pct 100, decision_accuracy_stress_pct 70, defect_recall_pct 100 (synthetic) |
| [Loan product policy question answering](assets/loan-policy-qa/asset.yaml) | workflow | validated | ai-coe | claude-haiku-5-5 | internal | hit_at_1_pct 93.3, hit_at_4_pct 100, key_fact_accuracy_pct 100 (synthetic) |
| [Vietnamese identifier redaction](assets/vn-pii-redactor/asset.yaml) | tool | experimental | ai-coe | none | confidential | - |

Totals: production 0, validated 3, experimental 1, deprecated 0
