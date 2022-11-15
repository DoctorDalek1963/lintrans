# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module contains the :class:`DisplaySettings` class, which holds configuration for display."""

from __future__ import annotations

import os
import pathlib
import pickle
from dataclasses import dataclass
from typing import Tuple

import lintrans


@dataclass(slots=True)
class DisplaySettings:
    """This class simply holds some attributes to configure display."""

    # === Basic stuff

    draw_background_grid: bool = True
    """This controls whether we want to draw the background grid.

    The background axes will always be drawn. This makes it easy to identify the center of the space.
    """

    draw_transformed_grid: bool = True
    """This controls whether we want to draw the transformed grid. Vectors are handled separately."""

    draw_basis_vectors: bool = True
    """This controls whether we want to draw the transformed basis vectors."""

    label_basis_vectors: bool = False
    """This controls whether we want to label the `i` and `j` basis vectors."""

    # === Animations

    smoothen_determinant: bool = True
    """This controls whether we want the determinant to change smoothly during the animation.

    .. note::
       Even if this is ``True``, it will be ignored if we're animating from a positive det matrix to
       a negative det matrix, or vice versa, because if we try to smoothly animate that determinant,
       things blow up and the app often crashes.
    """

    applicative_animation: bool = True
    """There are two types of simple animation, transitional and applicative.

    Let ``C`` be the matrix representing the currently displayed transformation, and let ``T`` be the target matrix.
    Transitional animation means that we animate directly from ``C`` from ``T``,
    and applicative animation means that we animate from ``C`` to ``TC``, so we apply ``T`` to ``C``.
    """

    animation_time: int = 1200
    """This is the number of milliseconds that an animation takes."""

    animation_pause_length: int = 400
    """This is the number of milliseconds that we wait between animations when using comma syntax."""

    # === Matrix info

    draw_determinant_parallelogram: bool = False
    """This controls whether or not we should shade the parallelogram representing the determinant of the matrix."""

    show_determinant_value: bool = True
    """This controls whether we should write the text value of the determinant inside the parallelogram.

    The text only gets draw if :attr:`draw_determinant_parallelogram` is also True.
    """

    draw_eigenvectors: bool = False
    """This controls whether we should draw the eigenvectors of the transformation."""

    draw_eigenlines: bool = False
    """This controls whether we should draw the eigenlines of the transformation."""

    # === Polygon

    draw_untransformed_polygon: bool = True
    """This controls whether we should draw the untransformed version of the user-defined polygon."""

    draw_transformed_polygon: bool = True
    """This controls whether we should draw the transformed version of the user-defined polygon."""

    # === Input/output vectors

    draw_input_vector: bool = True
    """This controls whether we should draw the input vector in the main viewport."""

    draw_output_vector: bool = True
    """This controls whether we should draw the output vector in the main viewport."""

    def save_to_file(self, filename: str) -> None:
        """Save the display settings to a file, creating parent directories as needed."""
        parent_dir = pathlib.Path(os.path.expanduser(filename)).parent.absolute()

        if not os.path.isdir(parent_dir):
            os.makedirs(parent_dir)

        data: Tuple[str, DisplaySettings] = (lintrans.__version__, self)

        with open(filename, 'wb') as f:
            pickle.dump(data, f, protocol=4)

    @classmethod
    def load_from_file(cls, filename: str) -> Tuple[str, DisplaySettings]:
        """Return the display settings that were previously saved to ``filename`` along with some extra information.

        The tuple we return has the version of lintrans that was used to save the file, and the data itself.

        :raises EOFError: If the file doesn't contain a pickled Python object
        :raises FileNotFoundError: If the file doesn't exist
        :raises ValueError: If the file contains a pickled object of the wrong type
        """
        if not os.path.isfile(filename):
            return lintrans.__version__, cls()

        with open(filename, 'rb') as f:
            file_data = pickle.load(f)

        if not isinstance(file_data, tuple):
            raise ValueError(f'File {filename} contains pickled object of the wrong type (must be tuple)')

        # Create a default object and overwrite the fields that we have
        data = cls()
        for attr in file_data[1].__slots__:
            setattr(data, attr, getattr(file_data[1], attr))

        return file_data[0], data
