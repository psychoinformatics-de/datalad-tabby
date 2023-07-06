DataLad Tabby
*************

This `DataLad <http://datalad.org>`__ extension package provides tooling for
working with a particular metadata format: `tabby`.

Another format?!

Yes... No! `tabby` is JSON(-LD) in disguise.

In a nutshell, `tabby` aims to be an approach to assemble complex metadata
structures from simple building blocks: *tables*.  Tables are easy to
understand with a clear structure, just rows and columns.  `tabby` specifies a
few syntax elements to connect tables to form more complex structures. At the
same time, `tabby` is implemented with the mindset that metadata without
defined vocabularies has limited utility.  Therefore, `tabby` aims to translate
into JSON-LD to provide semantic precision without imposing its complexity on
every aspect of metadata handling.  This makes it possible to let curators
enrich metadata without alienating these metadata from their original providers
or sources.


.. toctree::
   :maxdepth: 2

   specification.rst


Extension API
=============

Python tooling
--------------

.. currentmodule:: datalad_tabby
.. autosummary::
   :toctree: generated

   io


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. |---| unicode:: U+02014 .. em dash


.. toctree::
   :hidden:

   tabby-spec
