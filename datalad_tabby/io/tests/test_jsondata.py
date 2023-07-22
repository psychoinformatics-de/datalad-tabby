import json

from .. import load_tabby


def test_load_tabby_import_via_jsondata(tmp_path):
    # minimalistic record in singledir format
    root = tmp_path / 'root.tsv'
    root.write_text('name\tmyname\n')
    comp = tmp_path / 'comp.tsv'
    comp.write_text('sub\tsome\n')
    # and the key bit: the linkage between the sheets is defined
    # in a override
    root_json = tmp_path / 'root.json'
    root_json.write_text(json.dumps(
        {'parts': "@tabby-single-comp"}
    ))
    loaded = load_tabby(
        root,
        single=True,
        jsonld=False,
    )
    assert 'parts' in loaded
    # TODO this is broken ATM
    # https://github.com/psychoinformatics-de/datalad-tabby/issues/91
    assert loaded['parts'] == {'sub': 'some'}
