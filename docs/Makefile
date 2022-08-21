# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS  ?=
SPHINXBUILD ?= sphinx-build
SOURCEDIR   = source
BUILDDIR    = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile precompile

precompile:
	python create_objects_inv.py

	python -m pylint --rcfile=/dev/null --exit-zero --output=/dev/null --reports=y --disable=all --enable=imports,RP0402 --int-import-graph=source/backend/_images/int-imports.png $(shell find ../src/lintrans/ -name "*.py" | tr "\n" " ")

	pyreverse -A -S -m n -f SPECIAL -o png -d . lintrans
	rm packages.png
	mv classes.png source/backend/_images/classes.png

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
