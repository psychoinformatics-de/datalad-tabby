Scientific dataset (v1, ``tby-sd1``)
====================================

This convention defines a fairly minimalistic description of a scientific dataset.
With few exceptions the convention is built on the https://schema.org vocabulary.


Sheet ``authors``
-----------------

Context
~~~~~~~

.. literalinclude:: ../../../datalad_tabby/io/conventions/tby-sd1/authors.ctx.jsonld
   :language: json

Overrides
~~~~~~~~~

Any entity in the sheet is declared to be of type https://schema.org/Person, using
a given ORCID as a globally unique IRI.

.. literalinclude:: ../../../datalad_tabby/io/conventions/tby-sd1/authors.override.json
   :language: json


Sheet ``dataset``
-----------------

Context
~~~~~~~

.. literalinclude:: ../../../datalad_tabby/io/conventions/tby-sd1/dataset.ctx.jsonld
   :language: json

Default (JSON) data
~~~~~~~~~~~~~~~~~~~

A dataset must declare authors in a dedicated ``authors`` sheet. A dataset may
declare associated funding in a dedicated ``funding`` sheet. Both sheets use the
``tby-sd1`` convention.

.. literalinclude:: ../../../datalad_tabby/io/conventions/tby-sd1/dataset.json
   :language: json


Sheet ``funding``
-----------------

Context
~~~~~~~

.. literalinclude:: ../../../datalad_tabby/io/conventions/tby-sd1/funding.ctx.jsonld
   :language: json

Overrides
~~~~~~~~~

Any entity in the sheet is declared to be of type https://schema.org/Grant.

.. literalinclude:: ../../../datalad_tabby/io/conventions/tby-sd1/funding.override.json
   :language: json
