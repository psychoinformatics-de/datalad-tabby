The `tabby` format
******************

The scope of `tabby` metadata is the description of a single version of a
dataset: a collection of files, curated for a particular purpose.

A `tabby` metadata record comprises one or more files that share a common,
arbitrary file name prefix. Each file name contains the name of a (tabular)
metadata component. Each record, at minimum, contains a ``dataset``
components. A minimal metadata record on a dataset about "penguins" could
be represented in a single file: ``penguins_dataset.tsv``.


Two table types
===============

Tabular metadata is represented in plain-text, tab-separated-value (TSV) files.
`tabby` defines how this tabular information is converted to structured data
that can be represented in formats like JSON.

Two different table layouts are distinguished and are described below. The
particular layout cannot necessarily be inferred from the file content.
Instead, the specific semantic is declared when `Connecting tables`_.

No data type conversion of any kind is performed when reading data from
tables. Any item is represented as a plain-text string.


The ``single`` layout
---------------------

This layout represents a key-value mapping, equivalent to a JSON object.

Each table row corresponds to a particular key, which is given as the value of
the first column. Empty rows, or rows where the value in the first column is
missing or starts with ``#`` are skipped. When a particular key is repeated in a
subsequent row, the information in the latter row *replaces* the information in
the former.

The value corresponding to a key is given in the second column. If there are
values in subsequent columns, all values starting from column 2 until the last
column with a value are gathered into a list (JSON-array equivalent). Any missing
values in this list are represented as ``None`` (JSON's ``null``). If no value
is declared for a table row, the entire row (i.e., the key) is skipped)

Single-item list values are compacted by removing the containing list and
assigning the only items directly as the value.


The ``many`` layout
---------------------

This layout represents a series of homogeneous key-value mappings, equivalent
to JSON-array comprising homogeneously structured JSON-objects.

Any table row that is empty, or where the value in the first column starts with
``#`` is skipped.

The first non-skipped row defines a common set of keys. Every subsequent row
represents an entity that is described with values corresponding to these
common keys.

When two columns are associated with the exact same key, their associated
values are gathered into a list (JSON-array equivalent), with missing values
being skipped.

When a row contains columns with values beyond the column corresponding to the
last defined key, all these values are gathered into a list (JSON-array
equivalent) that include the values from the column of the last defined key,
and is assigned as the value corresponding to that last key.

Single-item list values are compacted by removing the containing list and
assigning the only items directly as the value.


Connecting tables
=================

Information from metadata tables can be nested to create more complex data
structures than what the two basic table layouts can represent individually.
This is supported by two dedicated import statements:

- ``@tabby-single-<tablename>``
- ``@tabby-many-<tablename>``

where ``<tablename>`` is the name of a `tabby` metadata record component, with
which the corresponding file name can be constructed. For example, using
``@tabby-many-authors`` in the TSV file ``penguins_dataset.tsv``, links the
information in the file ``penguins_authors.tsv`` located in the same directory.

The difference between the ``@tabby-single-...`` and the ``@tabby-many-...``
statements is how the linked tables are being interpreted, and correspond to
the two basic table layouts.

These import statements can be used in any value field in any of the two table
layouts. This includes value list (array) items.


Defining context
================

.. todo::
   This functionality is not fully implemented yet

Typically, the tabular components of a `tabby` metadata record use simple terms
like ``license`` for keys and equally simple values like ``1.5`` for values.
While this simplicity is useful for assembling a metadata record (possibly
manually), it is insufficient for yielding precise, machine-readable records
with comprehensively defined semantics. For that each and every term, like
``license``, must have a proper definition, and quantitative values, like
``1.5``, must come with information on the underlying concepts and possibly
associated units.

Providing the necessary context is possible by amending a metadata record with
JSON-LD ``@context`` records that can be supplied, for each tabular component
separately, via side-car files. Such a side-car files share the file name of
the annotated TSV file without the extension, and a ``.ctx.jsonld`` suffix.
For example, a context for ``penguins_authors.tsv`` would be read from
``penguins_authors.ctx.jsonld`` in the same directory.

The content of such a file must be a valid JSON-LD context.


Metadata enrichment (overrides)
===============================

When the tabular components of a `tabby` metadata record are not detailed
enough or precise enough, it is possible to enrich the record with additional
information, without having to edit the TSV files. This is done via an
overrides specification in a JSON side-car file.

The type of metadata enrichment described here is based on purely lexical
operations that manipulate (string) values. For other types of metadata
enrichment see `Defining context`_ or consider JSON-LD framing.

The override side-car file has the file name of the annotated TSV file without
the extension, plus a ``.override.json`` suffix.  For example, overrides for
``penguins_authors.tsv`` would be read from ``penguins_authors.override.json``
in the same directory.

An override specification comprises of a single JSON object (key-value
mapping), where a key indicates the target for injection or replacement, and
the value is either a JSON literal, a format-string, or a JSON array (list) of
these two types.

Any string value is assumed to be a format-string, compliant with the `Python
Format String Syntax`_, and will be interpolated using the key-value mapping
for the respective object read from the TSV file.  Therefore the brace
characters ``{}`` need to be quote in case a particular string is to be
treated as a literal value.

.. _Python Format String Syntax: https://docs.python.org/3/library/string.html#format-string-syntax

The full override record is built before it is applied, at once, to the
respective object read from a TSV file.

When declaring an override for a ``many`` table, the override is applied
individually to each object (row) defined in that table.

For uniformity, any metadata value is represented as a multi-value list
(array) at the point of interpolation override specifications. A single item
value for the key ``name`` therefore has to be referenced as ``{name[0]}``, not
just ``{name}``.
