Changelog
=========


1.1.0 (not yet released)
~~~~~~~~~~~~~~~~~~~~~~~~

New features
------------

+ `#6`_, `#11`_: add a configuration file.
+ `#3`_, `#5`_: add logging.
+ `#9`_, `#13`_: review handling of the exit code from zypper and
  provide intelligible error messages.  Retry the zypper call on
  failure to refresh a repository.

Misc
----

+ `#7`_, `#10`_: add a test suite.

Bug fixes and minor changes
---------------------------

+ `#12`_: review build tool chain.

.. _#3: https://github.com/RKrahl/auto-patch/issues/3
.. _#5: https://github.com/RKrahl/auto-patch/pull/5
.. _#6: https://github.com/RKrahl/auto-patch/issues/6
.. _#7: https://github.com/RKrahl/auto-patch/issues/7
.. _#9: https://github.com/RKrahl/auto-patch/issues/9
.. _#10: https://github.com/RKrahl/auto-patch/pull/10
.. _#11: https://github.com/RKrahl/auto-patch/pull/11
.. _#12: https://github.com/RKrahl/auto-patch/pull/12
.. _#13: https://github.com/RKrahl/auto-patch/pull/13


1.0.3 (2020-10-24)
~~~~~~~~~~~~~~~~~~

Bug fixes and minor changes
---------------------------

+ Fix a syntax error.


1.0.2 (2020-10-20)
~~~~~~~~~~~~~~~~~~

.. warning::
   Version 1.0.2 is broken, don't use it!

Bug fixes and minor changes
---------------------------

+ `#2`_, `#4`_: retry if the ZYPP library is locked.

.. _#2: https://github.com/RKrahl/auto-patch/issues/2
.. _#4: https://github.com/RKrahl/auto-patch/pull/4


1.0.1 (2020-08-19)
~~~~~~~~~~~~~~~~~~

Bug fixes and minor changes
---------------------------

+ `#1`_: fix for non-zero exit status from zypper ps.

+ Add dependency on lsof in the spec file.

+ Add Changelog.

.. _#1: https://github.com/RKrahl/auto-patch/pull/1


1.0 (2020-07-26)
~~~~~~~~~~~~~~~~

+ Initial version
