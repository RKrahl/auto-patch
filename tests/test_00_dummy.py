import pytest
from conftest import AutoPatchCaller

def test_dummy(tmpdir):
    with tmpdir.as_cwd():
        caller = AutoPatchCaller()
        caller.run()
