"""Utilities for loading a `tabby` record from disk"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import (
    Dict,
    List,
)

from .load_utils import (
    _assigned_context,
    _compact_obj,
    _build_import_trace,
    _build_overrides,
    _get_corresponding_context,
    _get_corresponding_jsondata_fpath,
    _get_corresponding_sheet_fpath,
    _get_index_after_last_nonempty,
    _manyrow2obj,
)


def load_tabby(
    src: Path,
    *,
    single: bool = True,
    jsonld: bool = True,
    recursive: bool = True,
    cpaths: List | None = None,
) -> Dict | List:
    """Load a tabby (TSV) record as structured (JSON(-LD)) data

    The record is identified by the table/sheet file path ``src``. This need
    not be the root 'dataset' sheet, but can be any component of the full
    record.

    The ``single`` flag determines whether the record is interpreted as a
    single entity (i.e., JSON object), or many entities (i.e., JSON array of
    (homogeneous) objects).  Depending on the ``single`` flag, either a
    ``dict`` or a ``list`` is returned.

    Other tabby tables/sheets are loaded when ``@tabby-single|many-`` import
    statements are discovered. The corresponding data structures then replace
    the import statement at its location. Setting the ``recursive`` flag to
    ``False`` disables table import, which will result in only the record
    available at the ``src`` path being loaded.

    With the ``jsonld`` flag, a declared or default JSON-LD context is
    loaded and inserted into the record.
    """
    std_convention_path = Path(__file__).parent / 'conventions'
    if cpaths is None:
        cpaths = [std_convention_path]
    else:
        cpaths.append(std_convention_path)

    return (_load_tabby_single if single else _load_tabby_many)(
        src=src,
        jsonld=jsonld,
        recursive=recursive,
        trace=[],
        cpaths=cpaths,
    )


def _load_tabby_single(
    *,
    src: Path,
    jsonld: bool,
    recursive: bool,
    trace: List,
    cpaths: List,
) -> Dict:
    jfpath = _get_corresponding_jsondata_fpath(src, cpaths)
    obj = json.load(jfpath.open()) if jfpath.exists() else {}
    if obj and not src.exists():
        # early exit, there is no tabular data
        return _postproc_tabby_obj(
            obj, src=src, jsonld=jsonld, recursive=recursive, trace=trace,
            cpaths=cpaths)

    with src.open(newline='') as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        # row_id is useful for error reporting
        for row_id, row in enumerate(reader):
            # row is a list of field, with only as many items
            # as this particular row has columns
            if not len(row) or not row[0] or row[0].startswith('#'):
                # skip empty rows, rows with no key, or rows with
                # a comment key
                continue
            key = row[0]
            val = row[1:]
            # cut `val` short and remove trailing empty items
            val = val[:_get_index_after_last_nonempty(val)]
            if not val:
                # skip properties with no value(s)
                continue
            # we do not amend values for keys!
            # another row for an already existing key overwrites
            # we support "sequence" values via multi-column values
            # supporting two ways just adds unnecessary complexity
            obj[key] = val

    return _postproc_tabby_obj(
        obj, src=src, jsonld=jsonld, recursive=recursive, trace=trace,
        cpaths=cpaths)


def _postproc_tabby_obj(
    obj: Dict,
    src: Path,
    jsonld: bool,
    recursive: bool,
    trace: List,
    cpaths: List,
):
    # look for @tabby-... imports in values, and act on them
    obj = {
        key:
        [
            _resolve_value(
                v,
                src,
                jsonld=jsonld,
                recursive=recursive,
                trace=trace,
                cpaths=cpaths,
            )
            for v in (val if isinstance(val, list) else [val])
        ]
        for key, val in obj.items()
    }
    # apply any overrides
    obj.update(_build_overrides(src, obj, cpaths))

    obj = _compact_obj(obj)

    if not jsonld:
        # early exit
        return obj

    # with jsonld==True, looks for a context
    ctx = _get_corresponding_context(src, cpaths)
    if ctx:
        _assigned_context(obj, ctx)

    return obj


def _load_tabby_many(
    *,
    src: Path,
    jsonld: bool,
    recursive: bool,
    trace: List,
    cpaths: List,
) -> List[Dict]:
    obj_tmpl = {}
    array = list()
    jfpath = _get_corresponding_jsondata_fpath(src, cpaths)
    if jfpath.exists():
        jdata = json.load(jfpath.open())
        if isinstance(jdata, dict):
            obj_tmpl = jdata
        elif isinstance(jdata, list):
            array.extend(
                _postproc_tabby_obj(
                    obj, src=src, jsonld=jsonld, recursive=recursive,
                    trace=trace, cpaths=cpaths)
                for obj in jdata
            )
    if array and not src.exists():
        # early exit, there is no tabular data
        return array

    # the table field/column names have purposefully _nothing_ to do with any
    # possibly loaded JSON data
    fieldnames = None

    with src.open(newline='') as tsvfile:
        # we cannot use DictReader -- we need to support identically named
        # columns
        reader = csv.reader(tsvfile, delimiter='\t')
        # row_id is useful for error reporting
        for row_id, row in enumerate(reader):
            # row is a list of field, with only as many items
            # as this particular row has columns
            if not len(row) \
                    or row[0].startswith('#') \
                    or all(v is None for v in row):
                # skip empty rows, rows with no key, or rows with
                # a comment key
                continue
            if fieldnames is None:
                # the first non-ignored row defines the property names/keys
                # cut `val` short and remove trailing empty items
                fieldnames = row[:_get_index_after_last_nonempty(row)]
                continue

            obj = obj_tmpl.copy()
            obj.update(_manyrow2obj(row, fieldnames))
            obj = _postproc_tabby_obj(
                obj, src=src, jsonld=jsonld, recursive=recursive, trace=trace,
                cpaths=cpaths)

            # simplify single-item lists to a plain value
            array.append(obj)
    return array


def _resolve_value(
    v: str,
    src_sheet_fpath: Path,
    jsonld: bool,
    recursive: bool,
    trace: List,
    cpaths: List,
):
    if not recursive:
        return v
    if not isinstance(v, str):
        return v

    if v.startswith('@tabby-single-'):
        loader = _load_tabby_single
        src = _get_corresponding_sheet_fpath(
            src_sheet_fpath, v[14:], cpaths)
    elif v.startswith('@tabby-optional-single-'):
        loader = _load_tabby_single
        src = _get_corresponding_sheet_fpath(
            src_sheet_fpath, v[23:], cpaths)
    elif v.startswith('@tabby-many-'):
        loader = _load_tabby_many
        src = _get_corresponding_sheet_fpath(
            src_sheet_fpath, v[12:], cpaths)
    elif v.startswith('@tabby-optional-many-'):
        loader = _load_tabby_many
        src = _get_corresponding_sheet_fpath(
            src_sheet_fpath, v[21:], cpaths)
    else:
        # strange, but not enough reason to fail
        return v

    trace = _build_import_trace(src, trace)

    try:
        loaded = loader(
            src=src,
            jsonld=jsonld,
            recursive=recursive,
            trace=trace,
            cpaths=cpaths,
        )
    except FileNotFoundError:
        if v.startswith('@tabby-optional-'):
            return {}
        else:
            raise
    return loaded
