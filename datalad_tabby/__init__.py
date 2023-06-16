"""DataLad Tabby extension for working with tabular data"""

__docformat__ = 'restructuredtext'

import logging
lgr = logging.getLogger('datalad.tabby')

# Defines a datalad command suite.
# This variable must be bound as a setuptools entrypoint
# to be found by datalad
command_suite = (
    # description of the command suite, displayed in cmdline help
    "DataLad Tabby command suite",
    [
        # specification of a command, any number of commands can be defined
        (
            # importable module that contains the command implementation
            'datalad_tabby.clone',
            # name of the command class implementation in above module
            'Clone',
            # optional name of the command in the cmdline API
            'tabby-clone',
            # optional name of the command in the Python API
            'tabby_clone'
        ),
    ]
)

from . import _version
__version__ = _version.get_versions()['version']
