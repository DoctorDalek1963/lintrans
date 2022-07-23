#!/usr/bin/env sh

pdflatex -shell-escape icon.tex \
&& convert -density 100 icon.pdf icon.jpg
