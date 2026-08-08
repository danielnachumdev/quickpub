# AGENTS.md

## Publishing (uv / pyproject.toml) — required

This repo is uv-managed. `pyproject.toml` is the source of truth (`[dependency-groups]`, `[tool.uv]`, `[tool.mypy]`, `[tool.pytest]`, `[tool.coverage]`, `[tool.pylint]`).

**Never** call `publish()` with the default `generate_project_files=True`. That overwrites `pyproject.toml` and deletes toolchain config.

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
- Full call: [`publish.py`](publish.py).

When adding QuickPub to another uv / PEP 621 project, use the same flags. `SetuptoolsBuildSchema` + generated files is only for projects that do not already own a `pyproject.toml`.

## Development

```bash
uv sync
uv run pytest
```
