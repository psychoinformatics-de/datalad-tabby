"""Utilities for loading a `tabby` record from disk"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import (
    Dict,
    List,
)

from charset_normalizer import from_path as cs_from_path

from .load_utils import (
    _assign_context,
    _compact_obj,
    _build_import_trace,
    _get_index_after_last_nonempty,
    _get_tabby_prefix_from_sheet_fpath,
    _manyrow2obj,
    _sanitize_override_key,
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
    ldr = _TabbyLoader(
        jsonld=jsonld,
        recursive=recursive,
        cpaths=cpaths,
    )
    return ldr(src=src, single=single)


class _TabbyLoader:
    def __init__(
        self,
        jsonld: bool = True,
        recursive: bool = True,
        cpaths: List[Path] | None = None,
    ):
        std_convention_path = Path(__file__).parent / 'conventions'
        if cpaths is None:
            cpaths = [std_convention_path]
        else:
            cpaths.append(std_convention_path)
        self._cpaths = cpaths
        self._jsonld = jsonld
        self._recursive = recursive

    def __call__(self, src: Path, *, single: bool = True):
        return (self._load_single if single else self._load_many)(
            src=src,
            trace=[],
        )

    def _load_single(
        self,
        *,
        src: Path,
        trace: List,
    ) -> Dict:
        jfpath = self._get_corresponding_jsondata_fpath(src)
        obj = json.load(jfpath.open()) if jfpath.exists() else {}
        if obj and not src.exists():
            # early exit, there is no tabular data
            return self._postproc_obj(
                obj,
                src=src,
                trace=trace,
            )

        try:
            obj.update(self._parse_tsv_single(src))
        except UnicodeDecodeError:
            # by default Path.open() uses locale.getencoding()
            # that didn't work, try guessing
            encoding = cs_from_path(src).best().encoding
            obj.update(self._parse_tsv_single(src, encoding=encoding))

        return self._postproc_obj(obj, src=src, trace=trace)

    def _parse_tsv_single(self, src: Path, encoding: bool = None) -> Dict:
        obj = {}
        with src.open(newline='', encoding=encoding) as tsvfile:
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
        return obj

    def _load_many(
        self,
        *,
        src: Path,
        trace: List,
    ) -> List[Dict]:
        obj_tmpl = {}
        array = list()
        jfpath = self._get_corresponding_jsondata_fpath(src)
        if jfpath.exists():
            jdata = json.load(jfpath.open())
            if isinstance(jdata, dict):
                obj_tmpl = jdata
            elif isinstance(jdata, list):
                array.extend(
                    self._postproc_obj(obj, src=src, trace=trace)
                    for obj in jdata
                )
        if array and not src.exists():
            # early exit, there is no tabular data
            return array

        # the table field/column names have purposefully _nothing_
        # to do with any possibly loaded JSON data

        try:
            array.extend(
                self._parse_tsv_many(src, obj_tmpl, trace=trace, fieldnames=None)
            )
        except UnicodeDecodeError:
            # by default Path.open() uses locale.getencoding()
            # that didn't work, try guessing
            encoding = cs_from_path(src).best().encoding
            array.extend(
                self._parse_tsv_many(
                    src, obj_tmpl, trace=trace, fieldnames=None, encoding=encoding
                )
            )

        return array

    def _parse_tsv_many(
        self,
        src: Path,
        obj_tmpl: Dict,
        trace: List,
        fieldnames: List | None = None,
        encoding: str | None = None,
    ) -> List[Dict]:
        array = []
        with src.open(newline="", encoding=encoding) as tsvfile:
            # we cannot use DictReader -- we need to support identically named
            # columns
            reader = csv.reader(tsvfile, delimiter="\t")
            # row_id is useful for error reporting
            for row_id, row in enumerate(reader):
                # row is a list of field, with only as many items
                # as this particular row has columns
                if (
                    not len(row)
                    or row[0].startswith("#")
                    or all(v is None for v in row)
                ):
                    # skip empty rows, rows with no key, or rows with
                    # a comment key
                    continue
                if fieldnames is None:
                    # the first non-ignored row defines the property names/keys
                    # cut `val` short and remove trailing empty items
                    fieldnames = row[: _get_index_after_last_nonempty(row)]
                    continue

                obj = obj_tmpl.copy()
                obj.update(_manyrow2obj(row, fieldnames))
                obj = self._postproc_obj(obj, src=src, trace=trace)

                # simplify single-item lists to a plain value
                array.append(obj)
        return array

    def _resolve_value(
        self,
        v: str,
        src_fpath: Path,
        trace: List,
    ):
        if not self._recursive:
            return v
        if not isinstance(v, str):
            return v

        if v.startswith('@tabby-single-'):
            loader = self._load_single
            sheet = v[14:]
        elif v.startswith('@tabby-optional-single-'):
            loader = self._load_single
            sheet = v[23:]
        elif v.startswith('@tabby-many-'):
            loader = self._load_many
            sheet = v[12:]
        elif v.startswith('@tabby-optional-many-'):
            loader = self._load_many
            sheet = v[21:]
        else:
            # strange, but not enough reason to fail
            return v

        src = self._get_corresponding_sheet_fpath(src_fpath, sheet)
        trace = _build_import_trace(src, trace)

        try:
            loaded = loader(src=src, trace=trace)
        except FileNotFoundError:
            if v.startswith('@tabby-optional-'):
                return {}
            else:
                raise
        return loaded

    def _postproc_obj(
        self,
        obj: Dict,
        src: Path,
        trace: List,
    ):
        # look for @tabby-... imports in values, and act on them
        obj = {
            key:
            [
                self._resolve_value(v, src, trace=trace)
                for v in (val if isinstance(val, list) else [val])
            ]
            for key, val in obj.items()
        }
        # apply any overrides
        obj.update(self._build_overrides(src, obj, self._cpaths))

        obj = _compact_obj(obj)

        if not self._jsonld:
            # early exit
            return obj

        # with jsonld==True, looks for a context
        ctx = self._get_corresponding_context(src)
        if ctx:
            _assign_context(obj, ctx)

        return obj

    def _get_corresponding_jsondata_fpath(self, fpath: Path) -> Path:
        return self._cvnfb(fpath.parent / f'{fpath.stem}.json')

    def _get_record_context_fpath(self, fpath: Path) -> Path:
        prefix = _get_tabby_prefix_from_sheet_fpath(fpath)
        if prefix:
            return self._cvnfb(fpath.parent / f'{prefix}.ctx.jsonld')
        else:
            return fpath.parent / 'ctx.jsonld'

    def _get_corresponding_context_fpath(self, fpath: Path) -> Path:
        return self._cvnfb(fpath.parent / f'{fpath.stem}.ctx.jsonld')

    def _get_corresponding_context(self, src: Path):
        rec_ctx_fpath = self._cvnfb(self._get_record_context_fpath(src))
        sheet_ctx_fpath = self._cvnfb(
            self._get_corresponding_context_fpath(src),
        )
        ctx = {}
        for ctx_fpath in (rec_ctx_fpath, sheet_ctx_fpath):
            if ctx_fpath.exists():
                custom_ctx = json.load(ctx_fpath.open())
                # TODO report when redefinitions occur
                ctx.update(custom_ctx)

        return ctx

    def _get_corresponding_override_fpath(self, fpath: Path) -> Path:
        return self._cvnfb(fpath.parent / f'{fpath.stem}.override.json')

    def _build_overrides(self, src: Path, obj: Dict, cpaths):
        # sanitize key names in object
        sanitized_obj = {
            _sanitize_override_key(k): v
            for k, v in obj.items()
        }
        overrides = {}
        ofpath = self._cvnfb(self._get_corresponding_override_fpath(src))
        if not ofpath.exists():
            # we have no overrides
            return overrides
        orspec = json.load(ofpath.open())
        for k in orspec:
            spec = orspec[k]
            ov = []
            for s in (spec if isinstance(spec, list) else [spec]):
                # interpolate str spec, anything else can pass
                # through as-is
                if not isinstance(s, str):
                    ov.append(s)
                    continue
                try:
                    o = s.format(**sanitized_obj)
                except KeyError:
                    # we do not have what this override spec need, skip it
                    # TODO log this
                    continue
                ov.append(o)
            overrides[k] = ov
        return overrides

    # TODO rename `sheet` to `tsvsheet` to clarify
    def _get_corresponding_sheet_fpath(
        self, fpath: Path, sheet_name: str,
    ) -> Path:
        prefix = _get_tabby_prefix_from_sheet_fpath(fpath)
        if prefix:
            ret = fpath.parent / f'{prefix}_{sheet_name}.tsv'
        else:
            ret = fpath.parent / f'{sheet_name}.tsv'
        return self._cvnfb(ret)

    def _cvnfb(self, fpath: Path) -> Path:
        """Get convention-based fallback file path, if needed"""
        if fpath.exists():
            # this file exists, no need to search for alternatives
            return fpath

        prefix = _get_tabby_prefix_from_sheet_fpath(fpath)
        # strip any prefix and extensions from file name
        sheet = fpath.name[len(prefix) + 1:] if prefix else fpath.name
        sheet = sheet.split('.', maxsplit=1)[0]
        # determine class declaration, if there is any
        sheet_comp = sheet.split('@', maxsplit=1)
        if len(sheet_comp) == 1:
            # no class declared, return input
            return fpath
        sname, scls = sheet_comp
        for cp in self._cpaths:
            cand = cp / scls / \
                f"{prefix}" \
                f"{'_' if prefix else ''}" \
                f"{sname}{fpath.name[len(sheet):]}"
            if cand.exists():
                # stop at the first existing alternative
                return cand
        # there was no alternative, go with original
        return fpath
