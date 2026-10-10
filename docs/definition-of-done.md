# Definition of done per maturity level

Levels are cumulative. The validator (`registry validate`) checks every item marked (auto); reviewers check the
rest during intake.

## experimental

Registered so others can find it and nobody builds it twice. Nothing is promised about quality.

- [ ] Manifest passes the schema: id, name, kind, owner, description, models, data classification, source (auto)
- [ ] Owner is a team, not a person who might move on
- [ ] Known limitations listed

## validated

Measured on a dataset and safe to reuse in a pilot.

- [ ] Evaluation with dataset, report link, date, metrics and thresholds (auto)
- [ ] Every thresholded metric meets its threshold (auto)
- [ ] Unacceptable errors gated at their hard limit (for example `fraud_recall >= 1.0`)
- [ ] Source pinned to a commit or tag, so the report describes exactly this version (auto)
- [ ] Safeguards listed and human oversight described (auto)
- [ ] Personal data handling reviewed if `personal_data: true`
- [ ] Report is reproducible: a reviewer can re-run it from the repository

## production

In use by real customers or staff.

- [ ] Evaluation on real data, not synthetic (auto)
- [ ] Runbook, dashboard, on-call and risk approval linked (auto)
- [ ] Reviewed within the last 180 days (auto)
- [ ] Live traffic sampled for human review, failures added to the evaluation set
- [ ] Cost and error-rate alerts in place

## deprecated

- [ ] Reason and sunset date (auto)
- [ ] Replacement linked if there is one; `replaced_by` must point to a registered asset (auto)
- [ ] Users notified
