import pytest


def test_no_patches(tmpdir, auto_patch_caller):
    """No patches available.
    """
    with tmpdir.as_cwd():
        auto_patch_caller.run()


def test_sec_patches(tmpdir, auto_patch_caller):
    """Some security patches available.
    """
    with tmpdir.as_cwd():
        auto_patch_caller.run()
