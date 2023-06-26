Tabular dataset description
###########################

The ``tabby`` specification is a format to describe a dataset using
nothing but tabular files (we'll refer to them as "tabby files") in
a way that allows a useful and meaningful catalog representation.

The tabby specification is loosely based on `ISA-tab`_, and makes
use of the `TSV format`_.

.. _ISA-tab: https://isa-specs.readthedocs.io/en/latest/isatab.html
.. _TSV format: https://en.wikipedia.org/wiki/Tab-separated_values

The core benefit of the tabby specification is that a complete set
of descriptive metadata of a dataset and its files can be provided
by hand-editing tables using common spreadsheet software. The
resulting tabby files are interoperable with software tools and
automated workflows for research data management and data
discoverability.

Below we provide a list of core tabby principles, followed by a
description of the two main tabular files that together form the
tabby specification:

- **the dataset tabby file**, which allows describing all properties
  of a single dataset,
- **the files tabby file**, which allows describing any (or all)
  files forming part of a single dataset.


Tabby principles
****************

1. A dataset is a collection of files
2. Dataset-level metadata describe the dataset as a whole
3. File-level metadata describe individual files belonging to a
   dataset
4. Properties are used to provide meaningful descriptions of
   arbitrary aspects of a dataset or a file
5. A property could be required or optional for the fulfillment
   of the tabby specification (on the dataset- or file-level)
6. The tabby specification has lists of recognized properties,
   for a dataset and files respectively
7. The tabby specification recognizes single-value properties 
   (e.g. ``'Identifier': '1234'``) and multi-value properties
   (e.g. ``Person: {'Name': 'John', 'LastName': 'Doe'}``) 
8. Apart from recognized properties, the specification also
   allows flexibility to users to define their own so-called
   "custom properties" for datasets and files.


Dataset tabby file
******************

In the TSV file for a dataset, each row describes a dataset property.
The first column of each row contains the property name, and is
followed by one or more columns containing corresponding values.
For multi-value properties, the content in each column is interpreted
based on the column number and the specification of the recognized
property itself.

Below follows one section for each recognized property. Each section
contains a table snippet with details on the syntax and semantics for
that property. ``colX`` labels identify the respective column
numbers. Optional cells are indicated by `*`.

Dataset identifier [required]
=============================

- Property: ``identifier``
- Definition: https://schema.org/identifier

==========  ==========
col1        col2
==========  ==========
identifier  <text>
==========  ==========

Dataset name [required]
=======================

- Property: ``name``
- Definition: https://schema.org/name

==========  ==========
col1        col2
==========  ==========
name        <text>
==========  ==========

Dataset description [optional]
==============================

- Property: ``description``
- Definition: https://schema.org/description

============  ==========
col1          col2
============  ==========
description   <text>
============  ==========

Dataset version [optional]
==========================

- Property: ``version``
- Definition: https://schema.org/version

==========  ==========
col1        col2
==========  ==========
version     <text>
==========  ==========

Author [optional]
=================

- Property: ``author``
- Definition: https://schema.org/author

One or more rows are supported, one row for each author. Order in the
table (top-to-bottom) defines author order (first is first, last is
last).

==========  ============== ========= ========= ================
col1        col2           col3*     col4*     col5*
==========  ============== ========= ========= ================
author      <full name>    <orcid>   <email>   <affiliation(s)>
==========  ============== ========= ========= ================

Publication [optional]
======================

- Property: ``publication``
- Definition: https://schema.org/publication

One or more rows are supported, each row for one publication related
to the dataset, or possibly a publication of the dataset itself. The
DOI should be included in url-form, preferably as
``https://doi.org/10.nnnnnn/example``. The citation is
free-format. Citation style should be consistent across publications.

===========  ======= ==========
col1         col2    col3
===========  ======= ==========
publication  <doi>   <citation>
===========  ======= ==========

Dataset keywords [optional]
===========================

- Property: ``keywords``
- Definition: https://schema.org/keywords

One keyword per cell, no limit on number of keywords.

==========  ========== ========== ==========
col1        col2       col3*      ...*
==========  ========== ========== ==========
keywords    <text>     <text>     <text>
==========  ========== ========== ==========

Custom dataset property [optional]
==================================

Definition: https://schema.org/Property

Any row with a col1 cell value that does not match a recognized field
described above is interpreted as a custom property.

The first two columns define category label and property name (category
labels will can be used to display a custom group in a catalog). A
special category label (column 1) ``property`` can be used to indicate
"no particular category" (these properties will be displayed as general
dataset properties in a catalog). The next column(s) are used to store
property value(s).

==========  ========== ========== ==========
col1        col2       col3*      ...*
==========  ========== ========== ==========
label       <name>     <value>    <text>
==========  ========== ========== ==========

SFB1451-specific properties
---------------------------

Origin SFB project
^^^^^^^^^^^^^^^^^^

==========  ========== ==========
col1        col2       col3
==========  ========== ==========
SFB1451     Project    <text>
==========  ========== ==========

Custom file property [optional]
===============================

- Property: ``filecolumn``
- Definition: https://schema.org/Property

The dataset tabby file also provides the flexibility to define
custom properties for the files belonging to the specific dataset,
via the recognized ``filecolumn``property. This would tell a tabby
processor to search for and parse extra columns in addition to the
recognized ones detailed in the "Files tabby file" section below.
It is expected that in addition to the ``name`` of the custom property
users also provide the ``definition`` and ``syntax`` of the property,
for example using schema.org URLs as is used throughout this
specification.

==========  ========== ============ ==========
col1        col2         col3         col4
==========  ========== ============ ==========
filecolumn  <name>     <definition> <syntax>
==========  ========== ============ ==========


Files tabby file
****************

In the TSV file that provides metadata for a dataset's files,
each row describes all properties of a single file, while columns
of a single header row define the file properties to be provided.
There are four recognized properties for files:

====================  ===============  ====================  ==========
filename              url*             contentbytesize*      md5*
====================  ===============  ====================  ==========
<relative UNIX Path>  <file location>  <file size in bytes>  <checksum>
====================  ===============  ====================  ==========

Only ``filename`` is required. All other columns are optional,
and can be left empty or skipped. Below is the description of
recognized columns.

filename [required]
===================

Definition: https://schema.org/name

The path, UNIX-style (forward slashes), relative to dataset's top level
directory. This identifies the file and its location in the dataset.

url [optional]
==============

Definition: https://schema.org/contentUrl

A URL from which the particular file can be retrieved. This allows a
catalog to display an actionable link for the file.

These URLs may point, for example, to data already published in
repositories (such as ProteomeCentral ProteomeXchange or Gene
Expression Omnibus), cloud hosting services which provide individual
file download links, or, in fact, any other location.

contentbytesize [optional]
==========================

Definition: https://schema.org/contentSize

File size, in bytes. This allows a catalog to display file size.

md5 [optional]
==============

Content checksum. This allows integrity checks.

MD5 is the recommended checksum. Other checksums (e.g. sha1, sha256)
can be used, in which case the column name (lowercase) should be
changed accordingly.

Custom file property [optional]
===============================

As explained before, the dataset tabby file can also specify
custom properties for files. Custom properties specified in the dataset
file via the `filecolumn` can then have a corresponding column header
in here in the files tabby file.
