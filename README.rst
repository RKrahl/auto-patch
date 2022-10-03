|gh-test| |pypi|

.. |gh-test| image:: https://img.shields.io/github/workflow/status/RKrahl/auto-patch/Run%20Test
   :target: https://github.com/RKrahl/auto-patch/actions/workflows/run-tests.yaml
   :alt: GitHub Workflow Status

.. |pypi| image:: https://img.shields.io/pypi/v/auto-patch
   :target: https://pypi.org/project/auto-patch/
   :alt: PyPI version

Automatically install security and other system updates
=======================================================

This package provides a script to call zypper to install security and
other system updates.  It also provides systemd unit files to
automatically call that script regularly.

Since the script depends on zypper, it will probably only work for
SUSE distributions (openSUSE and SLES).


System requirements
-------------------

Python:

+ Python 3.5 or newer.

External programs:

+ `zypper`_

Required library packages:

+ `setuptools`_

+ `python-systemd`_

Optional library packages:

+ `setuptools_scm`_

  The version number is managed using this package.  All source
  distributions add a static text file with the version number and
  fall back using that if `setuptools_scm` is not available.  So this
  package is only needed to build out of the plain development source
  tree as cloned from GitHub.

+ `pytest`_ >= 3.0

  Only needed to run the test suite.

+ `distutils-pytest`_

  Only needed to run the test suite.


Copyright and License
---------------------

Copyright 2020–2022 Rolf Krahl

Licensed under the `Apache License`_, Version 2.0 (the "License"); you
may not use this file except in compliance with the License.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied.  See the License for the specific language governing
permissions and limitations under the License.


.. _zypper: https://github.com/openSUSE/zypper
.. _setuptools: https://github.com/pypa/setuptools/
.. _python-systemd: https://github.com/systemd/python-systemd
.. _setuptools_scm: https://github.com/pypa/setuptools_scm
.. _pytest: https://pytest.org/
.. _distutils-pytest: https://github.com/RKrahl/distutils-pytest
.. _Apache License: https://www.apache.org/licenses/LICENSE-2.0
