"""This package supplies the main GUI and associated dialogs for visualization."""

from . import dialogs, plots, settings
from .main_window import main

__all__ = ['dialogs', 'main', 'plots', 'settings']
