"""Consider scenarios when the ZYPP library is locked.
"""

import pytest
from conftest import AutoPatchCaller


def test_locked_at_start(tmpdir):
    """ZYPP library is locked when auto-patch is started.
    """
    with tmpdir.as_cwd():
        caller = AutoPatchCaller.get_caller("locked_start")
        caller.run()
        caller.check_report()


def test_locked_in_between(tmpdir):
    """The auto-patch workflow is interrupted by intermittent locks.
    """
    with tmpdir.as_cwd():
        caller = AutoPatchCaller.get_caller("locked_between")
        caller.run()
        caller.check_report()


def test_locked_final(tmpdir):
    """The auto-patch workflow is interrupted by a persistent lock,
    auto-patch eventually gives up waiting.
    """
    with tmpdir.as_cwd():
        caller = AutoPatchCaller.get_caller("locked_final")
        caller.run()
        caller.check_report()


def test_locked_complete(tmpdir):
    """A persistent lock blocks auto-patch completely, auto-patch
    eventually gives up waiting, not a single zypper succeeded.  Note
    that no report is sent, because auto-patch couldn't even check the
    presence of available patches.
    """
    with tmpdir.as_cwd():
        caller = AutoPatchCaller.get_caller("locked_complete")
        caller.run()
        # assert that no mail report has been sent:
        with pytest.raises(FileNotFoundError):
            caller.check_report()
