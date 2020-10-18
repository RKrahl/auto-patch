#! python
"""Call zypper to install security and other system updates.
"""

from email.message import EmailMessage
import getpass
import logging
import os
import re
import smtplib
import socket
import subprocess
import sys
import tempfile

import systemd.journal

os.environ['LANG'] = "POSIX"
os.environ['LC_CTYPE'] = "en_US.UTF-8"

journal = systemd.journal.JournalHandler(level=logging.INFO)
logging.getLogger().addHandler(journal)
if os.isatty(sys.stderr.fileno()):
    stderr = logging.StreamHandler()
    stderr.setLevel(logging.DEBUG)
    stderr.setFormatter(logging.Formatter(fmt="%(levelname)s: %(message)s"))
    logging.getLogger().addHandler(stderr)
logging.getLogger().setLevel(logging.DEBUG)
log = logging.getLogger(__name__)

host = socket.getfqdn()
mailfrom = "%s@%s" % (getpass.getuser(), host)
mailto = os.environ.get('MAILTO', None) or ("root@%s" % host)
mailsubject = "auto-patch %s" % host


class Zypper:

    _zypper = "/usr/bin/zypper"

    @classmethod
    def call(cls, args, stdout=None, retcodes=None):
        cmd = [cls._zypper] + args
        log.debug("run: %s", " ".join(cmd))
        proc = subprocess.run(cmd, stdout=stdout, stderr=subprocess.PIPE,
                              universal_newlines=True)
        log.debug("return code from zypper: %d", proc.returncode)
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
        # ps: list processes using deleted files
        # 0: ok
        # 102: reboot required
        args = ["--quiet", "ps"]
        return cls.call(args, stdout=stdout, retcodes={102})


def patch(stdout=None):
    check_line_re = r"^\d+ patch(:?es)? needed \(\d+ security patch(:?es)?\)$"
    check_line_pattern = re.compile(check_line_re, flags=re.M)
    have_patches = False
    while True:
        p = stdout.tell()
        if Zypper.patch_check(stdout=stdout) == 0:
            log.debug("no patches needed")
            break
        stdout.seek(p)
        m = check_line_pattern.search(stdout.read())
        if m:
            log.info(m.group(0))
        else:
            log.info("patches are needed")
        have_patches = True
        Zypper.list_patches(stdout=stdout)
        rc = Zypper.patch(stdout=stdout)
        if rc == 0:
            log.debug("patches successfully installed")
            break
        elif rc == 102:
            log.debug("patches successfully installed, patch requires reboot")
            break
        elif rc == 103:
            log.debug("patches successfully installed, "
                      "need to check again for more patches")
            continue
    if not have_patches:
        return False
    rc = Zypper.ps(stdout=stdout)
    if rc == 102:
        # zypper ps reports that reboot is required.
        print("\nreboot is required", file=stdout)
        log.warning("reboot is required after installing patches")
    return True

def exchandler(type, value, traceback):
    log.critical("%s: %s", type.__name__, value,
                 exc_info=(type, value, traceback))

if __name__ == "__main__":
    sys.excepthook = exchandler
    with tempfile.TemporaryFile(mode='w+t') as tmpf:
        if patch(stdout=tmpf):
            tmpf.seek(0)
            report = tmpf.read()
            log.debug(report)
            msg = EmailMessage()
            msg.set_content(report)
            msg['From'] = mailfrom
            msg['To'] = mailto
            msg['Subject'] = mailsubject
            with smtplib.SMTP('localhost') as smtp:
                smtp.send_message(msg)
