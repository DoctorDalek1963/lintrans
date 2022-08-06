lintrans.matrices package
=========================

Module contents
---------------

.. automodule:: lintrans.matrices

.. _expression-syntax-docs:

Expression Syntax
-----------------

.. note::
   All whitespace is ignored.

Documentation on correct expression syntax is given here. This is a basic summary:

- A single matrix is written as a capital letter like ``A``, or as ``rot(x)``, where ``x`` is a
  real number
- When a matrix is given as ``rot(x)``, this means that it represents an anticlockwise rotation by
  ``x`` degrees
- Matrix A multiplied by matrix B is written as ``AB``
- Matrix A plus matrix B is written as ``A+B``
- Matrix A minus matrix B is written as ``A-B``
- Matrix A to the power of ``n`` is written as ``A^n`` or ``A^{n}`` where ``n`` is a positive or
  negative integer
- The transpose of matrix A is written as ``A^T`` or ``A^{T}``
- Any matrix may be multiplied by a real constant, like ``3A``, or ``1.2B``

.. note::
   ``A^2 3B`` will be interpreted as ``A^{23}B``, not ``A^{2}3B``. Braces are needed to clarify
   this. However, ``A^2 + 3B`` will be interpreted as expected.

Here is the technical BNF schema used by :func:`lintrans.matrices.parse.parse_matrix_expression`
and :func:`lintrans.matrices.parse.validate_matrix_expression`:

.. literalinclude:: bnf.txt

.. note::
   In the GUI, commas are also acceptable in an input expression, as long as everything between
   commas is valid on its own. These commas are used exclusively in the animation to animate an
   expression in steps.

Submodules
----------

lintrans.matrices.parse module
------------------------------

.. automodule:: lintrans.matrices.parse

lintrans.matrices.utility module
--------------------------------

.. automodule:: lintrans.matrices.utility

lintrans.matrices.wrapper module
--------------------------------

.. automodule:: lintrans.matrices.wrapper
