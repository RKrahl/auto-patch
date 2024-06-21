"""Automatically install security and other system updates

This package provides a script to call zypper to install security and
other system updates.  It also provides systemd unit files to
automatically call that script regularly.
"""

import setuptools
from setuptools import setup
import distutils.command.sdist
from distutils import log
from glob import glob
from pathlib import Path
import string
try:
    import distutils_pytest
    cmdclass = distutils_pytest.cmdclass
except (ImportError, AttributeError):
    cmdclass = dict()
try:
    import setuptools_scm
    version = setuptools_scm.get_version()
except (ImportError, LookupError):
    try:
        import _meta
        version = _meta.__version__
    except ImportError:
        log.warn("warning: cannot determine version number")
        version = "UNKNOWN"

docstring = __doc__


class meta(setuptools.Command):
    description = "generate meta files"
    user_options = []
    meta_template = '''
__version__ = "%(version)s"
'''
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        values = {
            'version': self.distribution.get_version(),
            'doc': docstring
        }
        with Path("_meta.py").open("wt") as f:
            print(self.meta_template % values, file=f)

# Note: Do not use setuptools for making the source distribution,
# rather use the good old distutils instead.
# Rationale: https://rhodesmill.org/brandon/2009/eby-magic/
class sdist(distutils.command.sdist.sdist):
    def run(self):
        self.run_command('meta')
        super().run()
        subst = {
            "version": self.distribution.get_version(),
            "url": self.distribution.get_url(),
            "description": docstring.split("\n")[0],
            "long_description": docstring.split("\n", maxsplit=2)[2].strip(),
        }
        for spec in glob("*.spec"):
            with Path(spec).open('rt') as inf:
                with Path(self.dist_dir, spec).open('wt') as outf:
                    outf.write(string.Template(inf.read()).substitute(subst))


with Path("README.rst").open("rt", encoding="utf8") as f:
    readme = f.read()

setup(
    name = "auto-patch",
    version = version,
    description = docstring.split("\n")[0],
    long_description = readme,
    url = "https://github.com/RKrahl/auto-patch",
    author = "Rolf Krahl",
    author_email = "rolf@rotkraut.de",
    license = "Apache-2.0",
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: System :: Systems Administration",
    ],
    python_requires = ">=3.6",
    install_requires = ["systemd"],
    packages = [],
    py_modules = [],
    scripts = ["scripts/auto-patch.py"],
    cmdclass = dict(cmdclass, sdist=sdist, meta=meta),
)
