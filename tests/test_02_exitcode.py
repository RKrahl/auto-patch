"""Testing exit code on error.

The auto-patch script should return a non-zeror exit code on error.
In particular, it should return the exit code from zypper if the
zypper call yields an error result.
"""

import pytest
from conftest import AutoPatchCaller


def test_error_syntax(tmpdir):
    """A syntax error in the zypper call.

    This would be an internal error in the auto-patch script.
    """
    with tmpdir.as_cwd():
        caller = AutoPatchCaller.get_caller("err_syntax")
        caller.run(exitcode=2)
        # assert that no mail report has been sent:
        with pytest.raises(FileNotFoundError):
            caller.check_report()


def test_error_permission(tmpdir):
    """Insufficient privileges calling zypper.

    This is a normal error that occurs if the auto-patch script is run
    by a user other than root.
    """
    with tmpdir.as_cwd():
        caller = AutoPatchCaller.get_caller("err_permissions")
        caller.run(exitcode=5)
        # assert that no mail report has been sent:
        with pytest.raises(FileNotFoundError):
            caller.check_report()


def test_error_scripterr(tmpdir):
    """A %post() scriptlet from one of the packages failed.

    This may happen, though rarely.  The auto-patch should report the
    error, but still deliver a report.
    """
    # FIXME: verify that the error is logged
    with tmpdir.as_cwd():
        caller = AutoPatchCaller.get_caller("err_scripterr")
        caller.run(exitcode=107)
        caller.check_report()
