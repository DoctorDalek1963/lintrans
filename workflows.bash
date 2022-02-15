#!/bin/bash

IFS=$'\n'

for command in $(cat .github/workflows/*.yaml | grep -Po '(?<=run: )[^|]+'); do
	echo -e "\e[1;32mRUNNING:\e[0m '$command'"
	eval "$command" || echo -e "\e[1;31mFAILED:\e[0m '$command'"
	echo
	echo
	echo
done

unset IFS
