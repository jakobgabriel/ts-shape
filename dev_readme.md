## Development 

- Generate new pdocs: `.\generate_docs.sh`
- Install package locally: `pip install -e .`
- Run tests locally with pytest: `pytest ./tests`

- Build package for upload: `python setup.py sdist bdist_wheel`
- Upload build package to pypi: `twine upload dist/* --verbose --skip-existing`