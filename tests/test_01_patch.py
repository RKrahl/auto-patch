import pytest
from conftest import AutoPatchCaller, ZypperResult


msg_check_no = """
0 patches needed (0 security patches)
"""
msg_check_sec = """
Category    | Patches
------------+--------
security    | 2
recommended | 1

3 patches needed (2 security patches)
"""
msg_list_sec = """
Repository             | Name               | Category    | Severity  | Interactive | Status | Since | Summary
-----------------------+--------------------+-------------+-----------+-------------+--------+-------+-------------------------------------
Main Update Repository | openSUSE-2020-1743 | security    | moderate  | ---         | needed | -     | Security update for gnutls
Main Update Repository | openSUSE-2020-1744 | security    | important | ---         | needed | -     | Security update for freetype2
Main Update Repository | openSUSE-2020-1745 | recommended | moderate  | ---         | needed | -     | Recommended update for yast2-network

3 patches needed (2 security patches)

"""
msg_patch_sec = """
The following 3 NEW patches are going to be installed:
  openSUSE-2020-1743 openSUSE-2020-1744 openSUSE-2020-1745

The following 15 packages are going to be upgraded:
  ft2demos ftbench ftdiff ftdump ftgamma ftgrid ftinspect ftlint ftmulti ftstring ftvalid ftview libfreetype6 libgnutls30 yast2-network

15 packages to upgrade.
Overall download size: 2.2 MiB. Already cached: 0 B. After the operation, additional 21.6 KiB will be used.
Continue? [y/n/v/...? shows all options] (y): y

"""

def test_no_patches(tmpdir):
    """No patches available.
    """
    zypper_results = [
        ZypperResult("patch-check", returncode=0, stdout=msg_check_no),
    ]
    with tmpdir.as_cwd():
        caller = AutoPatchCaller(zypper_results)
        caller.run()


def test_sec_patches(tmpdir):
    """Some security patches available.
    """
    zypper_results = [
        ZypperResult("patch-check", returncode=101, stdout=msg_check_sec),
        ZypperResult("list-patches", stdout=msg_list_sec),
        ZypperResult("patch", stdout=msg_patch_sec),
        ZypperResult("ps"),
    ]
    with tmpdir.as_cwd():
        caller = AutoPatchCaller(zypper_results)
        caller.run()
