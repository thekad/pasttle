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
* Client: These are just thin wrappers around curl, you can use this to post 
  to a pasttle server


Installing pasttle-server
=========================

Pasttle is part of PyPI, you can just:

.. code:: bash

    pip install pasttle

and it should pull all the necessary components. Whether you want to install
it in a virtual environment (which I recommend) or system-wide is totally up
to you.

If you instead want to try from source code (i.e. by cloning the git repo) 
then I suggest you execute:

.. code:: bash

    python setup.py install

... and be done with it. Again, if you do this in a virtual environment or
not is up to you.


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
starting the server.


Running the client
==================

Running the client just requires 2 steps:

* Source pasttle.bashrc
* Run ``pasttle -h`` or ``gettle -h`` to check usage
