#! python
"""Call zypper to install security and other system updates.
"""

import logging
import subprocess
import tempfile
import sys


class Zypper:

    _zypper = "/usr/bin/zypper"

    @classmethod
    def call(cls, args, stdout=None, retcodes=None):
        cmd = [cls._zypper] + args
        proc = subprocess.run(cmd, stdout=stdout, stderr=subprocess.PIPE,
                              universal_newlines=True)
        if (proc.returncode != 0 and
            not (retcodes and proc.returncode in retcodes)):
            proc.check_returncode()
        return proc.returncode

    @classmethod
    def patch_check(cls, stdout=None):
        # patch-check
        # 0: no patches needed
        # 100: patches available for installation
        # 101: security patches available for installation
        args = ["--quiet", "--non-interactive", "patch-check"]
        return cls.call(args, stdout=stdout, retcodes={100, 101})

    @classmethod
    def list_patches(cls, stdout=None):
        args = ["--quiet", "--non-interactive", "list-patches"]
        return cls.call(args, stdout=stdout)

    @classmethod
    def patch(cls, stdout=None):
        # patch: install patches
        # 0: ok
        # 102: successful installation, patch requires reboot
        # 103: successful installation, restart of package manager needed
        args = ["--quiet", "--non-interactive", "patch", "--skip-interactive"]
        return cls.call(args, stdout=stdout, retcodes={102, 103})

    @classmethod
    def ps(cls, stdout=None):
        args = ["--quiet", "ps"]
        return cls.call(args, stdout=stdout)


def patch(stdout=None):
    if Zypper.patch_check(stdout=stdout) == 0:
        return False
    while True:
        Zypper.list_patches(stdout=stdout)
        rc = Zypper.patch(stdout=stdout)
        if rc == 0:
            break
        elif rc == 102:
            # patch requires reboot.
            # should normally not happen, as we skipped interactive patches.
            break
        elif rc == 103:
            # restart of package manager needed.
            continue
    Zypper.ps(stdout=stdout)
    return True

if __name__ == "__main__":
    with tempfile.TemporaryFile(mode='w+t') as tmpf:
        if not patch(stdout=tmpf):
            return
        tmpf.seek(0)
        output = tmpf.read()
        print(output)
