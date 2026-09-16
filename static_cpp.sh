#!/bin/bash

# Copyright 2026. Andrew Wang.
# Run static checks on all C++ code.

set -uo pipefail

sources="native/*"

printf "Running clang-format...\n"
clang-format -i -style=file $sources

printf "Running cppcheck...\n"
cppcheck --language=c++ --std=c++23 --quiet \
    --check-level=exhaustive \
    --enable=all \
    --inconclusive \
    --template=gcc \
    --suppress=checkersReport \
    --suppress=missingIncludeSystem \
    $sources

if [[ ! -f "compile_commands.json" ]]; then
    printf "Generating compile commands...\n"
    bear -- make clean release
fi
run-clang-tidy -quiet

printf "Running cpplint...\n"
cpplint --filter=-build/include_subdir --quiet $sources
