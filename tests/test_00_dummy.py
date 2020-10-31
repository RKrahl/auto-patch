import pytest
from conftest import AutoPatchCaller, ZypperResult

def test_dummy(tmpdir):
    zypper_results = [
        ZypperResult("patch-check", returncode=0,
                     stdout="\n0 patches needed (0 security patches)\n")
    ]
    with tmpdir.as_cwd():
        caller = AutoPatchCaller(zypper_results)
        caller.run()
