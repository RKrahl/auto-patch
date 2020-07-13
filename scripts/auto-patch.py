#! python
"""Call zypper to install security and other system updates.
"""

import logging
import subprocess
import tempfile
import sys

_zypper = "/usr/bin/zypper"

def call_zypper(args, stdout=None, retcodes=None):
    cmd = [_zypper] + args
    proc = subprocess.run(cmd, stdout=stdout, stderr=subprocess.PIPE,
                          universal_newlines=True)
    if proc.returncode != 0 and not (retcodes and proc.returncode in retcodes):
        proc.check_returncode()
    return proc.returncode

def patch(stdout=None):
    # patch-check
    # 0: no patches needed
    # 100: patches available for installation
    # 101: security patches available for installation
    args = ["--quiet", "--non-interactive", "patch-check"]
    rc = call_zypper(args, stdout=stdout, retcodes={100, 101})
    if rc == 0:
        return False
    while True:
        # list-patches: add some more diagnostic info to the output
        args = ["--quiet", "--non-interactive", "list-patches"]
        rc = call_zypper(args, stdout=stdout)
        # patch: install patches
        # 0: ok
        # 102: successful installation, patch requires reboot
        # 103: successful installation, restart of package manager needed
        args = ["--quiet", "--non-interactive",
                "patch", "--skip-interactive"]
        rc = call_zypper(args, stdout=stdout, retcodes={102, 103})
        if rc == 0:
            break
        elif rc == 102:
            # should normally not happen, as we skipped
            # interactive patches.
            break
        elif rc == 103:
            continue
    # ps: lists all processes using deleted files
    args = ["--quiet", "ps"]
    rc = call_zypper(args, stdout=stdout)
    return True

if __name__ == "__main__":
    with tempfile.TemporaryFile(mode='w+t') as tmpf:
        if not patch(stdout=tmpf):
            return
        tmpf.seek(0)
        output = tmpf.read()
        print(output)
