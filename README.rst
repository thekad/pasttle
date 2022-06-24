.. image:: https://img.shields.io/github/tag/thekad/pasttle?style=for-the-badge
   :target: https://github.com/thekad/pasttle/releases
   :alt: Github

.. image:: https://img.shields.io/pypi/v/pasttle?style=for-the-badge
   :target: https://pypi.python.org/pypi/pasttle
   :alt: PyPi Release

.. image:: https://img.shields.io/circleci/build/github/thekad/pasttle?style=for-the-badge
   :target: https://app.circleci.com/pipelines/github/thekad/pasttle
   :alt: Latest CircleCI Build

.. image:: https://img.shields.io/codecov/c/github/thekad/pasttle?style=for-the-badge
   :target: https://codecov.io/gh/thekad/pasttle
   :alt: Code Coverage

.. image:: https://img.shields.io/pypi/l/pasttle?style=for-the-badge
   :target: https://opensource.org/licenses/MIT
   :alt: License

.. image:: https://img.shields.io/pypi/pyversions/pasttle?style=for-the-badge
   :target: https://pypi.python.org/pypi/pasttle
   :alt: Python Versions

.. image:: https://img.shields.io/gitter/room/thekad/pasttle?style=for-the-badge
   :alt: Join the chat at https://gitter.im/thekad/pasttle
   :target: https://gitter.im/thekad/pasttle?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

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


Running via docker
------------------

There is a docker container published you can use to run pasttle, if you want
to try out you can just:

.. code:: bash

  docker run --rm -p 9669:9669 thekad/pasttle:latest

This pulls and runs the docker image and publishes the ports on your localhost,
you can just open http://localhost:9669 at this point. If you CTRL+C your docker
run it will clean everything up and leave no trace.

If you want to customize the configuration a bit, you can mount your configuration
file `/app/config/pasttle.ini` inside the container:

.. code:: bash

  docker run --rm -p 9669:9669 -v /my/config.ini:/app/config/pasttle.ini thekad/pasttle:latest

If you want to persist your data, there are a few ways to accomplish this. The
first one is to run the pasttle docker image as is and make sure the sqlite
database is written to a volume that can survive docker restarts, by default
the docker container writes its sqlite db to `/app/data` so you can:

.. code:: bash

  docker run --rm -p 9669:9669 -v /some/persistent/location:/app/data:rw thekad/pasttle:latest

Some people may already have a database server around, in that case you will
need to consider a few things: you have to customize your config and also
install the necessary driver. Here's an example running with a postgresql
server using the psycopg2 driver:

.. code:: ini

  [main]
  bind: 0.0.0.0 ; so we can publish the port outside the container
  title: My dockerized pasttle
  dsn: postgresql+psycopg2://user:pass@postgres.host.tld:5432/pasttle
  wsgi: gunicorn ; already shipped in the docker image

Then we have to run our container taking into account the build-time
dependencies:

.. code:: bash

  docker run --rm -p 9669:9669 -v /my/custom.ini:/app/config/pasttle.ini -e BUILD_PACKAGES="build-base postgresql-dev" -e PYTHON_PACKAGES="psycopg2" thekad/pasttle:latest

The above will install the pre-requisites to build psycopg2, then install
psycopg2, and then finally run the pasttle server.

Available configuration options
-------------------------------

.. code:: ini

    [main]
    dsn: <database url> [default=sqlite:///]
    debug: <true/false> [default=true]
    bind: <address> [default=localhost]
    port: <port> [default=9669]
    title: <title>
    wsgi: <wsgi server to use> [default=wsgiref]
    pool_recycle: <db connection age> [default=3600]
    recent_items: <number to show on main page> [default=20]
    pygments_style: <coloration theme> [default=tango]


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
