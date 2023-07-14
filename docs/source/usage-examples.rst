Usage examples
**************

Metadata enrichment (overrides)
===============================

The table below shows three data types which can be used in an
override side-car file, ``*.override.json``. Examples in the table
assume that a horizontal input table contained ``doi
https://doi.org/10.nnnnnn/example``, and the value stored under the
``doi`` key should be replaced. The same method can be used to add a
new key (instead of changing the value of an existing one).

+------------------------+------------------------------------------------+-------------------------------------------------------------------------+
| type                   | json override                                  | produces                                                                |
+========================+================================================+=========================================================================+
| json literal           | ``{"doi": {"was here": true}}``                | ``{'doi': {'was here': True}}``                                         |
+------------------------+------------------------+-----------------------+-------------------------------------------------------------------------+
| string template        | ``{"doi": "I am become {doi[0]}"}``            | ``{'doi': 'I am become https://doi.org/10.nnnnnn/example'}``            |
+------------------------+------------------------------------------------+-------------------------------------------------------------------------+
| list                   | ``{"doi": ["Identifier", "doi", "{doi[0]}"]}`` | ``{'doi': ['Identifier', 'doi', 'https://doi.org/10.nnnnnn/example']}`` |
+------------------------+------------------------------------------------+-------------------------------------------------------------------------+

Overrides can be used for vertical tables, changing or extending each
object (row). Consider the following table, in which mouse strains
were identified by their JAX codes for brevity:

.. code-block:: none

   id    strain_jax    ...
   01    018280
   ...

Since RRIDs and URLs can be easily generated from these values, we can
supply the additional values with the following override:

.. code-block:: json

   {
     "RRID": "RRID:IMSR_JAX:{strain_jax[0]}",
     "url": "https://www.jax.org/strain/{strain_jax[0]}",
     "schema": "https://custom_schema.org/customExperiment"
   }

producing:

.. code-block:: python

  [
    {"id": "01", "strain_jax": "018280", "RRID": "RRID:IMSR_JAX:018280", "url": "https://www.jax.org/strain/018280", "schema": "https://custom_schema.org/customExperiment"},
    ...
  ]
