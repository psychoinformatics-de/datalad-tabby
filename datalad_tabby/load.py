"""Load a tabby metadata record"""

from __future__ import annotations

__docformat__ = 'restructuredtext'

import json
import logging
from pathlib import Path
from typing import Dict

import datalad_next.commands as dc
from datalad_next.constraints import (
    AnyOf,
    EnsureChoice,
    EnsureJSON,
    EnsurePath,
    EnsureValue,
)
from datalad_next.constraints.basic import (
    EnsureDType,
)
from datalad_next.constraints.exceptions import ParameterConstraintContext

from datalad_next.uis import ui_switcher as ui

from datalad_tabby.io import load_tabby

lgr = logging.getLogger('datalad.tabby.load')


load_modes = ('jsonld', 'json', 'single')


class _ParamValidator(dc.EnsureCommandParameterization):
    def __init__(self):
        super().__init__(
            param_constraints=dict(
                path=EnsurePath(lexists=True),
                mode=EnsureChoice(*load_modes),
                compact=AnyOf(
                    EnsureValue('@context'),
                    EnsureJSON(),
                    EnsurePath(),
                    EnsureDType(dict),
                ),
            ),
            joint_constraints={
                ParameterConstraintContext(
                    ('mode', 'compact'), 'mode requirement'):
                        self._check_compaction_jsonld_mode,
            },
        )

    def _check_compaction_jsonld_mode(self, mode, compact):
        if compact and mode != 'jsonld':
            self.raise_for(
                dict(mode=mode, compact=compact),
                "JSON-LD compaction requires mode 'jsonld'"
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
            choices=load_modes,
        ),
        compact=dc.Parameter(
            args=('--compact',),
            metavar='CONTEXT',
            doc="""A context for JSON-LD compaction of the loaded record
            (requires mode 'jsonld').""",
        ),
    )

    @staticmethod
    @dc.eval_results
    def __call__(
        path,
        mode: str = 'jsonld',
        compact: None | Path | Dict = None,
    ):
        rec = load_tabby(
            path,
            single=True,
            jsonld=mode == 'jsonld',
            recursive=mode != 'single'
        )

        if compact:
            from pyld import jsonld
            if compact == '@context':
                compact = rec.get('@context', {})
            elif isinstance(compact, Path):
                compact = json.load(compact.open())
            rec = jsonld.compact(rec, compact)

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
