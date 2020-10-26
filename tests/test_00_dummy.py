import pytest
from conftest import call_auto_patch

def test_dummy(tmpdir):
    with tmpdir.as_cwd():
        call_auto_patch()
