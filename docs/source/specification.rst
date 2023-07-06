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

Any table row that is empty, or where the value in the first column starts with ``#`` is skipped.

The first non-skipped row defines a common set of keys. Every subsequent row
represents an entity that is described with values corresponding to these
common keys.

When two columns are associated with the exact same key, there associated
values are gathered into a list (JSON-array equivalent), with missing
values being skipped.

When a row contains columns with values beyond the column corresponding to
the last defined key, all these values are gathered into a list (JSON-array equivalent) that include the values from the column of the last defined key,
and is assigned as th value corresponding to that last key.

Single-item list values are compacted by removing the containing list and
assigning the only items directly as the value.


Connecting tables
=================

TODO


Defining context
================

TODO


Amending metadata (enrichment)
==============================

TODO
