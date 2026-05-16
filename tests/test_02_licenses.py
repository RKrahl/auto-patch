"""Special case: a patch requires accepting a third party license.

A patch for a non-free package requires agreement with the terms of
the license.  By default, the zypper patch call fails with
ZypperLibraryError in non-interactive mode.  This can either be fixed
by manual intervention by the admin or by setting the
auto_agree_with_licenses configuration flag to yes.
"""

import pytest
from conftest import AutoPatchCaller


def test_license_default(tmpdir):
    """Default configuration.

    The patch command fails with ZypperLibraryError.
    """
    with tmpdir.as_cwd():
        caller = AutoPatchCaller.get_caller("no_license_consent")
        caller.run(exitcode=4)
        caller.check_report(extra_msg="ERROR:")


@pytest.mark.parametrize("flag", ["0", "no", "false", "off"])
def test_license_auto_agree_no(tmpdir, flag):
    """Explicitely switch off auto_agree_with_licenses.

    This is the default, so we won't get any different behavior.
    Try out different representations of the negative value.
    """
    with tmpdir.as_cwd():
        cfg = { 'zypper': {'auto_agree_with_licenses': flag} }
        caller = AutoPatchCaller.get_caller("no_license_consent", config=cfg)
        caller.run(exitcode=4)
        caller.check_report(extra_msg="ERROR:")


@pytest.mark.parametrize("flag", ["1", "yes", "true", "on"])
def test_license_auto_agree_yes(tmpdir, flag):
    """Explicitely switch on auto_agree_with_licenses.

    In this case, the patch is applied successfully.
    Try out different representations of the affirmative value.
    """
    with tmpdir.as_cwd():
        cfg = { 'zypper': {'auto_agree_with_licenses': flag} }
        caller = AutoPatchCaller.get_caller("auto_license_consent", config=cfg)
        caller.run()
        caller.check_report()
