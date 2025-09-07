# 🚀 Development Guide

## 1. Install Package Locally

```bash
pip install -e .
```
> Installs your package in editable mode for local development.

---

## 2. Run Tests

```bash
pytest ./tests
```
> Executes all tests to ensure your code is working as expected.

---

## 3. Build Distribution Packages

```bash
python setup.py sdist bdist_wheel
```
> Creates source and wheel distributions in the `dist/` directory.

---

## 4. Publish to PyPI

```bash
twine upload dist/* --verbose --skip-existing
```
> Uploads your package to [PyPI](https://pypi.org/).  
> **Tip:** Ensure your credentials are set up in `~/.pypirc`.

---

## 5. Automatic Version Bumping and Publishing (CI)

This repo is configured to auto-bump the version in `setup.py`, create a Git tag, and publish to PyPI on pushes to `main`.

- Workflow: `.github/workflows/auto_bump_version.yml`
- Publish on tags: `.github/workflows/pypi-packaging.yml` (triggers on `v*` tags)

Keep the version declaration in `setup.py` in this exact form (the trailing comma is fine):

```python
setuptools.setup(
    name="ts_shape",
    version = "0.0.0.24",
    # ...
)
```

On every push to `main`, the auto-bump workflow reads that line and increments it based on the latest commit message:

- Major: include `BREAKING CHANGE`, `#major`, or the short `!:` in the subject
- Minor: start the subject with `feat` or include `#minor`
- Patch: default for all other commits

Examples:

```text
feat: add new SPC rule 9
# => bumps 0.0.0.24 -> 0.1.0 and tags v0.1.0

fix: handle NaNs in StringFilter
# => bumps 0.1.0 -> 0.1.1 and tags v0.1.1

refactor!: remove deprecated API (BREAKING CHANGE)
# => bumps 0.1.1 -> 1.0.0 and tags v1.0.0
```

The workflow then:
- Commits the updated `setup.py` with `[skip ci]` to avoid loops
- Creates and pushes a tag `vX.Y.Z`
- The packaging workflow sees the tag and publishes the built artifacts to PyPI

One‑time repo setting required: enable “Read and write permissions” for GitHub Actions under
Settings → Actions → General → Workflow permissions.
