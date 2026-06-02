# AGENTS.md

## Project Overview

`docker-openwisp` provides Docker images, compose files, and deployment helpers for running OpenWISP in containers.

Core code lives in this repository root:

- `images/` contains Docker image definitions and service-specific scripts.
- `docker-compose.yml` and related compose files define local and deployment stacks.
- `customization/`, `deploy/`, `build.py`, and `Makefile` support image customization, install flows, and builds.
- Tests live in `tests/`.

## Source of Truth

- Use `README.rst` and `docs/` for setup, deployment, and usage.
- Use `.github/workflows/ci.yml` for CI-tested build, QA, and test commands.
- Use GitHub issue/PR templates when asked to open issues or PRs.

If instructions conflict, repository config and CI workflows win first, docs next, and this file is supplemental.

## Development Notes

- Keep changes focused. Avoid unrelated refactors and formatting churn.
- Preserve Docker image contracts, compose service names, environment variables, volumes, ports, and upgrade paths unless explicitly required.
- Be careful with shell scripts, Docker layers, permissions, entrypoints, health checks, and generated configuration.
- Avoid unnecessary blank lines inside functions or shell blocks.
- Update docs when behavior, settings, environment variables, deployment steps, or supported versions change.

## Testing and QA

- Add or update tests for every behavior change.
- For bug fixes, write the regression test first, run it against the unfixed code, confirm it fails for the expected reason, then implement the fix.
- Use targeted checks while iterating, then run the documented full QA/test command before considering the change complete.
- Run `./run-qa-checks` when present. Treat failures as blocking unless confirmed unrelated and reported.

## Security Notes

- Watch for exposed secrets, unsafe defaults, insecure permissions, unsafe shell expansion, path traversal, and accidental public ports.
- Preserve validation and safe handling around environment files, mounted volumes, TLS material, credentials, and service configuration.
- Write comments only when they explain why code is shaped a certain way. Put comments before the relevant block instead of scattering them inside it.

## Troubleshooting

- If setup, QA, builds, or tests fail, check docs first, then compare with CI. If commands diverge, follow CI.
