#!/bin/bash

# Define the source and documentation directories
SRC_DIR="./src/timeseries_shaper"
DOCS_DIR="./docs"

# Ensure the docs directory exists
mkdir -p $DOCS_DIR

# Find all Python files in the source directory and generate documentation for each
find $SRC_DIR -name '*.py' -exec pdoc {} -o $DOCS_DIR \;

# Optional: open the docs in your browser (Linux/Mac, adjust for your environment)
# xdg-open $DOCS_DIR/index.html