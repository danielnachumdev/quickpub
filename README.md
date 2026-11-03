# QuickPub

**Local CI/CD before you publish** — run enforcers, QA, packaging, and upload in one pipeline so broken releases fail on your machine, not on PyPI.

[![CI](https://github.com/danielnachumdev/quickpub/actions/workflows/ci.yml/badge.svg)](https://github.com/danielnachumdev/quickpub/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/quickpub.svg)](https://pypi.org/project/quickpub/)
[![Python](https://img.shields.io/pypi/pyversions/quickpub.svg)](https://pypi.org/project/quickpub/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

Requires **Python 3.11+** (CI-tested on **3.11–3.13**).

## Why QuickPub?

Publishing a Python package usually means juggling several steps: validate project files, run mypy/pylint/pytest, bump the version, build, upload. Miss a step and you find out in CI — or after a bad release.

**QuickPub** wires those steps together. You define the package once; it enforces constraints, runs QA across detected Python environments, builds, and uploads.

- **Enforcers** for README, LICENSE, `.pypirc`, and local/PyPI version consistency
- **Bounded QA runners** — mypy, pylint, pytest, unittest with configurable score floors
- **Build schemas** — setuptools sdist or `uv build` for PEP 621 / uv projects
- **Upload targets** — twine via `.pypirc`, optional GitHub push
- **MIT licensed**, CI-tested on Python **3.11–3.13**

## Install

```bash
pip install quickpub
# or
uv add quickpub
```

## Quick start

Add a `publish.py` in your project root:

```python
from quickpub import (
    publish,
    MypyRunner,
    PylintRunner,
    PytestRunner,
    SetuptoolsBuildSchema,
    PypircUploadTarget,
    PypircEnforcer,
    ReadmeEnforcer,
    LicenseEnforcer,
    LocalVersionEnforcer,
    PypiRemoteVersionEnforcer,
)

publish(
    name="my-package",
    version="1.0.0",
    author="Your Name",
    author_email="you@example.com",
    description="My package",
    homepage="https://github.com/you/my-package",
    dependencies=["requests>=2.25.0"],
    min_python="3.11.0",
    enforcers=[
        PypircEnforcer(),
        ReadmeEnforcer(),
        LicenseEnforcer(),
        LocalVersionEnforcer(),
        PypiRemoteVersionEnforcer(),
    ],
    global_quality_assurance_runners=[
        MypyRunner(bound="<=20"),
        PylintRunner(bound=">=0.8"),
        PytestRunner(bound=">=0.95"),
    ],
    build_schemas=[SetuptoolsBuildSchema()],
    upload_targets=[PypircUploadTarget()],
)
```

### uv / `pyproject.toml` projects (important)

If the project already has a PEP 621 `pyproject.toml` (uv, Hatch, Poetry, PDM), **do not** use the default file generation. `publish()` would overwrite `pyproject.toml` and wipe `[dependency-groups]`, `[tool.uv]`, `[tool.mypy]`, and other toolchain config.

Use `UvBuildSchema` and `generate_project_files=False`:

```python
from quickpub import (
    publish,
    UvBuildSchema,
    PypircUploadTarget,
    PypircEnforcer,
    ReadmeEnforcer,
    LicenseEnforcer,
    LocalVersionEnforcer,
    PypiRemoteVersionEnforcer,
    MypyRunner,
    PylintRunner,
    PytestRunner,
)

publish(
    name="my-package",
    version="1.0.0",
    author="Your Name",
    author_email="you@example.com",
    description="My package",
    homepage="https://github.com/you/my-package",
    dependencies=["requests>=2.25.0"],
    min_python="3.11.0",
    enforcers=[
        PypircEnforcer(),
        ReadmeEnforcer(),
        LicenseEnforcer(),
        LocalVersionEnforcer(),
        PypiRemoteVersionEnforcer(),
    ],
    global_quality_assurance_runners=[
        MypyRunner(bound="<=20"),
        PylintRunner(bound=">=0.8"),
        PytestRunner(bound=">=0.95"),
    ],
    build_schemas=[UvBuildSchema()],
    generate_project_files=False,
    upload_targets=[PypircUploadTarget()],
)
```

That keeps the existing `pyproject.toml`, bumps only `[project].version` and `__init__.__version__`, and builds with `uv build`.

Run it:

```bash
python publish.py
```

**Dry run** — validate and run QA without building or uploading:

```python
publish(..., demo=True)
```

PyPI upload needs a valid `.pypirc` (never commit it).

## What you get

| Surface | Role |
| -------- | ---- |
| `publish` | Orchestrates enforcers → QA → optional file gen → build → upload |
| Enforcers | README, LICENSE, `.pypirc`, local/PyPI version gates |
| QA runners | `MypyRunner`, `PylintRunner`, `PytestRunner`, `UnittestRunner` with bounds |
| Build schemas | `SetuptoolsBuildSchema`, `UvBuildSchema` |
| Upload targets | `PypircUploadTarget`, GitHub upload target |
| Providers | uv / pip package managers; default, uv, conda, union Python providers |

## What runs

When you call `publish()`, QuickPub runs these stages in order:

1. **Enforcers** — checks README, LICENSE, `.pypirc`, and local/PyPI version consistency
2. **Quality assurance** — mypy, pylint, pytest, and unittest with configurable score bounds, in parallel across detected Python environments
3. **File generation** — by default writes `setup.py`, `pyproject.toml`, `MANIFEST.in`, and updates `__init__.py`. Pass `generate_project_files=False` to keep an existing `pyproject.toml` (only `[project].version` and `__init__.__version__` are updated).
4. **Build & upload** — builds the sdist (`SetuptoolsBuildSchema` or `UvBuildSchema`) and uploads via twine (and optionally pushes to GitHub)

Skip build and upload with `demo=True`.

## Environment detection

By default, QuickPub detects your toolchain from the project root:

| Project layout | Package manager | Python provider |
| --- | --- | --- |
| `uv.lock` present | `UvPackageManager` | `UvPythonProvider` |
| otherwise | `PipPackageManager` | `DefaultPythonProvider` |

Override for conda or mixed setups:

```python
from quickpub import CondaPythonProvider, UnionProvider

publish(
    ...,
    python_interpreter_provider=UnionProvider([
        CondaPythonProvider(["base", "py311", "py312"]),
    ]),
)
```

For full control, pass `package_manager` and `python_interpreter_provider` explicitly, or call `resolve_publish_environment()` before `publish()`.

## CLI

QuickPub installs a `quickpub` command that wraps `publish()` via [Fire](https://github.com/google/python-fire). For most projects, a `publish.py` script is easier to maintain than long CLI invocations.

## Contributing & development

Agent/developer workflow (uv, tests, CI/CD labels, secrets): see [`AGENTS.md`](./AGENTS.md).

Report security issues privately via [GitHub advisories](https://github.com/danielnachumdev/quickpub/security/advisories/new) — please do not open a public issue for vulnerabilities.

## License

MIT — see [`LICENSE`](./LICENSE).
