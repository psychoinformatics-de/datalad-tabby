The `tabby` format
******************

`tabby` is a metadata format that can be used to describe arbitrary things. It
does not prescribe a specific terminology.

A `tabby` metadata record comprises linked components stored in individual
files that are assembled and interpreted to form a single JSON_ or JSON-LD_
document.  The different types of components are:

sheet
  The main building block of a `tabby` record. A sheet contains key-value pairs
  in a table(-like) format. See `Sheet types`_ for details.

context
  A record-global, or sheet-specific JSON-LD_ context that defines the
  terminology and semantics of information in sheets. This is an optional
  component. See `Defining context`_ for details.

override
  A JSON_-format specification of data transformations to be applied to the
  information in sheets, when assembling them into a complete JSON(-LD)
  document This is an optional component. See `Metadata enrichment
  (overrides)`_ for details.




File naming
===========

A `tabby` metadata record comprises one or more files that share a common,
arbitrary name prefix. In addition to this prefix, each file path contains the
name of a `sheet`. More generally, the name of all files comprising a `tabby`
metadata record follow the scheme::

    <record-id>{_,/}<sheet-name>.<extension>

where

- ``<record-id>`` is a character string that is common to all files comprising
  a single `tabby` metadata record. This ID is an arbitrary, case-sensitive
  string.

  For cross-platform compatibility reasons it is *recommended* to limit the
  identifier to lower-case ASCII values, and possibly alphanumeric characters.

  The ``<record-id>`` is specified as a ``_``-delimited file name prefix.
  Alternatively, the ``<record-id>`` can be identified via the name of the
  parent directory. In this case, no `tabby` record file component in this
  directory can include a ``_`` character in its file name, and only a single
  `tabby` record can be represented in that directory.

- ``<sheet-name>`` is a unique name for a particular sheet component of a
  ``tabby`` metadata record. The name must be lower-case and only consist of
  the character set ``[@a-z0-9-]`` (``@``, letter, digits, and dash/hyphen).

- ``<extension>`` uniquely identifies the nature of the record component:

  - ``tsv`` or ``json`` for a `sheet`
  - ``ctx.jsonld`` for a `context`
  - ``override.json`` for an `override` specification


Sheet types
===========

Tabular metadata is represented in plain-text files, typically in
tab-separated-value (TSV_) format (but see the layout specifications for a
JSON alternative).  `tabby` defines how this tabular information is
converted to structured data that can be represented in formats like JSON.

Two different sheet layouts are distinguished and are described below. The
particular layout cannot necessarily be inferred from the file content.
Instead, the specific semantic is declared when `Connecting sheets`_.

No data type conversion of any kind is performed when reading data from sheets
in TSV-format. Any item is represented as a plain-text string.


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

When a JSON-file is present (either in addition to a TSV-table or standalone),
it must contain a JSON-object. Keys and values in this object are updated with
the information read from a corresponding TSV-file, if one exists. Data read from
JSON or TSV files are interpreted in the exact same fashion. The only difference
is that JSON-native data types are preserved.


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

When a JSON-file is present (either in addition to a TSV-table or standalone),
it must contain ether a JSON-object or a JSON-array. If it contains a
JSON-object, this object is used as the template for any object read from a
corresponding TSV-file's rows (in the same fashion as TSV-based information
updates a JSON-object in the ``single`` layout). If it contains an array, all
elements in the array are interpreted as items in the ``many`` table, which
precede any items read from rows in a corresponding TSV-file, if one exists.
Otherwise, data read from JSON or TSV files are interpreted in the exact same
fashion. The only difference is that JSON-native data types are preserved.


Metadata record entry point (root)
==================================

Each `tabby` metadata record comprises, at minimum, one `sheet`
in ``single`` layout. A system using `tabby` records should establish a
convention to identify this root record via a particular name, such as
``dataset``.

A minimal metadata record on a dataset about "penguins" can be represented in a
single file, such as ``penguins_dataset.tsv``, or ``penguins_dataset.json``.


Connecting sheets
=================

Information from individual `sheets` can be nested to create more complex data
structures than what the two basic sheet layouts can represent individually.
This is supported by two dedicated import statements:

- ``@tabby-single-<sheetname>``
- ``@tabby-many-<sheetname>``

where ``<sheetname>`` is the name of a `tabby` metadata record component, with
which the corresponding file name can be constructed. For example, using
``@tabby-many-authors`` in the TSV file ``penguins_dataset.tsv``, links the
information in the file ``penguins_authors.tsv`` located in the same directory.

The difference between the ``@tabby-single-...`` and the ``@tabby-many-...``
statements is how the linked sheets are being interpreted, and correspond to
the two basic sheet layouts.

These import statements can be used in any value field in any of the two sheet
layouts. This includes value list (array) items.

Imports are not file-format specific, hence the sheet name must not include a
file extension. An imported sheet can always be in TSV-format, JSON-format, or
a combination of both formats.


Defining context
================

Typically, the `sheets` of a `tabby` metadata record use simple terms like
``license`` for keys and equally simple values like ``1.5`` for values.  While
this simplicity is useful for assembling a metadata record (possibly manually),
it is insufficient for yielding precise, machine-readable records with
comprehensively defined semantics. For that, each and every term, like
``license``, must have a proper definition, and quantitative values, like
``1.5``, must come with information on the underlying concepts and possibly
associated units.

Providing the necessary context is possible by amending a metadata record with
JSON-LD ``@context`` records that can be supplied, for each `sheet` separately,
via side-car files. Such a side-car files share the file name of the annotated
`sheet` without the extension, and a ``.ctx.jsonld`` suffix.  For example, a
context for ``penguins_authors.tsv`` would be read from
``penguins_authors.ctx.jsonld`` in the same directory.

In addition, a `tabby` record may include a record-global context specification
at ``<prefix>.ctx.jsonld`` or ``<prefix>/ctx.jsonld``. This defines a default
context for any `sheet`. Sheet-specific context definitions amend/override this
record-global default for a given `sheet`.

The content of any context file must be a valid `JSON-LD context`_.

.. _sec-override-specification:

Metadata enrichment (overrides)
===============================

When the tabular components of a `tabby` metadata record are not detailed
enough or precise enough, it is possible to enrich the record with additional
information, without having to edit the `sheets`. This is done via an
overrides specification in a JSON side-car file.

The type of metadata enrichment described here is based on purely lexical
operations that manipulate (string) values. For other types of metadata
enrichment see `Defining context`_ or consider `JSON-LD framing`_.

The override side-car file has the file name of the annotated `sheet` without
the extension, plus a ``.override.json`` suffix.  For example, overrides for
``penguins_authors.tsv`` would be read from ``penguins_authors.override.json``
in the same directory.

An override specification comprises of a single JSON object (key-value
mapping), where a key indicates the target for injection or replacement, and
the value is either a JSON literal, a format-string, or a JSON array (list) of
these two types.

Any string value is assumed to be a format-string, compliant with the `Python
Format String Syntax`_, and will be interpolated using the key-value mapping
for the respective object read from `sheet`.  Therefore the brace characters
``{}`` need to be quote in case a particular string is to be treated as a
literal value.

.. _Python Format String Syntax: https://docs.python.org/3/library/string.html#format-string-syntax

The full override record is built before it is applied, at once, to the
respective object read from a `sheet`.

When declaring an override for a ``many`` sheet, the override is applied
individually to each object (row) defined in that sheet.

For uniformity, any metadata value is represented as a multi-value list
(array) at the point of interpolation override specifications. A single item
value for the key ``name`` therefore has to be referenced as ``{name[0]}``, not
just ``{name}``. See :ref:`sec-override-examples` for examples.


.. _JSON: https://www.json.org
.. _JSON-LD: https://www.w3.org/TR/json-ld11
.. _JSON-LD framing: https://www.w3.org/TR/json-ld11-framing
.. _JSON-LD context: https://www.w3.org/TR/json-ld11/#the-context
.. _TSV: https://en.wikipedia.org/wiki/Tab-separated_values
