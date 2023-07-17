"""Load a tabby metadata record"""

__docformat__ = 'restructuredtext'

import json
import logging

import datalad_next.commands as dc
from datalad_next.constraints import (
    EnsureChoice,
    EnsurePath,
)
from datalad_next.uis import ui_switcher as ui

from datalad_tabby.io import load_tabby

lgr = logging.getLogger('datalad.tabby.load')


class _ParamValidator(dc.EnsureCommandParameterization):
    def __init__(self):
        super().__init__(
            param_constraints=dict(
                path=EnsurePath(lexists=True),
                mode=EnsureChoice('jsonld', 'json', 'single')
            ),
        )


@dc.build_doc
class Load(dc.ValidatedInterface):
    """Load a tabby metadata record
    """

    result_renderer = 'tailored'
    _validator_ = _ParamValidator()
    _params_ = dict(
        path=dc.Parameter(
            args=("path",),
            doc="""Path of the root tabby record component"""),
        mode=dc.Parameter(
            args=("--mode",),
            doc="""The mode with which to load a tabby record.""",
        ),
    )

    @staticmethod
    @dc.eval_results
    def __call__(
        path,
        mode: str = 'jsonld',
    ):
        rec = load_tabby(
            path,
            # TODO expose as parameter
            single=True,
            jsonld=mode == 'jsonld',
            recursive=mode != 'single'
        )

        yield dc.get_status_dict(
            action='tabby_load',
            path=path,
            status='ok',
            tabby=rec,
        )

    @staticmethod
    def custom_result_renderer(res, **kwargs):
        """This result renderer output only the tabby record,
        in a compact JSON-line format -- only if status==ok"""
        # the command implementation does not call other commands inside,
        # hence we need not anticipate foreign results to pass through
        #if res['status'] != 'ok':
        #    generic_result_renderer(res)
        #    return

        ui.message(json.dumps(
            res['tabby'],
            separators=(',', ':'),
            indent=None,
        ))
