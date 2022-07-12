#!/usr/bin/env sh

# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

rm -f *.log
rm -f *.aux
rm -f *.dvi
rm -f *.lof
rm -f *.lot
rm -f *.bit
rm -f *.idx
rm -f *.glo
rm -f *.bbl
rm -f *.bcf
rm -f *.ilg
rm -f *.toc
rm -f *.ind
rm -f *.out
rm -f *.blg
rm -f *.fdb_latexmk
rm -f *.fls
rm -f *.run.xml
rm -f *.synctex.gz

rm -f sections/processed_*.tex
rm -f sections/development/processed_*.tex

rm -rf _minted-main/
