# AGENTS.md

## Project Overview

`docker-openwisp` provides Docker images, compose files, and deployment helpers for running OpenWISP in containers.

Core code lives in this repository root:

- `images/` contains Docker image definitions and service-specific scripts.
- `docker-compose.yml` defines the standard deployment stack but works also for local testing.
- `customization/`, `deploy/`, `build.py`, and `Makefile` support image customization, install flows, and builds.
- Tests live in `tests/`.
- `docs/` is incorporated into the unified, versioned OpenWISP documentation built by `openwisp-docs`, not a standalone site; use `docs/user/` for end users and `docs/developer/` for contributors and developers of extensions, downstream, or derivative apps.

## Source of Truth

- Use `README.rst` and `docs/` for setup, deployment, and usage.
- Use `.github/workflows/ci.yml` for CI-tested build, QA, and test commands.
- Use GitHub issue/PR templates when asked to open issues or PRs.

If instructions conflict, repository config and CI workflows win first, docs next, and this file is supplemental.

## Contributing Guidelines

- Before editing, inspect the relevant implementation, tests, documentation, and configuration. Follow existing repository patterns and do not invent behavior or requirements.
- Keep each contribution focused and change only the lines necessary for its goal. Do not include unrelated refactors, formatting churn, or generated and dependency-file changes unless explicitly required.
- Add or update focused tests for every behavior change. Use test-driven development when the scope is very clear, such as bug fixes or narrowly scoped changes. For new features, tests may be added after implementation, but confirm they fail when key feature code is removed. When a test failure does not clearly state the expected outcome that was not met, add an explicit assertion message.
- Run `./qa-format` after each change.
- Run the relevant targeted tests, builds, and documented QA checks, including `./run-qa-checks` when provided. Do not claim a change is complete when verification fails; report the failure or blocker.
- When requirements, intended behavior, or an unexpected failure are unclear, stop and seek clarification instead of making speculative changes.
- When starting work on a new issue, create a new branch from `master`. Use `issues/<issue-number>-<short-title>` for issue work; otherwise, use a short, descriptive branch name.
- Commit messages must be descriptive and use past tense. Past tense is a writing guideline that agents and contributors must follow; it is not checked automatically. For issue work, use an allowed prefix and a capitalized, past-tense subject ending with `#<issue-number>`, for example `[fix] Fixed perennial "modified" state #213`. Repeat the issue reference in the body with `Fixes`, `Closes`, `Resolves`, or `Related to` as appropriate. After creating a commit, use `openwisp-commit --check` to validate the current `HEAD`; it cannot validate a proposed message. Use `openwisp-commit --check --rev-range <range>` for an existing commit range, and `cz -n cz_openwisp info` to view allowed prefixes and message structure.
- Add an explanatory commit body only for substantial changes, new features, or non-obvious bug fixes. The releaser automatically publishes the subject of `[feature]`, `[change]`, `[change!]`, `[deps]`, and `[fix]` commits, including scoped variants, in the changelog. Write those subjects in clear, user-friendly language suitable for release notes.
- Send new commits in response to review feedback instead of amending existing commits.

## Development Rules

- Follow the DRY principle: do not duplicate information or code across files.
- Preserve Docker image contracts, compose service names, environment variables, volumes, ports, and upgrade paths unless explicitly required.
- Be careful with shell scripts, Docker layers, permissions, entrypoints, health checks, and generated configuration.
- Process inventories, API responses, generated work, and telemetry in bounded batches.
- Do not accumulate all pages, task results, logs, or queued telemetry in memory without a known bound.
- Keep buffers and retry queues bounded. Define what happens when the limit is reached, such as sending the current batch, dropping old data, or reporting an error.
- When code consumes a paginated API, follow its continuation mechanism and process one page at a time.
- Place Python imports at the top of the file. Defer imports only when necessary, such as when an import depends on runtime initialization.
- Avoid unnecessary blank lines inside functions or shell blocks.
- Prefer short, precise names that rely on their nearest meaningful scope. Do not repeat a feature, domain object, or namespace already named by the containing module, class, or function. For example, prefer `EstimatedLocation.refresh()` over `EstimatedLocation.refresh_estimated_location()`. Repeat that context only when the name is used outside that scope or is needed to distinguish genuinely different concepts. When a concise name cannot express a necessary distinction, use a concise docstring to describe it rather than encoding it in an excessively long name.
- Before adding a comment or docstring, ask whether it conveys information a reader cannot reasonably infer from clear code, names, and surrounding scope. Add a concise comment when it explains a non-obvious reason, constraint, compatibility or security requirement, side effect, or unavoidable complexity. In opaque syntax or domain-specific code, especially shell scripts, a comment may also explain what the code does. Do not add comments that merely restate adjacent code one-to-one. Place comments before the relevant block instead of scattering them inside it.
- Update docs when behavior, settings, environment variables, deployment steps, or supported versions change, including when a documented feature's behavior changes or a new user-facing feature is added.
- Review documentation examples and references when behavior changes.
- Preserve public documentation anchors, URLs, include directives, and versioned links unless explicitly required.

## Testing and QA

- For complex or long tests, add a docstring when a longer test name would improve readability or maintainability.
- When separate tests cover different cases of the same feature, share almost identical database preparation, and primarily vary in input or expected outcome, group them in one test method with `subTest`. Keep each subtest's setup explicit and independent, and retain separate test methods when cases exercise genuinely distinct behavior. Leave one blank line before each `with self.subTest(...)` statement only when a test method contains multiple such statements. Do not add a blank line for a single `subTest` statement inside a loop.
- Prefer method decorators for context managers that apply to the entire test method and would otherwise create unnecessary nesting, unless decorator ordering conflicts or the context manager requires data unavailable when the method is defined.
- Use targeted checks while iterating, then run the documented full QA/test command before considering the change complete.
- During development, run focused tests and test suites directly affected by the change instead of routinely running the full suite.
- Before pushing a behavior-affecting change, verify that the full test suite has passed for the current branch after its latest code, test, dependency, or configuration change. If the full suite cannot run, report the blocker and wait for direction.
- Keep helpers and classes used by only one test method inside that method. Promote them to class or module scope only when genuinely reused.
- Keep tests quiet on success. When code under test writes to stdout or stderr, capture and assert that output rather than leaving it unasserted.

## Security Rules

- Watch for exposed secrets, unsafe defaults, insecure permissions, unsafe shell expansion or command strings, path traversal, and accidental public ports.
- Preserve validation and safe handling around environment files, mounted volumes, TLS material, credentials, and service configuration.
- Prevent secret disclosure, unsafe deployment instructions, stale security guidance, and insecure links.

## Troubleshooting

- If documentation and CI commands differ, use CI for verification and report the exact documentation path, CI workflow path, and differing commands. Do not change the documentation until the user explicitly chooses one of these actions: update the named documentation file in the current change because the divergence was caused by that change, or leave it unchanged for a separate follow-up. Never decide that scope distinction independently.
