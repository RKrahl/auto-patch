Changelog
=========


.. _changes-1_1_1:

1.1.1 (2025-08-09)
~~~~~~~~~~~~~~~~~~

Misc
----

+ `#14`_: drop support for Python 3.5.

Bug fixes and minor changes
---------------------------

+ `#15`_, `#18`_: Send a report also in the case of certain errors
  from zypper.
+ `#16`_, `#17`_: Review of the test framework.
+ `#19`_: Review build tool chain.

.. _#14: https://github.com/RKrahl/auto-patch/pull/14
.. _#15: https://github.com/RKrahl/auto-patch/issues/15
.. _#16: https://github.com/RKrahl/auto-patch/issues/16
.. _#17: https://github.com/RKrahl/auto-patch/pull/17
.. _#18: https://github.com/RKrahl/auto-patch/pull/18
.. _#19: https://github.com/RKrahl/auto-patch/pull/19


.. _changes-1_1_0:

1.1.0 (2022-10-03)
~~~~~~~~~~~~~~~~~~

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


.. _changes-1_0_3:

1.0.3 (2020-10-24)
~~~~~~~~~~~~~~~~~~

Bug fixes and minor changes
---------------------------

+ Fix a syntax error.


.. _changes-1_0_2:

1.0.2 (2020-10-20)
~~~~~~~~~~~~~~~~~~

.. warning::
   Version 1.0.2 is broken, don't use it!

Bug fixes and minor changes
---------------------------

+ `#2`_, `#4`_: retry if the ZYPP library is locked.

.. _#2: https://github.com/RKrahl/auto-patch/issues/2
.. _#4: https://github.com/RKrahl/auto-patch/pull/4


.. _changes-1_0_1:

1.0.1 (2020-08-19)
~~~~~~~~~~~~~~~~~~

Bug fixes and minor changes
---------------------------

+ `#1`_: fix for non-zero exit status from zypper ps.

+ Add dependency on lsof in the spec file.

+ Add Changelog.

.. _#1: https://github.com/RKrahl/auto-patch/pull/1


.. _changes-1_0:

1.0 (2020-07-26)
~~~~~~~~~~~~~~~~

+ Initial version
