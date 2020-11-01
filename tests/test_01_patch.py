"""Some standard scenarios applying patches with auto-patch.py.
"""

import pytest


def test_no_patches(tmpdir, auto_patch_caller):
    """No patches available.
    """
    with tmpdir.as_cwd():
        auto_patch_caller.run()
        # assert that no mail report has been sent:
        with pytest.raises(FileNotFoundError):
            auto_patch_caller.check_report()


def test_rec_patches(tmpdir, auto_patch_caller):
    """Some recommended patches available, but no security patches.
    """
    with tmpdir.as_cwd():
        auto_patch_caller.run()
        auto_patch_caller.check_report()


def test_sec_patches(tmpdir, auto_patch_caller):
    """Some security patches available.
    """
    with tmpdir.as_cwd():
        auto_patch_caller.run()
        auto_patch_caller.check_report()


def test_zypp_patches(tmpdir, auto_patch_caller):
    """A patches affects the package manager itself, restart patch required.
    """
    with tmpdir.as_cwd():
        auto_patch_caller.run()
        auto_patch_caller.check_report()


def test_patch_psproc(tmpdir, auto_patch_caller):
    """After applying patches, 'zypper ps' reports processes needing restart.
    """
    with tmpdir.as_cwd():
        auto_patch_caller.run()
        auto_patch_caller.check_report()


def test_patch_psreboot(tmpdir, auto_patch_caller):
    """After applying patches, 'zypper ps' reports reboot is needed.
    """
    with tmpdir.as_cwd():
        auto_patch_caller.run()
        auto_patch_caller.check_report()
