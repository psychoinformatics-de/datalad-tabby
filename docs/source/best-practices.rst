Best practices
**************

While `tabby` provides a framework to implement near-arbitrary metadata
records, often this flexibility is neither necessary nor actually beneficial.
This section documents "best-practices" for annotating particular dataset
properties. The depicted scenarios are nohow comprehensive, or "best" given any
concrete measure. There are collected here to prevent needless variation, and
facilitate adoption. Contributions to extend or improve this collection are
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
table. Standard JSON-LD rules for context scoping and propgation apply to the
semantics of such a declaration.

A third approach to context specification is a record-global
``<prefix>.ctx.jsonld`` file. If such a file exists, its content will be used
as the default context for any metadata object read from any table of the
`tabby` record, and is inserted as value of its ``@context`` key. Content from
a table-specific ``<prefix>_<table-name>.ctx.jsonld`` side car file will
amend/overwrite individual keys of this default context on a per-table basis.
This approach is particularly useful for declaring a standard set of IRI
prefixes for standard ontologies/vocabularies.


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
