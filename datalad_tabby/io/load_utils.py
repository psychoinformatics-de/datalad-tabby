"""(Standalone) helpers for loading `tabby` records"""

from __future__ import annotations

from pathlib import Path
from typing import (
    Dict,
    List,
)


def _assign_context(obj: Dict, ctx: Dict):
    if '@context' in obj:
        # TODO report when redefinitions occur
        # TODO in principle a table could declare a context, but this is
        # a theoretical possibility that is neither advertised nor tested
        obj['@context'].update(ctx)  # pragma: no cover
    else:
        obj['@context'] = ctx


def _get_tabby_prefix_from_sheet_fpath(fpath: Path) -> str:
    stem = fpath.stem
    if '_' not in stem:
        return ''
    else:
        # stem up to, but not including, the last '_'
        return stem[:(-1) * stem[::-1].index('_') - 1]


def _get_index_after_last_nonempty(val: List) -> int:
    for i, v in enumerate(val[::-1]):
        if v:
            return len(val) - i
    return 0


def _build_import_trace(src: Path, trace: List) -> List:
    if src in trace:
        raise RecursionError(
            f'circular import: {src} is (indirectly) referencing itself')

    # TODO if we ever want to go parallel, we should produce an independent
    # list instance here
    trace.append(src)
    return trace


def _compact_obj(obj: Dict) -> Dict:
    # simplify single-item lists to a plain value
    return {
        k:
        # we let any @context pass-through as-is to avoid ANY sideeffects
        # of fiddling with the complex semantics of context declaration
        # structure
        vals if k == '@context' else vals if len(vals) > 1 else vals[0]
        for k, vals in obj.items()
        # let anything pass that is not a container, or a container that
        # is not entirely made up of empty containers (at the first level)
        if not isinstance(vals, (dict, list)) or any(
            not isinstance(v, (dict, list)) or v for v in vals)
    }


def _manyrow2obj(
    vals: List,
    fieldnames: List,
) -> Dict:
    # if we get here, this is a value row, representing an individual
    # object
    obj = {}
    if len(vals) > len(fieldnames):
        # we have extra values, merge then into the column
        # corresponding to the last key
        last_key_idx = len(fieldnames) - 1
        lc_vals = vals[last_key_idx:]
        lc_vals = lc_vals[:_get_index_after_last_nonempty(lc_vals)]
        vals[last_key_idx] = lc_vals

    # merge values with keys, amending duplicate keys as necessary
    for i, k in enumerate(fieldnames):
        if i >= len(vals):
            # no more values defined in this row, skip this key
            continue
        v = vals[i]
        if not v:
            # no value, nothing to store or append
            continue
        # treat any key as a potential multi-value scenario
        k_vals = obj.get(k, [])
        k_vals.append(v)
        obj[k] = k_vals

    return obj


def _sanitize_override_key(key: str) -> str:
    """Sanitize a key for use with the Python format language

    An incoming key could be anything, but for use with the format
    language it needs to become a valid Python variable identifier.
    """
    # here comes an adhoc set of cases we found necessary to handle
    return key.replace('[', '_').replace(']', '_')
