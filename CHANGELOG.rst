CHANGELOG
=========

v0.10.0
------

* NOTICE: Dropping support for python2 as it is no longer maintained by
  the core team (EOL on 1/1/2020)
* Bugfix: Fixed unicode support ingestion
* Enhancement: Docker image is now based on python 3.8 and ships with gunicorn
* Dev change: Using pytest as the testing framework now (with codestyle and flake8 plugins)
* Updating the dependencies to the latest stable versions from upstream
* Slight style tweaks


v0.9.5
------

* NOTICE: Dropping support for python 2.6 as it is no longer maintained by
  the core team
* Updating the dependencies to the latest stable versions from upstream


v0.9.4
------

* Bugfix: get rid of annoying cast-null warnings


v0.9.3
------

* Enhancement: adding a link to the raw version on paste view


v0.9.2
------

* Bugfix: fixing a bug on postgres for parent value
* Bugfix: fixing the copyright year


v0.9.1
------

* Bugfix: the parent value was getting set to some weird integer


v0.9
----

* DB Change: Added ``parent`` field to the ``paste`` table, integer field
* There is now a rudimentary "history" function: if you edit an entry as new,
  it will store the id of the entry it is based on, and a new link will appear
  on the final "show paste" page so you can get a diff view. This diff view is
  currently constrained to those entries without passwords
* Refined the look&feel
* Now the "show paste" page is also styled
* Reorganized the index page so the most used links appear at the top
* Paste pages now return some extra metadata that might be useful in the
  future. Comes in the form of response headers in both normal and raw mode


v0.8
----

* Improved look&feel
* Added ``lexer`` field to the table, varchar of 64


v0.7.5
------

* Split the views into separate (reusable) files
