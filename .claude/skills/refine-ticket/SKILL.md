---
name: refine-ticket
description: Pull a GitHub issue, polish it into an unambiguous, AI-ready ticket (clear goal, scope, testable acceptance criteria, dependencies, out-of-scope, Definition of Done) and write the improved version back to GitHub. Use whenever the user says "refine", "polish", "groom", "clean up", "review" or "make AI-ready" a ticket/issue/task (e.g. "refine T05", "refine #12"), or before implementing an issue whose text is vague, thin or missing acceptance criteria — even if they don't say "refine".
---

# Refine ticket

Goal: after this runs, a fresh agent session can implement the issue from `CLAUDE.md` and the issue text alone, and anyone can tell objectively when it is done. Vague tickets cause wrong guesses, so close gaps now instead of during implementation.

Input: an issue number (`12`, `#12`) or task id (`T12` → issue #12; issue numbers match task numbers in this repo). If none is given, ask which one.

## Steps

1. **Pull it.** Use JSON output — plain `gh issue view` fails here on the deprecated Projects (classic) field:
   `gh issue view N --json number,title,body,labels,milestone,state,comments`
   Save the original body to `$TMPDIR` (or the scratchpad) as `issue-N.original.md` so nothing is lost.
2. **Gather context** (read-only): `CLAUDE.md`, `devpulse_high_level_requirements.md` sections the ticket touches, `docs/superpowers/plans/*breakdown*.md`, the issues named in "Depends on" (`gh issue view M --json title,body,state`), and the code that already exists in the area. Refinement grounded in the real requirements and codebase beats generic polish.
3. **Assess against the checklist** below. Note each gap.
4. **Resolve gaps.** Fill what the requirements/codebase already answer and mark it as derived. If a gap needs a product decision only the user can make, ask one concise question (batch them) — never invent requirements silently. Keep unknowns as an explicit "Open questions" list if the user can't answer yet.
5. **Rewrite** using the template below. Preserve the author's intent, labels, milestone and dependency links; keep what is already good verbatim. Do not expand scope — split off a follow-up instead and say so.
6. **Show the diff** (original vs. new) and a 3-line summary of what changed and why.
7. **Write back** unless the user asked for a dry run:
   `gh issue edit N --body-file <new.md>` (optionally `--title`). Do not touch labels/milestone/assignees unless the checklist found them wrong; if so, say what you changed. Then add one short comment: `gh issue comment N --body "Refined by AI: <what changed>. Original body preserved in this comment's collapsed section."` with the original body inside a `<details>` block, so history is recoverable.
8. Report the issue URL. Do not move the board status — refinement isn't implementation (the hook does that when work starts).

## Checklist

- **Outcome**: one sentence on what is true after this ships and why it matters.
- **Scope**: concrete, file/module/endpoint-level where known; stack matches `CLAUDE.md`.
- **Acceptance criteria**: each is observable and testable (a command, request/response, or UI behaviour), including error/empty/edge cases. Replace words like "works", "proper", "fast" with measurable checks.
- **Dependencies**: blockers listed as `Depends on: #N`, and each actually exists/is done or is noted.
- **Out of scope / non-goals**: stated, to stop agents wandering.
- **Test plan**: which tests prove each criterion (unit/e2e), and how to run them.
- **Security/data**: validation, ownership checks, secrets, where relevant.
- **Size**: if it can't be done in one PR on one branch `feat/T##-slug`, propose a split.
- **Definition of Done** footer kept intact.

## Template

```markdown
## Goal

<one-to-two sentences: outcome and why>

**Depends on:** #N, #M <!-- or "none" -->

## Scope

- ...

## Out of scope

- ...

## Acceptance criteria

- [ ] Given … when … then … (testable)
- [ ] ...

## Test plan

- ...

## Notes / open questions

- (derived from requirements §X) ...
- ❓ <question needing a human decision>

---

### Definition of Done

<keep the existing checklist unchanged>
```

Keep it tight: a refined ticket is clearer, not longer for its own sake.
