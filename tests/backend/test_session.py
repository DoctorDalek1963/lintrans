# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""Test the functionality of saving and loading sessions."""

from pathlib import Path

from lintrans.gui.session import Session
from lintrans.matrices.wrapper import MatrixWrapper

from conftest import get_test_wrapper


def test_save_and_load(tmp_path: Path, test_wrapper: MatrixWrapper) -> None:
    """Test that sessions save and load and return the same matrix wrapper."""
    session = Session(test_wrapper)
    path = str((tmp_path / 'test.lt').absolute())
    session.save_to_file(path)

    loaded_session = Session.load_from_file(path)
    assert loaded_session.matrix_wrapper == get_test_wrapper()
