"""DataLad Tabby extension for working with tabular data"""

__docformat__ = 'restructuredtext'

import logging
lgr = logging.getLogger('datalad.tabby')

# Defines a datalad command suite.
# This variable must be bound as a setuptools entrypoint
# to be found by datalad
command_suite = (
    # description of the command suite, displayed in cmdline help
    "Utilities for working with the `tabby` metadata format",
    [
        ('datalad_tabby.load', 'Load', 'tabby-load', 'tabby_load'),
    ]
)

from . import _version
__version__ = _version.get_versions()['version']
