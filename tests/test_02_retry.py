"""Testing automatic retry.

The auto-patch script should retry if the ZYPP library is locked by
another process or in case of failure to refresh a repository.
"""

import pytest
from conftest import AutoPatchCaller


no_wait = { 'retry': { 'max': "10", 'wait': "0" } }

def test_locked_at_start(tmpdir):
    """ZYPP library is locked when auto-patch is started.
    """
    with tmpdir.as_cwd():
        caller = AutoPatchCaller.get_caller("locked_start", config=no_wait)
        caller.run()
        caller.check_report()


def test_locked_in_between(tmpdir):
    """The auto-patch workflow is interrupted by intermittent locks.
    """
    with tmpdir.as_cwd():
        caller = AutoPatchCaller.get_caller("locked_between", config=no_wait)
        caller.run()
        caller.check_report()


def test_locked_final(tmpdir):
    """The auto-patch workflow is interrupted by a persistent lock,
    auto-patch eventually gives up waiting.
    """
    with tmpdir.as_cwd():
        caller = AutoPatchCaller.get_caller("locked_final", config=no_wait)
        caller.run(exitcode=7)
        # assert that no mail report has been sent:
        with pytest.raises(FileNotFoundError):
            caller.check_report()


def test_locked_complete(tmpdir):
    """A persistent lock blocks auto-patch completely, auto-patch
    eventually gives up waiting, not a single zypper succeeded.
    """
    with tmpdir.as_cwd():
        caller = AutoPatchCaller.get_caller("locked_complete", config=no_wait)
        caller.run(exitcode=7)
        # assert that no mail report has been sent:
        with pytest.raises(FileNotFoundError):
            caller.check_report()


def test_no_network_at_start(tmpdir):
    """Network failure when auto-patch is started.
    """
    with tmpdir.as_cwd():
        caller = AutoPatchCaller.get_caller("no_net_start", config=no_wait)
        caller.run()
        caller.check_report()


def test_no_network_complete(tmpdir):
    """A persistent network failure blocks auto-patch completely,
    auto-patch eventually gives up waiting, not a single zypper
    succeeded.
    """
    with tmpdir.as_cwd():
        caller = AutoPatchCaller.get_caller("no_net_complete", config=no_wait)
        caller.run(exitcode=106)
        # assert that no mail report has been sent:
        with pytest.raises(FileNotFoundError):
            caller.check_report()
