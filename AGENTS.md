# QuickPub – Agent Context

Implementation guide for coding agents changing **quickpub**. Product pitch and user-facing install: [`README.md`](README.md).

---

## Orientation

| Question | Answer |
| -------- | ------ |
| What is this? | Python package for **local pre-publish CI/CD** (enforcers, QA, build, upload) |
| Importable code | `quickpub/` |
| Toolchain | [uv](https://docs.astral.sh/uv/) + `pyproject.toml` / `uv.lock` |
| Python | `>=3.11` (CI matrix **3.11, 3.12, 3.13**) |
| Tests | `tests/` — pytest + coverage (`fail_under` **50** in `pyproject.toml`); **never delete** |
| Secrets | Never commit `.pypirc`, API keys, tokens |

```text
.
├── .github/             # CODEOWNERS, dependabot.yml, thin CI/CD orchestrators
├── quickpub/            # Importable package
├── tests/
├── githooks/            # Optional local hooks (e.g. black)
├── pyproject.toml
├── uv.lock
├── README.md            # Marketing / user docs
└── LICENSE              # MIT
```

Shared CI/CD: [`danielnachumdev/actions`](https://github.com/danielnachumdev/actions) (`@latest`). How to adopt: [`HOW-TO-USE.md`](https://github.com/danielnachumdev/actions/blob/latest/HOW-TO-USE.md).

---

## Develop

```bash
uv sync                 # default-groups includes dev + test → .venv
uv sync --all-groups    # equivalent here (dev + test are defaults)
```

`tool.uv.default-groups` is `["dev", "test"]` — plain `uv sync` installs those groups.

| Task | Command |
| ---- | ------- |
| Import smoke | `uv run python -c "import quickpub"` |
| Tests | `uv run pytest` |
| Types | `uv run mypy` |
| Lint | `uv run pylint quickpub` |

Config for mypy / pylint / pytest / coverage lives in `pyproject.toml`.

### Dependencies

- **Runtime:** `danielutils>=1.2.0`, `requests>=2.33.0`, `fire`, `twine>=6.1.0`
- **Dev group:** githooklib, tqdm, pylint, mypy, types-tqdm, types-requests, beautifulsoup4, setuptools, black
- **Test group:** pytest, pytest-xdist, pytest-asyncio, pytest-cov
- Security floors for Dependabot-fixed transitive deps are in `[tool.uv] constraint-dependencies`

Prefer editing floors in `pyproject.toml` and regenerating with `uv lock` / `uv sync`.

---

## Publishing consumers (uv / PEP 621) — required

When using QuickPub **as a library** against a uv-managed / PEP 621 project (including this repo if you ever run a local `publish.py`):

**Never** call `publish()` with the default `generate_project_files=True`. That overwrites `pyproject.toml` and deletes toolchain config (`[dependency-groups]`, `[tool.uv]`, `[tool.mypy]`, …).

Always publish with:

```python
from quickpub import publish, UvBuildSchema, PypircUploadTarget

publish(
    ...,
    build_schemas=[UvBuildSchema()],
    generate_project_files=False,
    upload_targets=[PypircUploadTarget()],
)
```

- `UvBuildSchema` runs `uv build` (not `python setup.py sdist`).
- `generate_project_files=False` keeps the existing toml; only `[project].version` and `__init__.__version__` are updated.
- `SetuptoolsBuildSchema` + generated files is only for projects that do **not** already own a `pyproject.toml`.

This repository does **not** ship a root `publish.py`. **quickpub** itself is released via GitHub CD (below), not a checked-in local publish script.

---

## Code style & domain notes

- Follow the writing-python skill when adding/refactoring modules (class-first, SRP files, no stub shims).
- Public surface is re-exported from `quickpub/__init__.py` (`publish`, strategies, structures, classifiers, `ExitEarlyError`, `resolve_publish_environment`, …).
- `__version__` is set in `quickpub/__init__.py` and bumped with `[project].version` when file generation / version update runs; CD stamps version into the release wheel from GitHub tags / `pyproject.toml`.
- Strategy layout: `strategies/` (abstract) + `strategies/implementations/` (enforcers, QA runners, build schemas, upload targets, providers, package managers).
- QA orchestration lives in `qa.py`; CLI / `publish()` entry in `__main__.py`.

---

## PRs, CI, and releases

1. Branch off `main`; open a PR into `main`.
2. Attach **exactly one** semver label: `noBump` | `bumpPatch` | `bumpMinor` | `bumpMajor`.
3. **CI** — `…/ci.yml@latest` (tests) + `…/semver-ci.yml@latest` (validate label). Prefer **`CI / CI`** and **`Semver / Semver`**.
4. **CD** — `…/semver-cd.yml@latest` after CI succeeds on `main`: bump → wheel → GitHub Release → floating `vMAJOR` → **PyPI** (`publish-pypi: true`), or skip on `noBump`.
5. Version **source of truth** is GitHub Release tags. If none yet, CD seeds from `pyproject.toml`.
6. Dependabot PRs stay on `noBump`.
7. Change shared CI/semver behavior in **`danielnachumdev/actions`**, not by re-vendoring here.

**PyPI:** shipped only via CD (Trusted Publishing OIDC preferred for repo + workflow `cd.yml`; optional repo secret `PYPI_API_TOKEN`). Thin CD must grant `id-token: write` and pass `PYPI_API_TOKEN` by name.

### Repo gates (already configured)

- `.github/CODEOWNERS` — `@danielnachumdev`
- Branch protection / ruleset: required **`CI / CI`** + **`Semver / Semver`**; code-owner reviews; no force-push to `main`
- Private vulnerability reporting via GitHub Security Advisories

---

## Sensitive / ignored

Do not commit: `.pypirc`, `.venv/`, `venv/`, `dist/`, `__pycache__/`, API keys, tokens. Track `uv.lock`. Respect `.gitignore`.
