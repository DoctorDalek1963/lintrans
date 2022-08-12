.. _expression-syntax:

Expression syntax
=================

The `expression input box` and :ref:`expression definition dialog<defining-matrices.as-expression>`
allow you to compose matrices using multiplication (scalar and matrix), addition, exponentiation,
brackets, and transposes. Obviously you can't easily type something like
:math:`\left(2\mathbf{A}^{2}3\mathbf{B}^{T}\right)^{-1}\mathbf{C}`, so lintrans uses a more
keyboard-friendly syntax.

For this example, you would type ``(2A^{2} 3B^{T})^{-1} C`` or ``(2A^{2}3B^T)^-1C`` if you wanted
to be more concise. Notice that the squared part of :math:`\mathbf{A}^{2}` didn't lose its braces.
This is because lintrans ignores spaces and parses exponents "greedily"[#]_, meaning that ``A^2
3B`` will be interpreted as ``A^{23}B``, not ``A^{2}3B`` as probably intended. If you have two
numbers next to each other like this, use braces (``A^{2}3B``) or brackets (``(A^2)(3B)``) to
separate the terms.

Most of the rules are exactly what you expect:

- A single matrix is written as a capital letter like ``A`` or ``B``
- To multiply a matrix by a scalar, you can just write it in front, like ``3A`` or ``-1.568237M``
- :math:`\mathbf{AB}` is written as ``AB``
- :math:`\mathbf{A} + \mathbf{B}` is written as ``A+B``
- :math:`\mathbf{A} - \mathbf{B}` is written as ``A-B``
- :math:`\mathbf{A}^{n}` is written as ``A^n`` or ``A^{n}``, where ``n`` is a positive or negative
  integer
- :math:`\mathbf{A}^{T}` is written as ``A^T`` or ``A^{T}``

Additionally, a matrix term may be replaced by ``rot(x)`` to signify an anticlockwise rotation by
:math:`x` degrees. ``rot(x)`` is equivalent to the standard rotation matrix
:math:`\begin{pmatrix}\cos x & -\sin x\\ \sin x & \cos x\end{pmatrix}`. This rotation function can
be used anywhere that a defined matrix could be used.

A matrix term may also be replaced by a parenthesised sub-expression. If you've visualized the
transformation ``AB`` and now want to visualize three times its inverse, you could define a new
matrix ``C`` equal to ``AB`` and visualize ``3C^-1``, or you could directly visualize ``3(AB)^-1``.
These sub-expressions may contain any valid expression (even nested sub-expressions) and can be
used anywhere that a defined matrix could be used.

Examples
--------

.. note::
   In this textbook format, I'm using :math:`\mathbf{R}_{\theta}` to represent an anticlockwise
   rotation of :math:`\theta^{\circ}`. I'm also using spaces for clarity in the lintrans format,
   but these spaces are ignored by the program. Use braces to clarify ambiguous expressions.

.. list-table::
   :widths: 50 50
   :header-rows: 1

   * - Textbook format
     - lintrans format
   * - :math:`\mathbf{A}^{2}\ 3\mathbf{B}`
     - ``A^{2}3B``
   * - :math:`\mathbf{A}^{23}\ \mathbf{B}`
     - ``A^23B``
   * - :math:`\left(2\mathbf{A}^{T} - 3\mathbf{B}^{2}\ \mathbf{C}\right)^{-1}`
     - ``(2A^T - 3B^2 C)^-1``
   * - :math:`\mathbf{M}\ \left(\mathbf{A}^{2}\ \mathbf{R}_{45}\right)^{-1}\ \mathbf{X}`
     - ``M (A^2 rot(45))^-1 X``
   * - :math:`\mathbf{A}\ \left(-2.5\mathbf{B}^{2}\ \left(\mathbf{C}^{-1}\ 2\mathbf{R}_{90}\ \mathbf{D}\right)^{-1}\right)^{3}`
     - ``A (-2.5B^2 (C^{-1} 2rot(90) D)^-1)^3``

I recommend to always put exponents in braces. I haven't done it here, just to show when it's
technically necessary, but it makes things easier to read, so it's good practice to use it all the
time.

.. rubric:: Footnotes

.. [#] The parser will see the character ``^`` and keep reading numbers after it (or a possible
   ``-`` at the start), until it reaches a character that it is not a number. It will then take all
   the numbers it's seen and call that the exponent. If there are braces after the ``^``, then it
   will just use the number in the braces.
