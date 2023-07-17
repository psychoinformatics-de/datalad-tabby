import json
import pytest

from datalad.api import tabby_load

from datalad_next.constraints.exceptions import CommandParametrizationError

from datalad_tabby.io import load_tabby


def test_arguments(tabby_tsv_record):
    with pytest.raises(CommandParametrizationError):
        tabby_load()

    with pytest.raises(CommandParametrizationError):
        tabby_load(tabby_tsv_record['root_sheet'], mode='bs')


def test_load(tabby_tsv_record, datalad_noninteractive_ui):
    res = tabby_load(tabby_tsv_record['root_sheet'])
    assert len(res) == 1
    res = res[0]
    assert res['status'] == 'ok'
    uil = datalad_noninteractive_ui.log
    assert len(uil) == 1
    assert uil[0][0] == 'message'
    # the default result renderer puts out the same info (and only that)
    # what the loader utility produces
    rec = uil[0][1]
    assert json.loads(
        ''.join(rec)) == load_tabby(tabby_tsv_record['root_sheet'])


def test_load_nonrecursive(tabby_tsv_record, datalad_noninteractive_ui):
    res = tabby_load(
        tabby_tsv_record['root_sheet'],
        mode='single'
    )
    res = res[0]
    uil = datalad_noninteractive_ui.log
    rec = uil[0][1]
    assert json.loads(
        ''.join(rec)) == load_tabby(
        tabby_tsv_record['root_sheet'],
        recursive=False)
