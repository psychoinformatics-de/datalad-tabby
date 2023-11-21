Best practices
**************

While `tabby` provides a framework to implement near-arbitrary metadata
records, often this flexibility is neither necessary nor actually beneficial.
This section documents "best-practices" for annotating particular dataset
properties. The depicted scenarios are nohow comprehensive, or "best" given any
concrete measure. They are collected here to prevent needless variation, and
to facilitate adoption. Contributions to extend or improve this collection are
most welcome.


Context declaration: precision vs. boilerplate
==============================================

The `tabby` format supports a dedicated context specification for each table.
However, a full context declaration per each table would lead to needlessly
verbose records.

Recommendation
--------------

When a single context is sufficient for a `tabby` record, it can be declared
as the context of the root table in ``<prefix>_dataset.ctx.jsonld``. The context
in this file is inserted into the `tabby` record at the root level, hence
covers the entire document, including content inserted from other tables.

When individual tables require a different context specification, it can be
declared in the respective ``<prefix>_<table-name>.ctx.jsonld`` side-car files.
Such a context is inserted in each metadata object read from the respective
table. Standard JSON-LD rules for context scoping and propagation apply to the
semantics of such a declaration.

A third approach to context specification is a record-global
``<prefix>.ctx.jsonld`` file. If such a file exists, its content will be used
as the default context for any metadata object read from any table of the
`tabby` record, and is inserted as the value of its ``@context`` key. Content
from a table-specific ``<prefix>_<table-name>.ctx.jsonld`` side car file will
amend/overwrite individual keys of this default context on a per-table basis.
This approach is particularly useful for declaring a standard set of IRI
prefixes for standard ontologies/vocabularies.


Declare the type of a metadata entity
=====================================

A `tabby` record comprises any number of nested/linked metadata objects (in the
form of JSON-objects). For semantically precise metadata, each of these objects
should declare a ``@type`` property to identify its nature (or `class` in RDF
terms). However, from a `tabby` user perspective this can often seem redundant
and tedious to specify manually. For example, for a human it may seem superfluous
to label each item in a ``funding`` table with a type that is always ``Grant``.

Recommendation
--------------

Conceptualize `tabby` tables to describe metadata entities of the same type,
and insert the ``@type`` definition as an override. For example, if a
``<prefix>_authors.tsv`` table only lists people (as opposed to also
organizations), the following override in ``<prefix>_authors.override.json``
would be suitable for an automatic type-declaration:

.. code-block:: json

   {
     "@type": "schema:Person"
   }

If type-homogeneity within a table cannot be achieved, use a dedicated ``type``
property and document a controlled vocabulary for users. An override can amend
a user-provided type-label to turn it into a defined term. For example, a list
of publications may comprise different types of published items. Using the
schema.org terms (like ``ScholarlyArticle``) is an option for identifying the
types. The following override in ``<prefix>_publications.override.json``
defines this approach. The user-provided label is explicitly prefixed to
yield a defined term:

.. code-block:: json

   {
     "type": "schema:{type[0]}"
   }

This ``type`` property can also be declared to serve as the JSON-LD node type
specification, by declaring the following in
``<prefix>_publications.ctx.jsonld``:

.. code-block:: json

   {
     "type": "@type",
   }

Leading to a corresponding entity to be reported as:

.. code-block:: json

   "publication": {
     "@type": "schema:ScholarlyArticle"
     //...
   }


Declare an ordered list of entities (e.g., author list)
=======================================================

``many``-format tables represent a JSON-array of objects with an intrinsic
order. However, in the context of JSON-LD `multiple array values SHOULD be
presumed to be unordered
<https://w3c.github.io/json-ld-bp/#unordered-values>`__. If the order of items
in a ``many`` table is significant, this requires a dedicated annotation.

Recommendation
--------------

Declare the property that links the ordered list of entities to be
a ``"@container": "@list"`` in the respective context. For an ordered
author list, for example, declare:

.. code-block:: json

   "author": {
      "@id": "...",
      "@container":"@list"
   }

in the context of the ``dataset`` table.


Declare an entity to be the *controller* of a dataset (GDPR)
============================================================

The concept of a `data controller` is a key element of the EU's General Data
Protection Regulation (see
https://www.gdpreu.org/the-regulation/key-concepts/data-controllers-and-processors).
More generally, a data controller can be seen an the entity that is (legally)
responsible for a dataset, and may serve as the main contact point regarding
any inquires concerning a dataset.

The `Data Privacy Vocabulary <https://w3c.github.io/dpv/dpv/>`__ provide a suitable
vocabulary to express this.

Recommendation
--------------

Define a ``dpv`` IRI-prefix in the JSON-LD context

.. code-block:: json

   {
     "dpv": "https://w3id.org/dpv#"
   }

Add a ``data-controller`` table to the metadata record. This may be in ``single``,
or ``many`` format, depending on the dataset. It should contain essential
properties of the data controller entity, such as a name, an email, and possibly
a (physical/postal) address.

Declare the data controller entity type via an override declaration
(``<prefix>_data-controller.override.json``):

.. code-block:: json

   {
     "@type": "dpv:DataController"
   }

Link the ``data-controller`` table as a property in the ``dataset`` table
(using the import statement that matches the chosen table format):

.. list-table::

   * - data-controller
     - @tabby-many-data-controller
