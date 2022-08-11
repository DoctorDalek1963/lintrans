.. _expression-syntax:

Expression syntax
=================

The `expression input box` and :ref:`expression definition dialog<defining-matrices-as-expression>`
allow you to compose matrices using multiplication (scalar and matrix), addition, exponentiation,
brackets, and transposes. Obviously you can't easily type something like
:math:`\left(2\mathbf{A}^{2}3\mathbf{B}^{T}\right)^{-1}\mathbf{C}`, so lintrans uses a more
keyboard-friendly syntax.

For this example, you would type ``(2A^{2} 3B^{T})^{-1} C`` or ``(2A^{2}3B^T)^-1C`` if you wanted
to be more concise. Notice that the squared part of :math:`\mathbf{A}^{2}` didn't lose its braces.
This is because lintrans ignores spaces and parses exponents "greedily", meaning that ``A^2 3B``
will be interpreted as ``A^{23}B``, not ``A^{2}3B`` as probably intended. If you have two numbers
next to each other like this, use braces (``A^{2}3B``) or brackets (``(A^2)(3B)``) to separate the
terms.
