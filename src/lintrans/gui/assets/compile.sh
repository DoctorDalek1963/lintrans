#!/usr/bin/env sh

pdflatex -shell-escape icon.tex
convert -density 16 icon.pdf 16.jpg
convert -density 32 icon.pdf 32.jpg
convert -density 64 icon.pdf 64.jpg
convert -density 128 icon.pdf 128.jpg
