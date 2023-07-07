import json

from datalad.api import tabby_load


from datalad_tabby.io import load_tabby
# TODO move to conftest.py
from datalad_next.tests.fixtures import datalad_noninteractive_ui
from datalad_tabby.io.tests import tabby_tsv_record


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

