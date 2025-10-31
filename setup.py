from setuptools import setup, find_packages 

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setup(
    name = "ts_shape",
    version = "0.0.0.30",
    author = "Jakob Gabriel",
    author_email = "jakob.gabriel5@googlemail.com",
    description = "ts-shape filters, transforms and engineers your timeseries dataframe",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://jakobgabriel.github.io/ts-shape/",
    project_urls = {
        "Bug Tracker": "https://github.com/jakobgabriel/ts-shape",
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages = find_packages(where="src"),
    package_dir = {"": "src"},
    python_requires = ">=3.10"
)