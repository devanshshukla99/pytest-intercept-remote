=======================
pytest-intercept-remote
=======================

|Build|


This package provides a plugin for ``pytest`` framework to intercept outgoing connection requests and dumps them to a file.

Installation
------------

The ``pytest-intercept-remote`` plugin can be installed using ``pip``

.. code-block:: bash

    $ git clone https://github.com/devanshshukla99/pytest-intercept-remote
    $ cd pytest-intercept-remote
    $ pip install .

The plugin will register automatically with ``pytest`` framework and will be ready to use.

Config
------

The default dump file can be configured by specifing ``intercept_dump_file`` in the ini file .
The plugin also allows ``--intercept-dump-file=[dump filepath]`` for overriding the dump filepath.

.. code-block:: bash

    $ pytest --intercept-remote --intercept-dump-file=urls.json

Usage
-----

This plugin can be used by ``--intercept-remote`` arg.

.. code-block:: bash

    $ pytest --intercept-remote

The tests trying to connect to internet will **xfail**.


Licence
-------
This plugin is licenced under a 3-clause BSD style licence - see the ``LICENCE`` file.


.. |Build| image:: https://github.com/devanshshukla99/pytest-intercept-remote/actions/workflows/python-app.yml/badge.svg
