# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module contains the :class:`DisplaySettings` class, which holds configuration for display."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DisplaySettings:
    """This class simply holds some attributes to configure display."""

    smoothen_determinant: bool = True
    """This controls whether we want the determinant to change smoothly during the animation.

    .. note::
       Even if this is True, it will be ignored if we're animating from a positive det matrix to
       a negative det matrix, or vice versa, because if we try to smoothly animate that determinant,
       things blow up and the app often crashes.
    """

    applicative_animation: bool = True
    """There are two types of simple animation, transitional and applicative.

    Let ``C`` be the matrix representing the currently displayed transformation, and let ``T`` be the target matrix.
    Transitional animation means that we animate directly from ``C`` from ``T``,
    and applicative animation means that we animate from ``C`` to ``TC``, so we apply ``T`` to ``C``.
    """

    animation_pause_length: int = 400
    """This is the number of milliseconds that we wait between animations when using comma syntax."""

    draw_determinant_parallelogram: bool = False
    """This controls whether or not we should shade the parallelogram representing the determinant of the matrix."""

    draw_determinant_text: bool = True
    """This controls whether we should write the text value of the determinant inside the parallelogram.

    The text only gets draw if :attr:`draw_determinant_parallelogram` is also True.
    """

    draw_eigenvectors: bool = False
    """This controls whether we should draw the eigenvectors of the transformation."""

    draw_eigenlines: bool = False
    """This controls whether we should draw the eigenlines of the transformation."""
