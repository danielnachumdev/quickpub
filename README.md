# QuickPub

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Run quality checks, tests, and packaging locally before you publish a Python package.

QuickPub validates versions and project files, runs QA tools (mypy, pylint, pytest, unittest), builds the sdist, and uploads to PyPI/GitHub — so failures show up on your machine, not in CI.

## Requirements

- Python **3.8+**
- Tested on **3.8, 3.9, 3.10, 3.11, 3.12, 3.13** (see [CI](.github/workflows/ci.yml))

## Install

[uv](https://docs.astral.sh/uv/) is the recommended workflow:

```bash
git clone https://github.com/danielnachumdev/quickpub.git
cd quickpub
uv sync
```

Runtime-only install:

```bash
uv sync --no-group dev --no-group test
```

Use as a CLI in another project:

```bash
uv add quickpub
```

## Usage

### Publish this repo

```bash
uv run python publish.py
```

Requires a valid `.pypirc` for PyPI upload. Set `demo=True` in `publish.py` to run checks without building or uploading.

### Publish your own package

`publish()` runs enforcers, QA, file generation, build, and upload in one call:

```python
from quickpub import (
    publish,
    MypyRunner,
    PylintRunner,
    PytestRunner,
    SetuptoolsBuildSchema,
    PypircUploadTarget,
    GithubUploadTarget,
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
    min_python="3.8.0",
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
    upload_targets=[PypircUploadTarget(), GithubUploadTarget()],
)
```

Omit `python_interpreter_provider` and `package_manager` to auto-detect the environment:

| Project layout | Package manager | Python provider |
|---|---|---|
| `uv.lock` present | `UvPackageManager` | `UvPythonProvider` |
| otherwise | `PipPackageManager` | `DefaultPythonProvider` |

Override for conda or mixed setups:

```python
from quickpub import CondaPythonProvider, UnionProvider

publish(
    ...,
    python_interpreter_provider=UnionProvider([
        CondaPythonProvider(["base", "py39", "py38"]),
    ]),
)
```

Manual control: `resolve_publish_environment()` or explicit `package_manager` / `python_interpreter_provider` arguments.

## What it does

**Enforcers** — README, LICENSE, `.pypirc`, local/PyPI version checks.

**QA runners** — mypy, pylint, pytest, unittest with configurable score bounds; runs in parallel across environments.

**Build & upload** — generates `setup.py` / `pyproject.toml` / `MANIFEST.in`, builds sdist, uploads via twine and/or git push.

**Environment providers** — `DefaultPythonProvider`, `UvPythonProvider`, `CondaPythonProvider`, or `UnionProvider` to combine them.

## Development

```bash
uv run pytest          # full test suite
uv run python publish.py  # publish quickpub itself
```

Tool config lives in `pyproject.toml` (`pytest`, `mypy`, `pylint`, `coverage`).

## License

MIT — see [LICENSE](LICENSE).
