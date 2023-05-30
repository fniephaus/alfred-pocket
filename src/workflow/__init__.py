#!/usr/bin/env python3

"""A helper library for `Alfred <http://www.alfredapp.com/>`_ workflows."""
import os

from .workflow import (
    ICON_ACCOUNT,
    ICON_BURN,
    ICON_CLOCK,
    ICON_COLOR,
    ICON_COLOUR,
    ICON_EJECT,
    ICON_ERROR,
    ICON_FAVORITE,
    ICON_FAVOURITE,
    ICON_GROUP,
    ICON_HELP,
    ICON_HOME,
    ICON_INFO,
    ICON_NETWORK,
    ICON_NOTE,
    ICON_SETTINGS,
    ICON_SWIRL,
    ICON_SWITCH,
    ICON_SYNC,
    ICON_TRASH,
    ICON_USER,
    ICON_WEB,
    MATCH_ALL,
    MATCH_ALLCHARS,
    MATCH_ATOM,
    MATCH_CAPITALS,
    MATCH_INITIALS,
    MATCH_INITIALS_CONTAIN,
    MATCH_INITIALS_STARTSWITH,
    MATCH_STARTSWITH,
    MATCH_SUBSTRING,
    KeychainError,
    PasswordNotFound,
    Variables,
    Workflow,
    manager,
)

# pylint: disable=consider-using-with
__version__ = open(
    os.path.join(os.path.dirname(__file__), "version"), encoding="utf-8"
).read()
__title__ = "Alpynist"
__author__ = "Arthur Pinheiro"
__license__ = "MIT"
__copyright__ = "Copyright 2022 Arthur Pinheiro"

__all__ = [
    "KeychainError",
    "PasswordNotFound",
    "Variables",
    "Workflow",
    "manager",
    "ICON_ACCOUNT",
    "ICON_BURN",
    "ICON_CLOCK",
    "ICON_COLOR",
    "ICON_COLOUR",
    "ICON_EJECT",
    "ICON_ERROR",
    "ICON_FAVORITE",
    "ICON_FAVOURITE",
    "ICON_GROUP",
    "ICON_HELP",
    "ICON_HOME",
    "ICON_INFO",
    "ICON_NETWORK",
    "ICON_NOTE",
    "ICON_SETTINGS",
    "ICON_SWIRL",
    "ICON_SWITCH",
    "ICON_SYNC",
    "ICON_TRASH",
    "ICON_USER",
    "ICON_WEB",
    "MATCH_ALL",
    "MATCH_ALLCHARS",
    "MATCH_ATOM",
    "MATCH_CAPITALS",
    "MATCH_INITIALS",
    "MATCH_INITIALS_CONTAIN",
    "MATCH_INITIALS_STARTSWITH",
    "MATCH_STARTSWITH",
    "MATCH_SUBSTRING",
]
