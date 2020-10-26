from multiprocessing import Process
import os
from pathlib import Path
import subprocess
import pytest


auto_patch_path = Path(os.environ['BUILD_SCRIPTS_DIR']) / "auto-patch.py"


def _mock_subprocess_run(cmd, **kwargs):
    with open("zypper-call.log", "at") as f:
        print(" ".join(cmd), file=f)
    return subprocess.CompletedProcess(cmd, 0, stderr="")

class _mock_smtp:
    def __init__(self, host='', **kwargs):
        pass
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def send_message(self, msg, **kwargs):
        with open("report.msg", "wt") as f:
            print(msg.as_string(), file=f)


def call_auto_patch():
    """Execute the auto-patch.py script in a prepared Python interpreter.

    We can't actually run zypper or send a mail report in the tests.
    So we use a monkey patched Python interpreter to mock up the
    relations to the outside world for the script.
    """
    def _patch_and_call():
        import subprocess
        import smtplib
        subprocess.run = _mock_subprocess_run
        smtplib.SMTP = _mock_smtp
        with auto_patch_path.open("rt") as script:
            exec(script.read(), dict(__name__="__main__"))

    p = Process(target=_patch_and_call)
    p.start()
    p.join()
