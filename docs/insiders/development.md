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