# Main branch governance

**Repository contract:** active. **GitHub settings:** independently verified on
2026-08-20.

After the initial bootstrap, `main` should accept changes only through reviewed
pull requests. The intended GitHub ruleset is:

- require a pull request before merge;
- require at least one accountable approval;
- require CODEOWNERS review for protected paths;
- dismiss stale approvals after new commits;
- require resolved review conversations and an up-to-date branch;
- require CI, data-governance, schema, submission-readiness, and repository-integrity checks;
- block direct pushes, force pushes, and branch deletion;
- apply the rule to administrators;
- prefer squash merges for bounded implementation phases.

Do not describe these controls as active until GitHub visibly reports the branch
as protected and a non-destructive direct-push test is rejected.

## Verification record

GitHub's protection API and public branch metadata independently reported
`main` as protected for everyone, including administrators, with the following
effective settings:

- pull requests are required with one approval, CODEOWNERS review, stale-review
  dismissal, resolved conversations, and an up-to-date branch;
- required checks are exactly `CI`, `Data governance`, `Schema validation`,
  `Submission readiness`, and `Repository integrity`;
- force pushes and branch deletion are disabled; and
- squash merge is the only enabled merge method.

An ordinary direct update using an empty commit with the same tree as `main`
was rejected by GitHub with protected-branch error `GH006`; the remote `main`
SHA remained `6b58c54e013011a93f8e96d8e15a9803491a3576`. The probe changed no repository
content or remote ref. This record contains no credentials, local paths, or
sensitive payloads.
