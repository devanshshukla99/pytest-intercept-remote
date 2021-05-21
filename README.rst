=======================
pytest-intercept-remote
=======================

|Build| |Coverage|


This package provides a plugin for ``pytest`` framework to intercept outgoing connection requests and dumps them to a file.

Installation
------------

The ``pytest-intercept-remote`` plugin can be installed by using:

.. code-block:: bash

    $ git clone https://github.com/devanshshukla99/pytest-intercept-remote
    $ cd pytest-intercept-remote
    $ pip install .

The plugin will register automatically with ``pytest`` framework and will be ready to use.

Config
------

The default dump file can be configured by specifing ``intercept_dump_file`` in the ini file or by overriding it by ``-o intercept_dump_file``.

.. code-block:: bash

    $ pytest --intercept-remote -o intercept_dump_file=urls.json

Usage
-----

This plugin can be used by adding ``--remote-data=any --intercept-remote`` options;

NOTE: The plugin only works over functions marked with `remote_data` marker, see `remotedata <https://github.com/astropy/pytest-remotedata>`_ for more info.

.. code-block:: bash

    $ pytest --remote-data=any --intercept-remote


The tests trying to connect to internet will ``xfail``.


Testing
-------

Use ``tox`` to make sure the plugin is working:

.. code-block:: bash

    $ git clone https://github.com/devanshshukla99/pytest-intercept-remote
    $ cd pytest-intercept-remote
    $ tox -e py38

See `tox <https://github.com/tox-dev/tox>`_ for more info.


Licence
-------
This plugin is licenced under a 3-clause BSD style licence - see the ``LICENCE`` file.

.. |Build| image:: https://github.com/devanshshukla99/pytest-intercept-remote/actions/workflows/main.yml/badge.svg

.. |Coverage| image:: https://codecov.io/gh/devanshshukla99/pytest-intercept-remote/branch/main/graph/badge.svg?token=81U29FC82V
    :target: https://codecov.io/gh/devanshshukla99/pytest-intercept-remote
