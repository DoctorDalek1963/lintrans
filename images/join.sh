#!/usr/bin/env sh

convert -frame 0 -mattecolor none -background none -gravity north $* -append png:- | convert - -shave 0 output.png
