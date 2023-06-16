"""DataLad Tabby Clone command"""

__docformat__ = 'restructuredtext'

from os.path import curdir
from os.path import abspath

from datalad_next.commands import (
    EnsureCommandParameterization,
    ValidatedInterface,
    Parameter,
    build_doc,
    datasetmethod,
    eval_results,
    generic_result_renderer,
    get_status_dict,
    ParameterConstraintContext,
)
from datalad_next.constraints import (
    EnsurePath,
)

import logging
lgr = logging.getLogger('datalad.tabby.clone')


class CloneParameterValidator(EnsureCommandParameterization):
    """"""

    def __init__(self):
        super().__init__(
            param_constraints=dict(
                tabby_file=EnsurePath()
            ),
            joint_constraints={
            },
        )


# decoration auto-generates standard help
@build_doc
# all commands must be derived from Interface
class Clone(ValidatedInterface):
    # first docstring line is used a short description in the cmdline help
    # the rest is put in the verbose help and manpage
    """Short description of the command

    Long description of arbitrary volume.
    """

    _validator_ = CloneParameterValidator()

    # parameters of the command, must be exhaustive
    _params_ = dict(
        tabby_file=Parameter(
            args=("-t", "--tabby-file"),
            doc="""Just a placeholder for the besic setup"""),
    )

    @staticmethod
    # generic handling of command results (logging, rendering, filtering, ...)
    @eval_results
    # signature must match parameter list above
    # additional generic arguments are added by decorators
    def __call__(
        tabby_file=abspath(curdir),
    ):
        yield get_status_dict(
            action='tabby_clone',
            path=tabby_file,
            status='error',
            message="This command has not yet been implemented",
        )
