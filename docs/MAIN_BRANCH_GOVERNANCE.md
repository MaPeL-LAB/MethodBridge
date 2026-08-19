# Main branch governance

**Repository contract:** prepared. **GitHub settings:** pending administrator verification.

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
