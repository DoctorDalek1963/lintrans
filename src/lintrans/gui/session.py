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
from lintrans.matrices import MatrixWrapper


def _return_none() -> None:
    """Return None.

    This function only exists to make the defaultdict in :class:`Session` pickle-able.
    """
    return None


class Session:
    """Hold information about a session and provide methods to save and load that data."""

    __slots__ = ('matrix_wrapper', 'polygon_points')

    def __init__(
        self,
        *,
        matrix_wrapper: MatrixWrapper,
        polygon_points: List[Tuple[float, float]]
    ) -> None:
        """Create a :class:`Session` object with the given data."""
        self.matrix_wrapper = matrix_wrapper
        self.polygon_points = polygon_points

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
    def load_from_file(cls, filename: str) -> Tuple[Session, str]:
        """Return the session state that was previously saved to ``filename`` along with its lintrans version.

        If the session file is missing any attributes that we expect, then
        those missing attributes will be None. The version number we return
        is the version of lintrans that created the save file.

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
            polygon_points=data_dict['polygon_points']
        )

        return session, data_dict['lintrans']
