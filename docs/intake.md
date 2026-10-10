# Intake and review

## Submitting

1. Copy an existing `assets/<id>/asset.yaml` that has the kind you are registering, rename the folder to the new
   id, and fill it in.
2. Run `uv run registry validate` and `uv run registry catalog`, and commit both the manifest and the
   regenerated catalog.
3. Open a pull request. The template asks for the definition-of-done items the validator cannot check.

## Reviewing

| Level requested | Reviewers | Target time |
|---|---|---|
| experimental | one CoE engineer | 2 working days |
| validated | one CoE engineer who re-runs the evaluation | 5 working days |
| production | CoE engineer, information security, model risk | 10 working days |

The reviewer for `validated` re-runs the evaluation from the pinned version and compares the numbers with the
manifest. A difference beyond run-to-run noise sends the manifest back.

## Keeping the registry honest

- CI runs `registry validate` and `registry catalog --check` on every pull request, and weekly on `main`, so a
  production asset whose last review is older than 180 days turns the build red without anyone opening a pull
  request.
- Moving an asset down a level (production to validated, or to deprecated) needs one reviewer, never more.
  Making it easy to downgrade keeps levels meaningful.
