## Asset

- id:
- level requested: experimental / validated / production / deprecated

## Checks the validator cannot make

- [ ] Owner is a team
- [ ] Limitations are listed
- [ ] (validated) Unacceptable errors are gated at their hard limit
- [ ] (validated) Personal data handling reviewed, if `personal_data: true`
- [ ] (validated) The evaluation can be re-run from the pinned version; command:
- [ ] (production) Live traffic is sampled for review; failures feed the evaluation set
- [ ] (production) Cost and error-rate alerts exist; link:
- [ ] (deprecated) Users notified

`registry validate` and `registry catalog --check` run in CI.
