# Contributing

Thank you for your interest in contributing to **ts-shape**! This page covers the licensing landscape of the project and its dependencies so that contributors can make informed decisions when adding or updating packages.

For development setup, building, testing, and publishing workflows, see the [Development Guide](insiders/development.md).

---

## Project License

ts-shape is released under the **MIT License**. See the full license text in [`LICENSE.txt`](../LICENSE.txt).

All contributions to this repository are accepted under the same MIT License.

---

## Third-Party Dependency Licenses

The table below lists every runtime dependency declared in `pyproject.toml`, its license, and what it is used for in ts-shape.

| Dependency | Version | License | Purpose |
|---|---|---|---|
| **pandas** | >= 2.1.0 | BSD-3-Clause | Core dataframe operations |
| **numpy** | >= 1.26.4 | BSD-3-Clause | Numerical computations |
| **scipy** | >= 1.13.1 | BSD-3-Clause | Scientific and statistical functions |
| **sqlalchemy** | >= 2.0.32 | MIT | Database connectivity (TimescaleDB loader) |
| **psycopg2-binary** | >= 2.9.9 | LGPL-2.1 | PostgreSQL adapter |
| **azure-storage-blob** | >= 12.19.1 | MIT | Azure Blob Storage loader |
| **s3fs** | >= 2024.10.0 | BSD-3-Clause | S3 file system access |
| **requests** | >= 2.32.3 | Apache-2.0 | HTTP requests |
| **pytz** | >= 2024.1 | MIT | Timezone handling |

### License Compatibility

All dependencies are **compatible with the MIT License**:

- **BSD-3-Clause** (pandas, numpy, scipy, s3fs) — permissive, no restrictions beyond attribution.
- **MIT** (sqlalchemy, azure-storage-blob, pytz) — same terms as ts-shape itself.
- **Apache-2.0** (requests) — permissive, compatible with MIT distribution.
- **LGPL-2.1** (psycopg2-binary) — the only copyleft dependency. Since ts-shape uses psycopg2 as an unmodified library installed via pip (dynamic linking), no LGPL obligations are triggered for ts-shape users or distributors.

### Guidelines for Adding New Dependencies

When proposing a new dependency, please consider:

1. **License compatibility** — MIT, BSD, and Apache-2.0 are preferred. Avoid GPL-licensed packages as they are incompatible with MIT distribution.
2. **Necessity** — prefer the standard library or existing dependencies where possible.
3. **Maintenance** — choose well-maintained packages with active communities.
4. **Update `requirements.in`** — add direct dependencies there, then run `python scripts/requirements.py compile` to pin versions (see [Development Guide](insiders/development.md#6-manage-requirements-pip-tools)).
