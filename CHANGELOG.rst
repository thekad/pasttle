CHANGELOG
=========

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


v0.8
----

* Improved look&feel
* Added ``lexer`` field to the table, varchar of 64


v0.7.5
------

* Split the views into separate (reusable) files
