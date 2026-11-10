Closes #

## What changed

<!-- One paragraph. A reviewer should understand it without asking back. -->

## Acceptance Criteria

<!-- Paste each AC line from the issue and point to the code or test that satisfies it. -->

- [ ] Every AC line of the issue is met

## Definition of Done

Full list in [`DOD.md`](../_bmad-output/planning-artifacts/DOD.md). Tick the lines that apply to this PR:

- [ ] Displayed numbers carry sample size, snapshot date and source, kept apart from the narrative text
- [ ] Small samples are suppressed via `display_policy.suppression_for`, not scattered `n < 30` checks
- [ ] Thresholds and parameters come from versioned config, not hardcoded
- [ ] Each reused operation has exactly one signature in `REGISTRY.md`
- [ ] Alembic has a single head
- [ ] Dependency direction is not inverted
- [ ] User actions call no external model outside the two allowed paths
- [ ] No CV or JD content in tables, logs, events or temp files
- [ ] Main ACs have tests, and test names carry the FR or AD code
- [ ] CI gates for the related ADs are still green
- [ ] Screens work fully on mobile, with `aria-*` and visible focus
- [ ] New CLI commands are documented in `README` or `docs/`
- [ ] `specs/<issue>-<slug>/` is updated for this issue and for every issue whose code this PR touches

## Where reviewers should look closely

<!-- Name the files and say why. Do not leave empty. -->
