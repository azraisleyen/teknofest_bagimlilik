# Python packaging

## Discovery boundary

This repository is a flat-layout Django application rather than a `src/` library. Automatic
setuptools discovery is unsafe here because application assets and integration artifacts are also
top-level directories. `pyproject.toml` therefore supplies explicit discovery roots and include /
exclude patterns. Only `apps.*`, `config.*`, and the independently importable
`sentra_qr_client` are installed. Tests are never shipped as import packages.

The JSON event schemas used during request validation are package resources under
`apps.qr.schemas.v1`, so validation works from editable installs and built wheels. Canonical copies
remain under `contracts/v1` for non-Python consumers. Changes to either copy must remain identical;
contract tests enforce their presence, and CI verifies wheel contents from a clean virtualenv.

## Dependency strategy

Application and production dependency pins live in `[project.dependencies]`. `requirements/base.txt`
installs that project in editable mode for repository development; production and development
requirements extend the same base rather than restating application versions. Build-system tooling
is separately and exactly pinned because PEP 517 resolves it before project installation.

## Release verification

A release candidate must pass isolated sdist/wheel builds, strict Twine metadata checks, clean-wheel
imports, packaged-resource checks, `pip check`, the complete quality job, and the security job.
Deployment remains repository/image based because Django templates and static deployment assets are
part of the application image; the wheel is the verified Python-code distribution inside that
build, not a standalone end-user server bundle.
