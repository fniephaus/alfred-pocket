#!/usr/bin/env python3
# This module relies on Notificator created by Vítor Galvão
# See https://github.com/vitorgalvao/notificator

"""
Post notifications via the macOS Notification Center.

The main API is a single function, :func:`~workflow.notify.notify`.

It works by copying a simple application to your workflow's cache
directory.
"""

import os
import subprocess

from workflow import Workflow

wf = Workflow()
logger = wf.logger


def notify(title="", text="", sound=""):
    """Post notification via Notificator helper.

    Args:
        title (str, optional): Notification title.
        text (str, optional): Notification body text.
        sound (str, optional): Name of sound to play (from ``/System/Library/Sounds``).

    Raises:
        ValueError: Raised if both ``title`` and ``text`` are empty.

    Returns:
        bool: ``True`` if notification was posted, else ``False``.
    """
    if text == "":
        raise ValueError("A message is mandatory.")

    notificator = os.path.join(os.path.dirname(__file__), "notificator")
    retcode = subprocess.run(
        [notificator, "--title", title, "--message", text, "--sound", sound], check=True
    ).returncode

    if retcode == 0:
        return True

    logger.error("Notificator exited with status %s", retcode)
    return False
