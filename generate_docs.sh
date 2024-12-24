#!/bin/bash

# Define the source and documentation directories
SRC_DIR="./src/ts_shape"
DOCS_DIR="./docs"

# Ensure the docs directory exists
mkdir -p $DOCS_DIR

# Export the environment variable to allow subprocess execution in pdoc
export PDOC_ALLOW_EXEC=1

# Find all Python files in the source directory and generate documentation for each
find $SRC_DIR -name '*.py' -exec pdoc {} -o $DOCS_DIR \;

# Optional: open the docs in your browser (Linux/Mac, adjust for your environment)
# xdg-open $DOCS_DIR/index.html