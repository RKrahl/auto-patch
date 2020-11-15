import argparse
from configparser import ConfigParser
import json
from multiprocessing import Process
import os
from pathlib import Path
import pickle
import subprocess
import pytest


test_dir = Path(__file__).parent
script_dir = Path(os.environ['BUILD_SCRIPTS_DIR'])

os.environ['AUTO_PATCH_CFG'] = "auto-patch.cfg"


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
    _zypper_result_data = None

    @classmethod
    def _get_zypper_result_data(cls):
        if not cls._zypper_result_data:
            datafile = test_dir / "zypper-result-data.json"
            with datafile.open("rt") as f:
                cls._zypper_result_data = json.load(f)
        return cls._zypper_result_data

    @classmethod
    def get_caller(cls, case, config=None):
        data = cls._get_zypper_result_data()
        zypper_results = [ ZypperResult(**args) for args in data[case] ]
        return cls(zypper_results, config)

    def _create_config(self, config):
        if config is None:
            config = { 'retry': { 'wait': "0" } }
        cp = ConfigParser()
        for k in ('mailreport', 'retry'):
            cp[k] = {}
        for k, v in config.items():
            cp[k] = v
        with open("auto-patch.cfg", 'wt') as f:
            cp.write(f)

    def __init__(self, zypper_results, config=None):
        self._create_config(config)
        parser = argparse.ArgumentParser()
        parser.add_argument('--quiet', action='store_true')
        parser.add_argument('--non-interactive', action='store_true')
        parser.add_argument('subcmd')
        parser.add_argument('--skip-interactive', action='store_true')
        self.zypper_arg_parser = parser
        self.zypper_results = zypper_results
        self.results_iter = iter(self.zypper_results)

    def _mock_subprocess_run(self, cmd, stdout=None, **kwargs):
        zypp_res = next(self.results_iter)
        assert Path(cmd[0]).name == "zypper"
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
            with open("report.pickle", "wb") as f:
                pickle.dump(msg, f)

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

    def check_report(self):
        with open("report.pickle", "rb") as f:
            msg = pickle.load(f)
        body = msg.get_content()
        idx = 0
        for res in self.zypper_results:
            idx = body.find(res.stdout, idx)
            assert idx >= 0
            idx += len(res.stdout)
        return msg
