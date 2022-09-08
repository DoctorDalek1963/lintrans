#!/bin/bash

# Don't run compile-for-release.yaml locally, because that won't work properly
for file in .github/workflows/docstrings.yaml .github/workflows/linting.yaml .github/workflows/tests.yaml .github/workflows/type-checks.yaml; do
	IFS=$'\n'

	for command in $(cat $file | grep -Po '(?<=run: )[^|]+'); do
		echo -e "\e[1;32mRUNNING:\e[0m '$command'"
		eval "$command" || echo -e "\e[1;31mFAILED:\e[0m '$command'"
		echo
		echo
		echo
	done

	unset IFS
done
