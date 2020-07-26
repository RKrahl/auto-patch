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

+ None

Optional library packages:

+ `setuptools_scm`_

  The version number is managed using this package.  All source
  distributions add a static text file with the version number and
  fall back using that if `setuptools_scm` is not available.  So this
  package is only needed to build out of the plain development source
  tree as cloned from GitHub.


Copyright and License
---------------------

Copyright 2020 Rolf Krahl

Licensed under the `Apache License`_, Version 2.0 (the "License"); you
may not use this file except in compliance with the License.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied.  See the License for the specific language governing
permissions and limitations under the License.


.. _zypper: https://github.com/openSUSE/zypper
.. _setuptools_scm: https://github.com/pypa/setuptools_scm/
.. _Apache License: https://www.apache.org/licenses/LICENSE-2.0
