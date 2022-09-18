#!/usr/bin/env sh

make_img() {
	convert -density $1 icon.pdf $1.jpg
	convert $1.jpg $1.xpm
	rm $1.jpg
}

pdflatex -shell-escape icon.tex

convert -density 100 icon.pdf icon.jpg

make_img 16
make_img 32
make_img 64
make_img 128
