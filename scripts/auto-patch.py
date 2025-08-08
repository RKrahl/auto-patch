#! python
"""Call zypper to install security and other system updates.
"""

from configparser import ConfigParser
from contextlib import contextmanager
from email.message import EmailMessage
import getpass
import logging
import os
import re
import smtplib
import socket
import subprocess
from subprocess import CalledProcessError
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

def setup_logging(cfg):
    root = logging.getLogger()
    journal_level = cfg.get('journal_level')
    journal_hdlr = systemd.journal.JournalHandler(level=journal_level)
    root.addHandler(journal_hdlr)
    if os.isatty(sys.stderr.fileno()):
        stderr_hdlr = logging.StreamHandler()
        stderr_hdlr.setLevel(cfg.get('stderr_level'))
        fmt = "%(levelname)s: %(message)s"
        stderr_hdlr.setFormatter(logging.Formatter(fmt=fmt))
        root.addHandler(stderr_hdlr)
    root.setLevel(logging.DEBUG)

@contextmanager
def logging_add_report(cfg, stream):
    root = logging.getLogger()
    report_hdlr = logging.StreamHandler(stream=stream)
    report_hdlr.setLevel(cfg.get('report_level'))
    fmt = "\n%(levelname)s: %(message)s"
    report_hdlr.setFormatter(logging.Formatter(fmt=fmt))
    root.addHandler(report_hdlr)
    try:
        yield None
    finally:
        report_hdlr.flush()
        root.removeHandler(report_hdlr)
        report_hdlr.close()

log = logging.getLogger(__name__)


class ZypperExitException(CalledProcessError):
    """Represent a particular non-zero exit code from zypper.
    """
    ExitCode = 0
    Message = None
    _SubClasses = dict()

    @classmethod
    def check_returncode(cls, proc):
        """Raise the appropriate exception if the exit code is non-zero."""
        if proc.returncode:
            try:
                ExcClass = cls._SubClasses[proc.returncode]
            except KeyError:
                raise CalledProcessError(proc.returncode, proc.args,
                                         proc.stdout, proc.stderr) from None
            raise ExcClass(proc.args, proc.stdout, proc.stderr)

    @classmethod
    def register_exit_code(cls, subcls):
        """A class decorator to register the exit code for a subclass.
        """
        assert issubclass(subcls, cls)
        assert subcls.ExitCode and subcls.ExitCode not in cls._SubClasses
        cls._SubClasses[subcls.ExitCode] = subcls
        return subcls

    def __init__(self, cmd, stdout=None, stderr=None):
        if not self.ExitCode:
            # This is an abstract class that may not be instantiated.
            # Derived classes must override the class variable
            # ExitCode.
            raise NotImplementedError
        super().__init__(self.ExitCode, cmd, stdout, stderr)

    def __str__(self):
        if not self.Message:
            # This is an abstract class.  Derived classes must
            # override the class variable Message.
            raise NotImplementedError
        return self.Message

@ZypperExitException.register_exit_code
class ZypperBugError(ZypperExitException):
    ExitCode = 1
    Message = "Unexpected situation, probably a bug in zypper"

@ZypperExitException.register_exit_code
class ZypperSyntaxError(ZypperExitException):
    ExitCode = 2
    Message = "Syntax error in the zypper call"

@ZypperExitException.register_exit_code
class ZypperInvalidArgsError(ZypperExitException):
    ExitCode = 3
    Message = "Invalid arguments in the zypper call"

@ZypperExitException.register_exit_code
class ZypperLibraryError(ZypperExitException):
    ExitCode = 4
    Message = "Problem reported by ZYPP library"

@ZypperExitException.register_exit_code
class ZypperPrivilegesError(ZypperExitException):
    ExitCode = 5
    Message = "Insufficient privileges calling zypper"

@ZypperExitException.register_exit_code
class ZypperNoReposError(ZypperExitException):
    ExitCode = 6
    Message = "No repositories defined in zypper"

@ZypperExitException.register_exit_code
class ZypperLockedError(ZypperExitException):
    ExitCode = 7
    Message = "ZYPP library is locked"

@ZypperExitException.register_exit_code
class ZypperCommitError(ZypperExitException):
    ExitCode = 8
    Message = "Error during installation or removal of packages"

@ZypperExitException.register_exit_code
class ZypperPatchesAvailable(ZypperExitException):
    ExitCode = 100
    Message = "Patches available for installation"

@ZypperExitException.register_exit_code
class ZypperSecurityPatchesAvailable(ZypperExitException):
    ExitCode = 101
    Message = "Security patches available for installation"

@ZypperExitException.register_exit_code
class ZypperRebootNeeded(ZypperExitException):
    ExitCode = 102
    Message = "Installation of a patch requires reboot"

@ZypperExitException.register_exit_code
class ZypperRestartNeeded(ZypperExitException):
    ExitCode = 103
    Message = "Installation of a patch requires restart of package manager"

@ZypperExitException.register_exit_code
class ZypperCapabilityNotFound(ZypperExitException):
    ExitCode = 104
    Message = ("Arguments does not match available or installed "
               "package names or capabilities")

@ZypperExitException.register_exit_code
class ZypperSignal(ZypperExitException):
    ExitCode = 105
    Message = "Exit of zypper after receiving a SIGINT or SIGTERM"

@ZypperExitException.register_exit_code
class ZypperReposSkipped(ZypperExitException):
    ExitCode = 106
    Message = "Some repo temporarily disabled because of failure to refresh"

@ZypperExitException.register_exit_code
class ZypperRPMScriptfailed(ZypperExitException):
    ExitCode = 107
    Message = "Some packages install script returned an error"


class Zypper:

    _zypper = "/usr/bin/zypper"

    @classmethod
    def call(cls, args, stdout=None):
        cmd = [cls._zypper] + args
        log.debug("run: %s", " ".join(cmd))
        stdout.flush()
        proc = subprocess.run(cmd, stdout=stdout, stderr=subprocess.PIPE,
                              universal_newlines=True)
        log.debug("return code from zypper: %d", proc.returncode)
        ZypperExitException.check_returncode(proc)

    @classmethod
    def patch_check(cls, stdout=None):
        args = ["--quiet", "--non-interactive", "patch-check"]
        return cls.call(args, stdout=stdout)

    @classmethod
    def list_patches(cls, stdout=None):
        args = ["--quiet", "--non-interactive", "list-patches"]
        return cls.call(args, stdout=stdout)

    @classmethod
    def patch(cls, stdout=None):
        args = ["--quiet", "--non-interactive", "patch", "--skip-interactive"]
        return cls.call(args, stdout=stdout)

    @classmethod
    def ps(cls, stdout=None):
        args = ["--quiet", "ps"]
        return cls.call(args, stdout=stdout)


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
                try:
                    Zypper.patch_check(stdout=stdout)
                    log.debug("no patches needed")
                    break
                except (ZypperPatchesAvailable, ZypperSecurityPatchesAvailable):
                    pass
                stdout.seek(p)
                m = check_line_pattern.search(stdout.read())
                if m:
                    log.info(m.group(0))
                else:
                    log.info("patches are needed")
                have_patches = True
                Zypper.list_patches(stdout=stdout)
                try:
                    Zypper.patch(stdout=stdout)
                    log.info("patches successfully installed")
                    break
                except ZypperRebootNeeded:
                    log.info("patches successfully installed")
                    break
                except ZypperRestartNeeded:
                    log.info("patch requires restart to "
                             "check again for more patches")
                    continue
            if not have_patches:
                return False
            try:
                Zypper.ps(stdout=stdout)
            except ZypperRebootNeeded:
                log.warning("reboot is required after installing patches")
            return True
        except (ZypperLockedError, ZypperReposSkipped) as err:
            if try_count < config['retry'].getint('max'):
                log.warning("%s.  Will try again ...", err)
                sleep(config['retry'].getint('wait'))
                continue
            else:
                err.Message += (".  Giving up after %d tries." % try_count)
                raise err

def make_report(logfile):
    logfile.seek(0)
    report = logfile.read()
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

def main():
    setup_logging(config['logging'])
    with tempfile.TemporaryFile(mode='w+t') as tmpf:
        exit_code = 0
        with logging_add_report(config['logging'], tmpf):
            try:
                have_patches = patch(stdout=tmpf)
            except (ZypperCommitError, ZypperRPMScriptfailed,
                    ZypperSignal) as err:
                log.error(err)
                exit_code = err.ExitCode
        if exit_code or have_patches:
            make_report(tmpf)
        return exit_code

if __name__ == "__main__":
    try:
        exit_code = main()
    except (ZypperPrivilegesError, ZypperNoReposError, ZypperLockedError,
            ZypperReposSkipped) as err:
        log.error(err)
        sys.exit(err.ExitCode)
    except ZypperExitException as err:
        log.critical("Internal error %s: %s", type(err).__name__, err,
                     exc_info=err)
        sys.exit(err.ExitCode)
    except Exception as err:
        log.critical("Internal error %s: %s", type(err).__name__, err,
                     exc_info=err)
        sys.exit(-1)
    sys.exit(exit_code)
