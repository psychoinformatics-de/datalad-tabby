Collection-of-files dataset (v1, ``tby-ds1``)
=============================================

This convention defines the essential building blocks to describe a collection
of files as a dataset. With few exceptions the convention is built on the
https://schema.org vocabulary.

Here is an example of a fairly minimal, yet sensible, description of a dataset.
The dataset has a few key properties (e.g., a licence), an author, and comprises
two files. This information is expressed in three TSV files:

- ``dataset@tby-ds1.tsv``

  .. csv-table::
     :align: left
     :file: tby-ds1_demo/dataset@tby-ds1.tsv
     :delim: tab
     :widths: auto
     :stub-columns: 1

- ``authors@tby-ds1.tsv``

  .. csv-table::
     :align: left
     :file: tby-ds1_demo/authors@tby-ds1.tsv
     :delim: tab
     :widths: auto
     :header-rows: 1

- ``files@tby-ds1.tsv``

  .. csv-table::
     :align: left
     :file: tby-ds1_demo/files@tby-ds1.tsv
     :delim: tab
     :widths: auto
     :header-rows: 1


Using the following, minimal JSON-LD context for compaction...

.. literalinclude:: tby-ds1_demo/ds1-compact.jsonld
   :language: json

... the information in the TSV tables is transformed into a single, fully
annotated JSON-LD document on the dataset.

.. literalinclude:: tby-ds1_demo/compacted.jsonld
   :language: json

.. The compacted output was built with:
   $ datalad tabby-load \
       docs/source/conventions/tby-ds1_demo/dataset@tby-ds1.tsv \
       --compact docs/source/conventions/tby-ds1_demo/ds1-compact.jsonld \
   | jq > docs/source/conventions/tby-ds1_demo/compacted.jsonld


Sheet types
^^^^^^^^^^^

Sheet ``authors``
-----------------

Context
~~~~~~~

.. literalinclude:: ../../../datalad_tabby/io/conventions/tby-ds1/authors.ctx.jsonld
   :language: json

Overrides
~~~~~~~~~

Any entity is declared to be of type https://schema.org/Person.

.. literalinclude:: ../../../datalad_tabby/io/conventions/tby-ds1/authors.override.json
   :language: json


Sheet ``dataset``
-----------------

Context
~~~~~~~

Licenses are declared using the identifiers given at https://spdx.org/licenses
as a standard vocabulary.

.. literalinclude:: ../../../datalad_tabby/io/conventions/tby-ds1/dataset.ctx.jsonld
   :language: json

Default (JSON) data
~~~~~~~~~~~~~~~~~~~

Information on authors and files is included, if they exist.

.. literalinclude:: ../../../datalad_tabby/io/conventions/tby-ds1/dataset.json
   :language: json


Sheet ``files``
---------------

Context
~~~~~~~

File paths are annotated to be names of any described entity, including
a definition of the path convention used (e.g., POSIX).

.. literalinclude:: ../../../datalad_tabby/io/conventions/tby-ds1/files.ctx.jsonld
   :language: json

Overrides
~~~~~~~~~

Any entity is declared to be of type https://schema.org/DigitalDocument.
A given `md5sum` is used as a node identifier.

.. literalinclude:: ../../../datalad_tabby/io/conventions/tby-ds1/files.override.json
   :language: json
