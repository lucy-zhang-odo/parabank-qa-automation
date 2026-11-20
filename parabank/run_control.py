"""Stopping a test run cleanly when the shared demo site is down or rate-limiting us,
with an error annotation on GitHub Actions so the reason is visible on the run page."""
import os
import sys

import pytest


def annotate(config, title: str, message: str):
    """On GitHub Actions, show the message as an error annotation on the run page."""
    if os.environ.get("GITHUB_ACTIONS"):
        with config.pluginmanager.getplugin("capturemanager").global_and_fixture_disabled():
            sys.stdout.write(f"::error title={title}::{message}\n")
            sys.stdout.flush()


def stop(config, message: str):
    """End the run without running tests."""
    annotate(config, "ParaBank demo unavailable", message)
    pytest.exit(message, returncode=3)


def stop_after_this_test(session, message: str):
    """The demo site started rate-limiting during the run: stop instead of letting every
    remaining test fail (or wait for a timeout) for the same reason."""
    if not session.shouldstop:
        annotate(session.config, "ParaBank demo rate-limited", message)
        session.shouldstop = message
