import argparse
from multiprocessing import Process
import os
from pathlib import Path
import subprocess
import pytest


script_dir = Path(os.environ['BUILD_SCRIPTS_DIR'])


class ZypperResult:
    """Represent the result of one mock zypper call in AutoPatchCaller.
    """
    def __init__(self, cmd, returncode=0, stdout="", stderr=""):
        self.cmd = cmd
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

class AutoPatchCaller:
    """Execute the auto-patch.py script in a prepared Python interpreter.

    We can't actually run zypper or send a mail report in the tests.
    So we use a monkey patched Python interpreter to mock up the
    relations to the outside world for the script.
    """

    auto_patch_path = script_dir / "auto-patch.py"

    def __init__(self, zypper_results):
        parser = argparse.ArgumentParser()
        parser.add_argument('--quiet', action='store_true')
        parser.add_argument('--non-interactive', action='store_true')
        parser.add_argument('subcmd')
        parser.add_argument('--skip-interactive', action='store_true')
        self.zypper_arg_parser = parser
        self.zypper_results = list(zypper_results)

    def _mock_subprocess_run(self, cmd, stdout=None, **kwargs):
        zypp_res = self.zypper_results.pop(0)
        args = self.zypper_arg_parser.parse_args(args=cmd[1:])
        assert args.subcmd == zypp_res.cmd
        stdout.write(zypp_res.stdout)
        return subprocess.CompletedProcess(cmd, zypp_res.returncode,
                                           stderr=zypp_res.stderr)

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

    def _patch_and_call(self):
        import subprocess
        import smtplib
        subprocess.run = self._mock_subprocess_run
        smtplib.SMTP = self._mock_smtp
        with self.auto_patch_path.open("rt") as script:
            exec(script.read(), dict(__name__="__main__"))

    def run(self):
        p = Process(target=self._patch_and_call)
        p.start()
        p.join()
        assert p.exitcode == 0
