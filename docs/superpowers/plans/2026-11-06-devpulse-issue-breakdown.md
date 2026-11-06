# DevPulse Issue Breakdown

> Source of truth for GitHub issues. `scripts/create-issues.py` parses this file and creates labels, milestones and issues. Issues are ordered so dependencies are always created first; `T##` tokens in bodies are rewritten to `#<issue number>`.

**Spec:** `devpulse_high_level_requirements.md`

**Stack (decided):** NestJS + Prisma + PostgreSQL (API) · Next.js + React + TypeScript + Ant Design + TanStack Query + Zustand (web) · JWT auth · REST · UI designed in OpenPencil · pnpm monorepo (`apps/api`, `apps/web`, `packages/*`) · Docker · GitHub Actions · Playwright.

**Format:** each issue is `## T## Title` followed by `Labels:`, `Milestone:` and `Depends:` lines, then the body. A shared Definition of Done is appended to every issue by the script.

---

## T01 Monorepo scaffold and engineering tooling

Labels: area:infra, type:chore, priority:p0
Milestone: M0 Foundation
Depends: none

Set up the repo so every later task starts from a consistent, enforced baseline.

**Scope**

- pnpm workspaces: `apps/api` (NestJS), `apps/web` (Next.js), `packages/shared` (shared TS types / zod schemas / enums such as `TaskStatus`, `Priority`, `TaskType`).
- TypeScript strict mode everywhere, shared `tsconfig.base.json`.
- ESLint + Prettier, `.editorconfig`, `.nvmrc`, `.gitignore`.
- Husky + lint-staged + commitlint (Conventional Commits).
- Root scripts: `lint`, `typecheck`, `test`, `build`, `dev`.

**Acceptance criteria**

- `pnpm install && pnpm lint && pnpm typecheck && pnpm build` passes on a clean clone.
- A commit with a non-conventional message is rejected by the hook.

## T02 Local development environment (Docker Compose, env management)

Labels: area:infra, type:chore, priority:p0
Milestone: M0 Foundation
Depends: T01

**Scope**

- `docker-compose.yml` with PostgreSQL 16 (named volume, healthcheck) and optional api/web services for dev.
- `.env.example` for api and web; no secrets committed.
- Document one-command startup (`pnpm dev:up`).

**Acceptance criteria**

- Fresh clone to running DB with one documented command.
- App fails fast with a clear message when required env vars are missing (validated in T05).

## T03 CI pipeline (GitHub Actions)

Labels: area:infra, type:chore, priority:p0
Milestone: M0 Foundation
Depends: T01

**Scope**

- Workflow on PR + push to `main`: install (cached), lint, typecheck, unit tests, build, Prisma migrate check against a Postgres service container, `pnpm audit --prod`.
- Separate job for Playwright E2E (enabled once T26 lands).
- Required status checks documented; branch protection instructions in README.

**Acceptance criteria**

- A PR with a failing lint/type/test cannot be merged.
- CI runtime under ~10 minutes with caching.

## T04 AI automation workflow and repo conventions

Labels: area:infra, type:chore, priority:p0
Milestone: M0 Foundation
Depends: T01

The project is built mostly by AI agents; the repo must make that safe and repeatable.

**Scope**

- `CLAUDE.md`: architecture, commands, conventions, definition of done, do/don't list.
- Issue templates (feature, bug), PR template with checklist, `CODEOWNERS`.
- Branch naming `feat/T##-slug`, one PR per issue, `Closes #N` in PR body.
- Dependabot config (npm, docker, actions).
- GitHub Action running Claude code review on PRs (secret setup documented).

**Acceptance criteria**

- A new agent session can pick up an issue using only `CLAUDE.md` and the issue text.
- PRs automatically get the template and an AI review.

## T05 Backend core infrastructure (NestJS)

Labels: area:backend, type:feature, priority:p0
Milestone: M0 Foundation
Depends: T01, T02

**Scope**

- Config module with schema validation (fail fast).
- Layering convention: controller → service → repository (Prisma access only in repositories).
- Global `ValidationPipe` (whitelist, forbidNonWhitelisted, transform), global exception filter, consistent response envelope `{ data, meta }` and error shape `{ error: { code, message, details } }`.
- Structured logging (pino) with redaction of passwords, tokens, cookies, auth headers; request IDs.
- helmet, CORS allow-list, rate limiting (stricter on auth routes), graceful shutdown.
- `/health` (liveness + DB readiness), Swagger/OpenAPI at `/docs` (disabled in prod by env).

**Acceptance criteria**

- Unit/e2e tests prove: validation errors return the standard shape, unknown fields are rejected, sensitive fields never appear in logs.

## T06 Database schema, Prisma migrations and seed

Labels: area:backend, area:database, type:feature, priority:p0
Milestone: M0 Foundation
Depends: T02, T05

**Scope**

- Models: `User`, `RefreshToken` (hashed), `Task` (type TASK|BUG, status TODO|IN_PROGRESS|DONE, priority LOW|MEDIUM|HIGH|CRITICAL, optional `dueDate`), `Note` (markdown), `Snippet` (title, description, language, code), `Tag`, and join tables `NoteTag`, `SnippetTag`.
- Every owned row has `userId` FK with `onDelete: Cascade`; unique `(userId, tag name)` (case-insensitive).
- Indexes for list/filter paths (`userId,status`, `userId,dueDate`, `userId,updatedAt`) and for search (pg_trgm / tsvector, finalised in T21).
- Committed migrations; dev seed script with realistic sample data.

**Acceptance criteria**

- `prisma migrate deploy` works from empty DB; seed is idempotent.
- Schema reviewed against ownership/isolation requirement (no table without `userId` scope).

## T07 Design system and tokens in OpenPencil

Labels: area:design, type:chore, priority:p0
Milestone: M0 Foundation
Depends: none

**Scope**

- Colors (light + dark), typography (UI + monospace), spacing, radius, elevation, status/priority colors.
- Component library: buttons, inputs, select, tag, badge, table, card, modal, drawer, toast, empty/loading/error states, kanban card.
- Export tokens in a form `apps/web` can consume (T08 maps them to Ant Design theme).
- Design files committed under `design/`.

**Acceptance criteria**

- Tokens documented in `design/README.md`; clean, minimal, developer-focused look per spec §8.

## T08 Screen designs in OpenPencil (all pages, states, tablet)

Labels: area:design, type:chore, priority:p0
Milestone: M0 Foundation
Depends: T07

**Scope**

- Screens: Login, Register, Dashboard, Tasks (list + Kanban), Task form, Knowledge Vault (notes/snippets lists), Note editor + preview, Snippet editor, Command palette.
- For each: loading, empty, error, success states; delete confirmation.
- Desktop and tablet layouts.

**Acceptance criteria**

- Every screen needed by T10–T24 has a design; exported PNGs in `design/exports/`.

## T09 Frontend core (Next.js app shell)

Labels: area:frontend, type:feature, priority:p0
Milestone: M0 Foundation
Depends: T01, T07

**Scope**

- Next.js (App Router) + TypeScript strict, Ant Design themed from T07 tokens, light/dark.
- TanStack Query provider with sane defaults (stale time, no refetch storms); typed API client with unified error handling mapped to the API error shape.
- Zustand store for client-only state (UI prefs, palette open state).
- App shell: sidebar/top nav for Dashboard / Tasks / Vault, responsive down to tablet, global toast + error boundary, route-level loading/empty/error primitives.
- Reusable `ConfirmDialog`, `EmptyState`, `PageHeader`, `FormField` components.

**Acceptance criteria**

- Shell renders on desktop and tablet widths; component tests cover shared components.

## T10 Backend authentication

Labels: area:backend, type:feature, priority:p0
Milestone: M1 Authentication
Depends: T05, T06

**Scope**

- `POST /auth/register`, `/auth/login`, `/auth/refresh`, `/auth/logout`, `GET /auth/me`.
- Passwords hashed with argon2id; password policy validated server-side; email normalised and unique.
- JWT short-lived access token + rotating refresh token (stored hashed, revocable), delivered via httpOnly, Secure, SameSite cookies; CSRF protection for cookie flows.
- Global auth guard (deny by default, `@Public()` opt-out) and `@CurrentUser()` decorator.
- Generic login error (no user enumeration), login rate limiting.

**Acceptance criteria**

- Tests: register/login/logout/refresh happy paths, wrong password, duplicate email, expired/revoked token, rotation reuse detection.
- No password or token ever appears in responses or logs.

## T11 Frontend authentication

Labels: area:frontend, type:feature, priority:p0
Milestone: M1 Authentication
Depends: T08, T09, T10

**Scope**

- Login and Register pages with inline validation and server error mapping.
- Session bootstrap via `/auth/me`, silent refresh, route protection (middleware + client guard), logout action, redirect-after-login.

**Acceptance criteria**

- Unauthenticated users are redirected to login; data persists across logout/login; expired session recovers or redirects cleanly.

## T12 Backend tasks and bugs API

Labels: area:backend, type:feature, priority:p0
Milestone: M2 Tasks & Bugs
Depends: T10

**Scope**

- CRUD under `/tasks`: title (required, length-limited), description, type, priority, status, optional due date.
- List endpoint: search (title/description, case-insensitive), filters (type, status, priority), sort, offset or cursor pagination with total.
- `PATCH /tasks/:id/status` for Kanban moves (and optional ordering).
- Ownership enforced in the repository layer (queries scoped by `userId`); foreign IDs return 404.

**Acceptance criteria**

- Integration tests cover each filter combination, pagination boundaries, validation errors, and cross-user access returning 404 for read, update and delete.

## T13 Frontend tasks list view

Labels: area:frontend, type:feature, priority:p1
Milestone: M2 Tasks & Bugs
Depends: T08, T09, T11, T12

**Scope**

- Tasks page with list view, debounced search, filters (type, status, priority) synced to URL query params, pagination, due-today/overdue highlighting.
- Loading skeletons, empty state, error state with retry.

**Acceptance criteria**

- Filters/search/pagination state survives reload and back/forward; no redundant requests while typing.

## T14 Frontend task create/edit/delete

Labels: area:frontend, type:feature, priority:p1
Milestone: M2 Tasks & Bugs
Depends: T13

**Scope**

- Create/edit form (drawer or modal) with field validation matching backend rules and server error display.
- Delete with confirmation; success/error toasts; optimistic updates with rollback where safe.

**Acceptance criteria**

- Full CRUD works from list view; cache invalidation keeps lists and dashboard consistent.

## T15 Frontend Kanban view

Labels: area:frontend, type:feature, priority:p1
Milestone: M2 Tasks & Bugs
Depends: T14

**Scope**

- List/Kanban toggle (persisted preference); columns Todo / In Progress / Done.
- Drag and drop between columns (keyboard accessible) calling the status endpoint with optimistic update and rollback on failure.
- Same search and filters apply to both views.

**Acceptance criteria**

- Moving a card persists after reload; failure shows an error and restores the card.

## T16 Backend tags API

Labels: area:backend, type:feature, priority:p0
Milestone: M3 Knowledge Vault
Depends: T10

**Scope**

- `GET /tags` (with usage counts), tag creation by name on assignment, rename, delete (unlinks, does not delete items).
- Per-user, case-insensitive uniqueness; name normalisation and length limits.

**Acceptance criteria**

- Tests for uniqueness, normalisation, cascade behaviour and cross-user isolation.

## T17 Backend notes API

Labels: area:backend, type:feature, priority:p0
Milestone: M3 Knowledge Vault
Depends: T16

**Scope**

- CRUD under `/notes`: title, markdown `content`, tags.
- List: search (title + content), filter by tags (any/all), pagination, sort by `updatedAt`.
- Markdown stored raw; size limits enforced; sanitisation is a render-time concern (T20), documented.

**Acceptance criteria**

- Integration tests for CRUD, tag assignment, search, tag filters and ownership isolation.

## T18 Backend code snippets API

Labels: area:backend, type:feature, priority:p0
Milestone: M3 Knowledge Vault
Depends: T16

**Scope**

- CRUD under `/snippets`: title, description, language (from supported list in `packages/shared`), code, tags.
- List: search (title, description, code), filter by tags and language, pagination.

**Acceptance criteria**

- Integration tests for CRUD, language/tag filters, search, ownership isolation.

## T19 Frontend Knowledge Vault page

Labels: area:frontend, type:feature, priority:p1
Milestone: M3 Knowledge Vault
Depends: T08, T09, T11, T17, T18

**Scope**

- Vault page with Notes / Snippets tabs, shared search box, tag filter, language filter (snippets), URL-synced state, pagination.
- Tag input component (create-on-type, reusable).
- Loading, empty and error states; delete confirmation.

**Acceptance criteria**

- Filters/search work consistently with the Tasks page patterns (shared hooks/components).

## T20 Frontend note editor with Markdown preview

Labels: area:frontend, type:feature, priority:p1
Milestone: M3 Knowledge Vault
Depends: T19

**Scope**

- Note create/edit with split or tabbed edit/preview, GFM rendering, syntax-highlighted fenced code.
- Rendering is sanitised (no raw HTML/XSS); unsaved-changes warning.

**Acceptance criteria**

- A test with a malicious markdown payload proves scripts/handlers are not rendered.

## T21 Frontend snippet editor and syntax highlighting

Labels: area:frontend, type:feature, priority:p1
Milestone: M3 Knowledge Vault
Depends: T19

**Scope**

- Snippet create/edit with language selector and code editor; syntax-highlighted read view with copy-to-clipboard.
- Lazy-load highlighter/editor to protect bundle size.

**Acceptance criteria**

- Highlighting correct for each supported language; copy gives success feedback.

## T22 Backend global search API

Labels: area:backend, type:feature, priority:p1
Milestone: M4 Search & Command Palette
Depends: T12, T17, T18

**Scope**

- `GET /search?q=&types=&limit=` returning grouped, ranked results across tasks, bugs, notes, snippets, each with `type`, `id`, `title`, snippet of match.
- PostgreSQL full-text search with `pg_trgm` for partial/typo-tolerant matches; GIN indexes via migration.
- Strictly scoped by `userId`; query length/limit validation.

**Acceptance criteria**

- Integration tests across all four types, ranking sanity, isolation; `EXPLAIN` shows index use on a seeded dataset of ≥10k rows with p95 under 100 ms.

## T23 Frontend command palette

Labels: area:frontend, type:feature, priority:p1
Milestone: M4 Search & Command Palette
Depends: T09, T22, T14, T19

**Scope**

- Global `Ctrl/Cmd + K` from any authenticated page; debounced search with grouped results.
- Navigation to selected item; shortcuts for "Create task", "Create note", "Create snippet" and page navigation.
- Full keyboard navigation (arrows, Enter, Esc), focus trap, ARIA combobox semantics.

**Acceptance criteria**

- Opens/closes reliably, no request on empty query, works at tablet width; component and E2E tests.

## T24 Backend dashboard summary API

Labels: area:backend, type:feature, priority:p1
Milestone: M5 Dashboard
Depends: T12, T17, T18

**Scope**

- `GET /dashboard`: task counts by status, tasks due today and overdue (user timezone handling documented), recently updated notes and snippets (limit configurable).
- Single efficient query strategy; no N+1.

**Acceptance criteria**

- Tests for boundary dates (due today at day edges, overdue, Done tasks excluded from overdue) and isolation.

## T25 Frontend dashboard

Labels: area:frontend, type:feature, priority:p1
Milestone: M5 Dashboard
Depends: T08, T14, T19, T24

**Scope**

- Status summary, due-today/overdue panel, recent notes and snippets, quick-create actions, deep links to items.
- Loading/empty/error states per widget.

**Acceptance criteria**

- Counts match the Tasks page; links open the correct item; layout works on desktop and tablet.

## T26 Backend automated test suite and isolation tests

Labels: area:testing, area:backend, type:chore, priority:p1
Milestone: M6 Hardening & Release
Depends: T12, T17, T18, T22, T24

**Scope**

- Integration tests using a real PostgreSQL (Testcontainers or CI service), migrations applied per run.
- Dedicated cross-user isolation suite hitting every protected endpoint with a second user's IDs.
- Coverage gate in CI (target ≥80% on services).

**Acceptance criteria**

- Every protected endpoint has an authorization test (401 unauthenticated, 404 foreign resource).

## T27 End-to-end tests (Playwright) for acceptance criteria

Labels: area:testing, area:frontend, type:chore, priority:p1
Milestone: M6 Hardening & Release
Depends: T15, T20, T21, T23, T25

**Scope**

- One E2E spec per acceptance criterion in spec §11 (register/login/logout, dashboard accuracy, task CRUD + Kanban, notes/snippets, tags, search, command palette, persistence, states, tablet viewport).
- Runs in CI against Docker Compose stack; traces/screenshots on failure.

**Acceptance criteria**

- All 10 acceptance criteria are covered by a named test and green in CI.

## T28 Accessibility, responsive and performance pass

Labels: area:frontend, type:chore, priority:p2
Milestone: M6 Hardening & Release
Depends: T25, T23

**Scope**

- axe checks in E2E, keyboard-only walkthrough, focus management, contrast in both themes.
- Tablet breakpoints verified; Lighthouse performance ≥90 and accessibility ≥95 on key pages; bundle analysis, lazy-loading review, request-waterfall review (no unnecessary API calls).

**Acceptance criteria**

- Lighthouse and axe results recorded in the PR; no critical a11y violations.

## T29 Security hardening review

Labels: area:security, type:chore, priority:p1
Milestone: M6 Hardening & Release
Depends: T26, T27

**Scope**

- Review against OWASP ASVS/Top 10: authn/session, CSRF, XSS (markdown), injection, IDOR, rate limiting, security headers/CSP, cookie flags, dependency audit, secrets scan, error message leakage, log redaction.
- Fix findings or file follow-up issues with severity.

**Acceptance criteria**

- Written report in `docs/security/review.md`; no open high/critical findings.

## T30 Production build, containers and deployment

Labels: area:infra, type:feature, priority:p1
Milestone: M6 Hardening & Release
Depends: T03, T29

**Scope**

- Multi-stage, non-root Dockerfiles for api and web; production compose (or chosen host) with reverse proxy/TLS notes.
- Migrations run on deploy (`migrate deploy`), healthchecks, resource limits, env/secret handling, DB backup and restore procedure.
- Release workflow: build and push images on tag.

**Acceptance criteria**

- `docker compose -f docker-compose.prod.yml up` yields a working stack; restore-from-backup rehearsed and documented.

## T31 Documentation

Labels: area:docs, type:chore, priority:p2
Milestone: M6 Hardening & Release
Depends: T30

**Scope**

- README (quickstart, scripts, env), `docs/ARCHITECTURE.md` (layers, data model diagram, auth flow), API reference from OpenAPI, `CONTRIBUTING.md`, runbook (deploy, backup, rollback).

**Acceptance criteria**

- A new developer reaches a running app and a green test run using only the docs.

## T32 Release readiness and acceptance sign-off

Labels: area:release, type:chore, priority:p1
Milestone: M6 Hardening & Release
Depends: T27, T28, T29, T30, T31

**Scope**

- Walk through spec §11 acceptance criteria 1–10 with evidence links (tests, screenshots).
- Verify out-of-scope list (spec §10) was not accidentally built.
- Tag `v1.0.0`, write release notes.

**Acceptance criteria**

- Checklist in this issue fully ticked with evidence; release published.
