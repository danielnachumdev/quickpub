# QuickPub

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Catch publish failures on your machine before they hit CI or PyPI.

QuickPub runs pre-publish checks, quality tools, tests, packaging, and upload in one pipeline — so broken releases fail locally with fast feedback.

## The problem

Publishing a Python package usually means juggling several steps: validate project files, run mypy/pylint/pytest, bump the version, generate packaging files, build the sdist, upload to PyPI. Miss a step and you find out in CI — or worse, after a bad release.

QuickPub wires those steps together. You define your package once; it enforces constraints, runs QA across Python environments, builds, and uploads.

## Install

```bash
pip install quickpub
```

With [uv](https://docs.astral.sh/uv/):

```bash
uv add quickpub
```

Requires Python **3.8+** (tested on 3.8–3.13).

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
    build_schemas=[UvBuildSchema()],
    generate_project_files=False,
    upload_targets=[PypircUploadTarget()],
)
```

That keeps the existing `pyproject.toml`, bumps only `[project].version` and `__init__.__version__`, and builds with `uv build`. See [this repo's `publish.py`](publish.py).

Run it:

```bash
python publish.py
```

**Dry run** — validate and run QA without building or uploading:

```python
publish(..., demo=True)
```

PyPI upload needs a valid `.pypirc`. See [this repo's `publish.py`](publish.py) for a full working example.

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

For full control, pass `package_manager` and `python_interpreter_provider` explicitly, or call `resolve_publish_environment()` before `publish()`.

## CLI

QuickPub installs a `quickpub` command that wraps `publish()` via [Fire](https://github.com/google/python-fire). For most projects, a `publish.py` script is easier to maintain than long CLI invocations.

## Development

To work on QuickPub itself, clone the repo and use uv:

```bash
git clone https://github.com/danielnachumdev/quickpub.git
cd quickpub
uv sync
uv run pytest
```

## License

MIT — see [LICENSE](LICENSE).
