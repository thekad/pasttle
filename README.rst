.. image:: https://img.shields.io/travis/thekad/pasttle/master.svg
   :target: https://travis-ci.org/thekad/pasttle
   :alt: Latest Travis CI Build

.. image:: https://img.shields.io/github/tag/thekad/pasttle.svg
   :target: https://github.com/thekad/pasttle
   :alt: Github Tag

.. image:: https://img.shields.io/pypi/v/pasttle.svg
   :target: https://pypi.python.org/pypi/pasttle
   :alt: PyPi Release

.. image:: https://img.shields.io/pypi/l/pasttle.svg
   :target: https://pypi.python.org/pypi/pasttle
   :alt: License

.. image:: https://img.shields.io/pypi/pyversions/pasttle.svg
   :target: https://pypi.python.org/pypi/pasttle
   :alt: Python Versions

Overview
========

Pasttle is based upon http://sprunge.us, born out of the necessity to:

* Have a lightweight pastebin software
* Not depend on Google AE
* Paste via CLI

Also, I wanted to play more with http://bottlepy.org

Pasttle is split in server and client, it depends on what you are trying to 
use to run one or the other.

* Server: Runs on python and needs a database (defaults to using SQLite) to
  store all the data. You want this if you are setting your own private 
  pasttle instance
* Client: Entirely written in bash. These are just thin wrappers around curl,
  you can use this to post to a pasttle server


Installing/Upgrading pasttle-server
===================================

.. note::

   If you are upgrading pasttle-server, you'd do well in reading CHANGELOG.rst
   first so you make sure the version you are upgrading has any additional
   steps.

Pasttle is part of PyPI, you can just:

.. code:: bash

    pip install pasttle

... and it should pull all the necessary components. Whether you want to install
it in a virtual environment (which I recommend) or system-wide is totally up
to you.

If you instead want to try from source code (i.e. by cloning the git repo) 
then I suggest you execute:

.. code:: bash

    python setup.py install

... and be done with it. Again, if you do this in a virtual environment or
not is up to you.

In either case, if you want to add any other database drivers on top of the
shipped SQLite driver, you need to install it separately depending on what
method you used to install pasttle to begin with.


Running the server
==================

Once you have it installed you need a database and (optionally) a different 
WSGI runner (bottle, which pasttle runs on top of, runs on wsgiref by default) 
but can run on Paste, tornado, CherryPy, and several others.

Also, since pasttle uses SQLAlchemy as the backend, you have your pick of any 
database that SQLAlchemy supports: SQLite (the default), MySQL and Postgres 
being the most famous.

Once you have your database all setup, you just need to create a pasttle.ini 
(like the one in the repo) and change the values to whatever matches your 
environment. 

After that:

.. code:: bash

    pasttle-server.py

Should start the server. If you want to use a different config file, just set 
the environment variable ``PASTTLECONF`` to the file you want to read before 
starting the server, like this:

.. code:: bash

   export PASTTLECONF=/etc/pasttle/mypasttle.ini
   pasttle-server.py
   # optionally, specify a different config section, e.g. [development]
   export PASTTLECONF=/etc/pasttle/mypasttle.ini:development
   pasttle-server.py

Alternatively, an uWSGI configuration is provided in the ``.ini`` file.
Here is a script to run the server with virtualenv option:

.. code:: bash

    #!/usr/bin/sh

    if [ -n "$VIRTUAL_ENV" ]; then
        OPT="-H $VIRTUAL_ENV"
    fi

    exec uwsgi pasttle.ini --plugin python $OPT


Available configuration options
-------------------------------

Defaults are inside `[brackets]`:

.. code:: ini

    [main]
    debug: <true/false> [true]
    bind: <address> [localhost]
    port: 9669
    title: Punchy title
    wsgi: <wsgi server to use>* [auto]
    pool_recycle: <db connection age>* [3600]
    recent_items: <number to show on main page> [20]
    pygments_style: <coloration theme> [tango]


.. note::

    pool_recycle
            See documentation of ``sqlalchemy.create_engine`` for details
    wsgi
            WSGI server to use, look at ``bottle.server_names`` for the list

            .. code:: python

                    import bottle
                    print(bottle.server_names.keys())
                    ['cgi', 'gunicorn', 'cherrypy', 'eventlet', 'tornado', 'geventSocketIO', 'rocket', 'diesel', 'twisted', 'wsgiref', 'fapws3', 'bjoern', 'gevent', 'meinheld', 'auto', 'flup', 'gae', 'paste', 'waitress']



Running the client
==================

Running the client just requires 2 steps:

* Source pasttle.bashrc
* Run ``pasttle -h`` or ``gettle -h`` to check usage
