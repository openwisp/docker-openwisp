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
- Avoid unnecessary blank lines inside functions or shell blocks.
- Prefer short, precise names that rely on their nearest meaningful scope. Do not repeat a feature, domain object, or namespace already named by the containing module, class, or function. For example, prefer `EstimatedLocation.refresh()` over `EstimatedLocation.refresh_estimated_location()`. Repeat that context only when the name is used outside that scope or is needed to distinguish genuinely different concepts. When a concise name cannot express a necessary distinction, use a concise docstring to describe it rather than encoding it in an excessively long name.
- Before adding a comment or docstring, ask whether it conveys information a reader cannot reasonably infer from clear code, names, and surrounding scope. Add a concise comment when it explains a non-obvious reason, constraint, compatibility or security requirement, side effect, or unavoidable complexity. In opaque syntax or domain-specific code, especially shell scripts, a comment may also explain what the code does. Do not add comments that merely restate adjacent code one-to-one.
- Update docs when behavior, settings, environment variables, deployment steps, or supported versions change, including when a documented feature's behavior changes or a new user-facing feature is added.
- Review documentation examples and references when behavior changes.
- Preserve public documentation anchors, URLs, include directives, and versioned links unless explicitly required.

## Testing and QA

- Use targeted checks while iterating, then run the documented full QA/test command before considering the change complete.
- Keep helpers and classes used by only one test method inside that method. Promote them to class or module scope only when genuinely reused.

## Security Rules

- Watch for exposed secrets, unsafe defaults, insecure permissions, unsafe shell expansion, path traversal, and accidental public ports.
- Preserve validation and safe handling around environment files, mounted volumes, TLS material, credentials, and service configuration.
- Prevent secret disclosure, unsafe deployment instructions, stale security guidance, and insecure links.

## Troubleshooting

- If documentation and CI commands differ, use CI for verification and report the exact documentation path, CI workflow path, and differing commands. Do not change the documentation until the user explicitly chooses one of these actions: update the named documentation file in the current change because the divergence was caused by that change, or leave it unchanged for a separate follow-up. Never decide that scope distinction independently.
