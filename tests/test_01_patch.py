"""Some standard scenarios applying patches with auto-patch.py.
"""

import pytest
from conftest import AutoPatchCaller


def test_no_patches(tmpdir):
    """No patches available.
    """
    with tmpdir.as_cwd():
        caller = AutoPatchCaller.get_caller("no_patches")
        caller.run()
        # assert that no mail report has been sent:
        with pytest.raises(FileNotFoundError):
            caller.check_report()


def test_rec_patches(tmpdir):
    """Some recommended patches available, but no security patches.
    """
    with tmpdir.as_cwd():
        caller = AutoPatchCaller.get_caller("rec_patches")
        caller.run()
        caller.check_report()


def test_sec_patches(tmpdir):
    """Some security patches available.
    """
    with tmpdir.as_cwd():
        caller = AutoPatchCaller.get_caller("sec_patches")
        caller.run()
        caller.check_report()


def test_zypp_patches(tmpdir):
    """A patches affects the package manager itself, restart patch required.
    """
    with tmpdir.as_cwd():
        caller = AutoPatchCaller.get_caller("zypp_patches")
        caller.run()
        caller.check_report()


def test_patch_psproc(tmpdir):
    """After applying patches, 'zypper ps' reports processes needing restart.
    """
    with tmpdir.as_cwd():
        caller = AutoPatchCaller.get_caller("patch_psproc")
        caller.run()
        caller.check_report()


def test_patch_psreboot(tmpdir):
    """After applying patches, 'zypper ps' reports reboot is needed.
    """
    with tmpdir.as_cwd():
        caller = AutoPatchCaller.get_caller("patch_psreboot")
        caller.run()
        caller.check_report()
