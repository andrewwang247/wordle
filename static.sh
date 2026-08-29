#!/bin/bash

# Copyright 2026. Andrew Wang.
# Run static checks on all Python code.

set -uo pipefail

# List of all Python files.
pyfiles=$(find . -name "*.py" -type f -not -path "./env/*");

printf "Running autopep...\n"
autopep8 -i -a -a $pyfiles

printf "Running pylint...\n"
pylint $pyfiles

printf "Running pycodestyle...\n"
pycodestyle $pyfiles

printf "Running pydocstyle...\n"
pydocstyle $pyfiles

printf "Running mypy...\n"
mypy --strict $pyfiles
