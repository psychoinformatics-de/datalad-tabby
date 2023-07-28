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

    # compaction refused when not in jsonld mode
    with pytest.raises(CommandParametrizationError):
        tabby_load(tabby_tsv_record['root_sheet'],
                   mode='json', compact='@context')


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
        recursive=False,
        jsonld=False)


def test_load_compaction(tabby_tsv_record, tmp_path):
    rec = tabby_load(tabby_tsv_record['root_sheet'], mode='jsonld')[0]['tabby']
    # we have a redundant context spec in each funding record
    assert all('@context' in r for r in rec['funding'])

    # but compaction takes it out, when we define all relevant IRIs
    # in a global compaction context
    compaction = {
        "schema": "https://schema.org/",
    }
    compaction_fname = tmp_path / 'compact.jsonld'
    compaction_fname.write_text(json.dumps(compaction))
    # test def via structured data, or JSON file input
    for c in compaction, compaction_fname:
        rec = tabby_load(
            tabby_tsv_record['root_sheet'],
            mode='jsonld',
            compact=c,
        )[0]['tabby']
        # we have a redundant context spec in each funding record
        assert not any('@context' in r for r in rec['schema:funding'])
        assert rec['@context'] == compaction

    # smoke test for using the context that is defined in the root
    # record for compaction
    rec = tabby_load(
        tabby_tsv_record['root_sheet'],
        mode='jsonld',
        compact='@context',
    )[0]['tabby']
    # this time "funding" has a compact, standalone definition
    assert not any('@context' in r for r in rec['funding'])
