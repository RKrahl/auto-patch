"""Test setting configuration in the configuration file.
"""

import getpass
import socket
import os
from pathlib import Path
import shutil
import pytest
from conftest import AutoPatchCaller


hostname = socket.getfqdn()
user = getpass.getuser()
default_mailfrom = "%s@%s" % (user, hostname)
default_mailto = "root@%s" % (hostname)
default_mailsubject = "auto-patch %s" % (hostname)
default_mailhost = "localhost"


def test_default_config(tmpdir):
    """Default config file as installed with the package.
    The default file has all options commented out, so built-in
    defaults apply.
    """
    cfg_path = Path(__file__).parent / ".." / "etc" / "auto-patch.cfg"
    with tmpdir.as_cwd():
        caller = AutoPatchCaller.get_caller("sec_patches")
        shutil.copyfile(str(cfg_path), "auto-patch.cfg")
        caller.run()
        mailhost, msg = caller.check_report()
        assert mailhost == default_mailhost
        assert msg['from'] == default_mailfrom
        assert msg['to'] == default_mailto
        assert msg['subject'] == default_mailsubject

def test_no_config(tmpdir):
    """No config file present.
    The script should take this gracefully and apply the built-in defaults.
    """
    with tmpdir.as_cwd():
        caller = AutoPatchCaller.get_caller("sec_patches")
        os.unlink("auto-patch.cfg")
        caller.run()
        mailhost, msg = caller.check_report()
        assert mailhost == default_mailhost
        assert msg['from'] == default_mailfrom
        assert msg['to'] == default_mailto
        assert msg['subject'] == default_mailsubject

def test_config_mail_addresses(tmpdir):
    """Configure mail from and to.
    """
    mailfrom = "root@host.example.com"
    mailto = "admin@example.com"
    with tmpdir.as_cwd():
        cfg = { 'mailreport': {'mailfrom': mailfrom, 'mailto': mailto} }
        caller = AutoPatchCaller.get_caller("sec_patches", config=cfg)
        caller.run()
        mailhost, msg = caller.check_report()
        assert mailhost == default_mailhost
        assert msg['from'] == mailfrom
        assert msg['to'] == mailto
        assert msg['subject'] == default_mailsubject

def test_config_mail_subject(tmpdir):
    """Configure mail subject.
    """
    subject = "auto-patch report"
    with tmpdir.as_cwd():
        cfg = { 'mailreport': {'subject': subject} }
        caller = AutoPatchCaller.get_caller("sec_patches", config=cfg)
        caller.run()
        mailhost, msg = caller.check_report()
        assert mailhost == default_mailhost
        assert msg['from'] == default_mailfrom
        assert msg['to'] == default_mailto
        assert msg['subject'] == subject

def test_config_mailhost(tmpdir):
    """Configure mailhost.
    """
    mailhost = "mailhub.example.com"
    with tmpdir.as_cwd():
        cfg = { 'mailreport': {'mailhost': mailhost} }
        caller = AutoPatchCaller.get_caller("sec_patches", config=cfg)
        caller.run()
        mailhost, msg = caller.check_report()
        assert mailhost == mailhost
        assert msg['from'] == default_mailfrom
        assert msg['to'] == default_mailto
        assert msg['subject'] == default_mailsubject

@pytest.mark.parametrize("flag", ["1", "yes", "true", "on"])
def test_config_mailreport_on(tmpdir, flag):
    """Explicitely switch on mail report in the configuration.

    This is the default, so we won't get any different behavior.
    Try out different representations of the affirmative value.
    """
    with tmpdir.as_cwd():
        cfg = { 'mailreport': {'report': flag} }
        caller = AutoPatchCaller.get_caller("sec_patches", config=cfg)
        caller.run()
        mailhost, msg = caller.check_report()
        assert mailhost == default_mailhost
        assert msg['from'] == default_mailfrom
        assert msg['to'] == default_mailto
        assert msg['subject'] == default_mailsubject

@pytest.mark.parametrize("flag", ["0", "no", "false", "off"])
def test_config_mailreport_off(tmpdir, flag):
    """Explicitely switch off mail report in the configuration.

    Try out different representations of the negative value.
    """
    with tmpdir.as_cwd():
        cfg = { 'mailreport': {'report': flag} }
        caller = AutoPatchCaller.get_caller("sec_patches", config=cfg)
        caller.run()
        # assert that no mail report has been sent:
        with pytest.raises(FileNotFoundError):
            caller.check_report()
