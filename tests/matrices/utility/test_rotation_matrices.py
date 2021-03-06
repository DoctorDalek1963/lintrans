# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""Test functions for rotation matrices."""

from typing import List, Tuple

import numpy as np
import pytest

from lintrans.matrices import create_rotation_matrix
from lintrans.typing_ import MatrixType

angles_and_matrices: List[Tuple[float, float, MatrixType]] = [
    (0, 0, np.array([[1, 0], [0, 1]])),
    (90, np.pi / 2, np.array([[0, -1], [1, 0]])),
    (180, np.pi, np.array([[-1, 0], [0, -1]])),
    (270, 3 * np.pi / 2, np.array([[0, 1], [-1, 0]])),
    (360, 2 * np.pi, np.array([[1, 0], [0, 1]])),

    (45, np.pi / 4, np.array([
        [np.sqrt(2) / 2, -1 * np.sqrt(2) / 2],
        [np.sqrt(2) / 2, np.sqrt(2) / 2]
    ])),
    (135, 3 * np.pi / 4, np.array([
        [-1 * np.sqrt(2) / 2, -1 * np.sqrt(2) / 2],
        [np.sqrt(2) / 2, -1 * np.sqrt(2) / 2]
    ])),
    (225, 5 * np.pi / 4, np.array([
        [-1 * np.sqrt(2) / 2, np.sqrt(2) / 2],
        [-1 * np.sqrt(2) / 2, -1 * np.sqrt(2) / 2]
    ])),
    (315, 7 * np.pi / 4, np.array([
        [np.sqrt(2) / 2, np.sqrt(2) / 2],
        [-1 * np.sqrt(2) / 2, np.sqrt(2) / 2]
    ])),

    (30, np.pi / 6, np.array([
        [np.sqrt(3) / 2, -1 / 2],
        [1 / 2, np.sqrt(3) / 2]
    ])),
    (60, np.pi / 3, np.array([
        [1 / 2, -1 * np.sqrt(3) / 2],
        [np.sqrt(3) / 2, 1 / 2]
    ])),
    (120, 2 * np.pi / 3, np.array([
        [-1 / 2, -1 * np.sqrt(3) / 2],
        [np.sqrt(3) / 2, -1 / 2]
    ])),
    (150, 5 * np.pi / 6, np.array([
        [-1 * np.sqrt(3) / 2, -1 / 2],
        [1 / 2, -1 * np.sqrt(3) / 2]
    ])),
    (210, 7 * np.pi / 6, np.array([
        [-1 * np.sqrt(3) / 2, 1 / 2],
        [-1 / 2, -1 * np.sqrt(3) / 2]
    ])),
    (240, 4 * np.pi / 3, np.array([
        [-1 / 2, np.sqrt(3) / 2],
        [-1 * np.sqrt(3) / 2, -1 / 2]
    ])),
    (300, 10 * np.pi / 6, np.array([
        [1 / 2, np.sqrt(3) / 2],
        [-1 * np.sqrt(3) / 2, 1 / 2]
    ])),
    (330, 11 * np.pi / 6, np.array([
        [np.sqrt(3) / 2, 1 / 2],
        [-1 / 2, np.sqrt(3) / 2]
    ]))
]


def test_create_rotation_matrix() -> None:
    """Test that create_rotation_matrix() works with given angles and expected matrices."""
    for degrees, radians, matrix in angles_and_matrices:
        assert create_rotation_matrix(degrees, degrees=True) == pytest.approx(matrix)
        assert create_rotation_matrix(radians, degrees=False) == pytest.approx(matrix)

        assert create_rotation_matrix(-1 * degrees, degrees=True) == pytest.approx(np.linalg.inv(matrix))
        assert create_rotation_matrix(-1 * radians, degrees=False) == pytest.approx(np.linalg.inv(matrix))

    assert (create_rotation_matrix(-90, degrees=True) ==
            create_rotation_matrix(270, degrees=True)).all()
    assert (create_rotation_matrix(-0.5 * np.pi, degrees=False) ==
            create_rotation_matrix(1.5 * np.pi, degrees=False)).all()
