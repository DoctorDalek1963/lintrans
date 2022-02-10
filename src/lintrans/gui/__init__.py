"""This package supplies the main GUI and associated dialogs for visualization."""

from . import dialogs, plots, settings, validate
from .main_window import main

__all__ = ['dialogs', 'main', 'plots', 'settings', 'validate']
