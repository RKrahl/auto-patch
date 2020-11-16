#! python
"""Call zypper to install security and other system updates.
"""

from configparser import ConfigParser
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
from time import sleep

import systemd.journal

os.environ['LANG'] = "POSIX"
os.environ['LC_CTYPE'] = "en_US.UTF-8"

try:
    config_files = os.environ['AUTO_PATCH_CFG'].split(':')
except KeyError:
    config_files = "/etc/auto-patch.cfg"

config_defaults = {
    'mailreport': {
        'report': "on",
        'hostname': socket.getfqdn(),
        'user': getpass.getuser(),
        'mailfrom': "%(user)s@%(hostname)s",
        'mailto': "root@%(hostname)s",
        'subject': "auto-patch %(hostname)s",
        'mailhost': "localhost",
    },
    'retry': {
        'max': "30",
        'wait': "60",
    },
    'logging': {
        'journal_level': "INFO",
        'stderr_level': "DEBUG",
        'report_level': "WARNING",
    },
}
config = ConfigParser(comment_prefixes=('#', '!'))
for k, v in config_defaults.items():
    config[k] = v
config.read(config_files)

journal_level = config['logging'].get('journal_level')
journal_hdlr = systemd.journal.JournalHandler(level=journal_level)
logging.getLogger().addHandler(journal_hdlr)
if os.isatty(sys.stderr.fileno()):
    stderr_hdlr = logging.StreamHandler()
    stderr_hdlr.setLevel(config['logging'].get('stderr_level'))
    fmt = "%(levelname)s: %(message)s"
    stderr_hdlr.setFormatter(logging.Formatter(fmt=fmt))
    logging.getLogger().addHandler(stderr_hdlr)
logging.getLogger().setLevel(logging.DEBUG)
log = logging.getLogger(__name__)


class ZypperLockedError(Exception):
    def __init__(self):
        super().__init__("ZYPP library is locked")


class Zypper:

    _zypper = "/usr/bin/zypper"

    @classmethod
    def call(cls, args, stdout=None, retcodes=None):
        cmd = [cls._zypper] + args
        log.debug("run: %s", " ".join(cmd))
        stdout.flush()
        proc = subprocess.run(cmd, stdout=stdout, stderr=subprocess.PIPE,
                              universal_newlines=True)
        log.debug("return code from zypper: %d", proc.returncode)
        if proc.returncode == 7:
            raise ZypperLockedError()
        elif (proc.returncode != 0 and
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
    try_count = 0
    while True:
        try_count += 1
        try:
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
                log.info("patches successfully installed")
                if rc == 0 or rc == 102:
                    break
                elif rc == 103:
                    log.info("patch requires restart to "
                             "check again for more patches")
                    continue
            if not have_patches:
                return False
            rc = Zypper.ps(stdout=stdout)
            if rc == 102:
                log.warning("reboot is required after installing patches")
            return True
        except ZypperLockedError:
            if try_count < config['retry'].getint('max'):
                log.info("ZYPP library is locked.  Will try again ...")
                sleep(config['retry'].getint('wait'))
                continue
            else:
                log.error("ZYPP library is locked.  "
                          "Giving up after %d tries." % try_count)
                return have_patches

def exchandler(type, value, traceback):
    log.critical("%s: %s", type.__name__, value,
                 exc_info=(type, value, traceback))

if __name__ == "__main__":
    sys.excepthook = exchandler
    with tempfile.TemporaryFile(mode='w+t') as tmpf:
        report_hdlr = logging.StreamHandler(stream=tmpf)
        report_hdlr.setLevel(config['logging'].get('report_level'))
        report_hdlr.setFormatter(logging.Formatter(fmt="\n%(message)s"))
        logging.getLogger().addHandler(report_hdlr)
        if patch(stdout=tmpf):
            report_hdlr.flush()
            logging.getLogger().removeHandler(report_hdlr)
            report_hdlr.close()
            tmpf.seek(0)
            report = tmpf.read()
            log.debug(report)
            if config['mailreport'].getboolean('report'):
                msg = EmailMessage()
                msg.set_content(report)
                msg['From'] = config['mailreport'].get('mailfrom')
                msg['To'] = config['mailreport'].get('mailto')
                msg['Subject'] = config['mailreport'].get('subject')
                mailhost = config['mailreport'].get('mailhost')
                with smtplib.SMTP(mailhost) as smtp:
                    smtp.send_message(msg)
