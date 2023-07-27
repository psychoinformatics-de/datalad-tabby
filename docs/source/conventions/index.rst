.. _chap_conventions:

Conventions for sheet formats and semantics
===========================================

`tabby` records can conform to a particular (set of) conventions that
cover individual composition of a record, the semantic definition
of its components, and/or the employed vocabularies.

Employed conventions are declared on a per-sheet basis, by including their
label directly in the sheet name (see :ref:`sec_convention_declaration`).

Technically, a convention can be thought of as a (default) provider for any
sheet component (context, overrides, JSON data, or even a sheet itself). This
means that if a record does not contain any such sheet component the convention
specification is checked for a matching component, which is then used, if it
exists.

Conventions enable rather minimal tabby records. They can adopt semantics and
override logic from a convention, and thereby avoid duplication across
individual records. Only on load a complete record is built and reported.
Individual sheets in a record need not use a single convention, but may
mix-and-match from any available convention.


.. toctree::
   :caption: Built-in conventions
   :maxdepth: 1

   tby-ds1.rst
   tby-sd1.rst


Adding new/Updating built-in conventions
----------------------------------------

Labels of all built-in conventions:

- start with the ``tby-`` prefix.  This is an arbitrary prefix that aims to
  minimize name conflicts with user-provided conventions.
- include a short name for the convention.
- include a version number. This version number is incremented whenever
  backward-incompatible changes to a convention specification are made.


Convention specifications are put into a
``datalad_tabby/io/conventions/<label>/`` directory in the package source tree.
Because the version is included in the directory name, it is ensures that there
are no naming conflicts when versions are incremented, and previous
specifications can remain available indefinitely.
