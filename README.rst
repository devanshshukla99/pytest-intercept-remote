=================
pytest-intercept
=================

This package provides a plugin for ``pytest`` framework to intercept outgoing connection requests and dumps them to a file.

Installation
------------

The ``pytest-intercept`` plugin can be installed using ``pip``

.. code-block:: bash

    $ git clone https://github.com/devanshshukla99/pytest-intercept
    $ cd pytest-intercept
    $ pip install .

The plugin will register with ``pytest`` framework automatically and will be ready to use.

Usage
-----

This plugin allows use of ``--intercept=[Intercept output/dump file]`` as a command-line argument.

.. code-block:: bash

    $ pytest --intercept=urls.json

The tests trying to connect to internet will **fail** with ``Runtime Exception``.


.. Licence
.. -------
.. This plugin is licenced under a 3-clause BSD style licence - see the ``LICENCE.rst`` file.
