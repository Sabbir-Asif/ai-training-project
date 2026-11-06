# DevPulse — agent guide

Monorepo built mostly by AI agents. Read this and the issue text; that should be enough to start.

## Layout

- `apps/api` — NestJS backend (`@devpulse/api`), Jest tests (`*.spec.ts`)
- `apps/web` — Next.js App Router frontend (`@devpulse/web`)
- `packages/shared` — zod schemas / enums shared by both (`@devpulse/shared`), Vitest tests. Built to `dist/` with `tsc`; consumers need it built (root `typecheck`/`build` do this).
- Requirements: `devpulse_high_level_requirements.md`; task breakdown: `docs/superpowers/plans/`

## Commands (Node 24, pnpm 12 via corepack)

`pnpm install` · `pnpm dev` · `pnpm lint` · `pnpm typecheck` · `pnpm test` · `pnpm build` · `pnpm format`
Before opening a PR, `pnpm lint && pnpm typecheck && pnpm test && pnpm build` must all pass.

## Workflow

- **First job on any issue: move its board card to "In Progress"** (`scripts/set-issue-status.sh N "In Progress"`),
  before reading code or editing. The hook below does this automatically as a safety net.
- Vague ticket? Run the `refine-ticket` skill first (`.claude/skills/refine-ticket`) to make it AI-ready.

- One issue = one branch `feat/T##-slug` = one PR with `Closes #N` in the body.
- Commits follow Conventional Commits (enforced by commitlint via Husky). Pre-commit runs lint-staged.
- Board: the "DevPulse" GitHub Project (#10). A Claude Code hook (`.claude/settings.json` →
  `scripts/hooks/issue-in-progress.sh`) moves the issue to **In Progress** before the first edit on a
  `feat/T##-*` branch. Set other states with `scripts/set-issue-status.sh <issue> <Todo|"In Progress"|Done>`
  (set Done when the PR merges). Needs `gh` auth with `project` scope.

## Conventions

- TypeScript strict everywhere; extend `tsconfig.base.json`. No `any` (lint error). Use `import type`.
- Shared enums/schemas (`TaskStatus`, `Priority`, `TaskType`) live in `packages/shared`; never duplicate them.
- Validate all backend input; check ownership on user-scoped data.
- Frontend handles loading, empty, success and error states.

## Don't

- Commit secrets or `.env` files (only `.env.example`). Don't log tokens/passwords.
- Skip hooks (`--no-verify`) or weaken lint/TS settings to make something pass.
- Add dependencies build scripts without listing them in `allowBuilds` in `pnpm-workspace.yaml`.

## Definition of Done

See the checklist at the bottom of every issue: tests + green lint/typecheck/build, validation,
UI states, no secrets, docs/`CLAUDE.md` updated when conventions change.
