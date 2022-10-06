# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module provides the :class:`Session` class, which provides a way to save and load sessions."""

from __future__ import annotations

import os
import pathlib
import pickle
from collections import defaultdict
from typing import Any, DefaultDict, List, Tuple

import lintrans
from lintrans.gui.settings import DisplaySettings
from lintrans.matrices import MatrixWrapper


def _return_none() -> None:
    """Return None.

    This function only exists to make the defaultdict in :class:`Session` pickle-able.
    """
    return None


class Session:
    """Hold information about a session and provide methods to save and load that data."""

    __slots__ = ('matrix_wrapper', 'polygon_points', 'display_settings', 'input_vector')
    matrix_wrapper: MatrixWrapper
    polygon_points: List[Tuple[float, float]]
    display_settings: DisplaySettings
    input_vector: Tuple[float, float]

    def __init__(
        self,
        *,
        matrix_wrapper: MatrixWrapper,
        polygon_points: List[Tuple[float, float]],
        display_settings: DisplaySettings,
        input_vector: Tuple[float, float],
    ) -> None:
        """Create a :class:`Session` object with the given data."""
        self.matrix_wrapper = matrix_wrapper
        self.polygon_points = polygon_points
        self.display_settings = display_settings
        self.input_vector = input_vector

    def save_to_file(self, filename: str) -> None:
        """Save the session state to a file, creating parent directories as needed."""
        parent_dir = pathlib.Path(os.path.expanduser(filename)).parent.absolute()

        if not os.path.isdir(parent_dir):
            os.makedirs(parent_dir)

        data_dict: DefaultDict[str, Any] = defaultdict(_return_none, lintrans=lintrans.__version__)
        for attr in self.__slots__:
            data_dict[attr] = getattr(self, attr)

        with open(filename, 'wb') as f:
            pickle.dump(data_dict, f, protocol=4)

    @classmethod
    def load_from_file(cls, filename: str) -> Tuple[Session, str, bool]:
        """Return the session state that was previously saved to ``filename`` along with some extra information.

        The tuple we return has the :class:`Session` object (with some possibly None arguments),
        the lintrans version that the file was saved under, and whether the file had any extra
        attributes that this version doesn't support.

        :raises AttributeError: For specific older versions of :class:`Session` before it used ``__slots__``
        :raises EOFError: If the file doesn't contain a pickled Python object
        :raises FileNotFoundError: If the file doesn't exist
        :raises ValueError: If the file contains a pickled object of the wrong type
        """
        with open(filename, 'rb') as f:
            data_dict = pickle.load(f)

        if not isinstance(data_dict, defaultdict):
            raise ValueError(f'File {filename} contains pickled object of the wrong type (must be defaultdict)')

        session = cls(
            matrix_wrapper=data_dict['matrix_wrapper'],
            polygon_points=data_dict['polygon_points'],
            display_settings=data_dict['display_settings'],
            input_vector=data_dict['input_vector'],
        )

        # Check if the file has more attributes than we expect
        # If it does, it's probably from a higher version of lintrans
        extra_attrs = len(
            set(data_dict.keys()).difference(
                set(['lintrans', *cls.__slots__])
            )
        ) != 0

        return session, data_dict['lintrans'], extra_attrs
