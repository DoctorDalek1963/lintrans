#!/bin/bash

IFS=$'\n'

for command in $(cat .github/workflows/*.yml | grep -Po '(?<=run: )[^|]+'); do
	echo "RUNNING: '$command'"
	eval "$command"
	echo
	echo
	echo
done

unset IFS
