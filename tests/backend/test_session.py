# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""Test the functionality of saving and loading sessions."""

from pathlib import Path

import lintrans
from lintrans.gui.session import Session
from lintrans.gui.settings import DisplaySettings
from lintrans.matrices.wrapper import MatrixWrapper

from conftest import get_test_wrapper


def test_save_and_load(tmp_path: Path, test_wrapper: MatrixWrapper) -> None:
    """Test that sessions save and load and return the same matrix wrapper."""
    points = [(1, 0), (-2, 3), (3.2, -10), (0, 0), (-2, -3), (2, -1.3)]
    session = Session(
        matrix_wrapper=test_wrapper,
        polygon_points=points,
        display_settings=DisplaySettings(),
        input_vector=(2, 3)
    )

    path = str((tmp_path / 'test.lt').absolute())
    session.save_to_file(path)

    loaded_session, version, extra_attrs = Session.load_from_file(path)
    assert loaded_session.matrix_wrapper == get_test_wrapper()
    assert loaded_session.polygon_points == points
    assert loaded_session.display_settings == DisplaySettings()
    assert loaded_session.input_vector == (2, 3)

    assert version == lintrans.__version__
    assert not extra_attrs
