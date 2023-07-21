import json

from .. import load_tabby


def test_load_tabby(tabby_record_w_overrides):
    trwo = tabby_record_w_overrides
    loaded = load_tabby(
        trwo['input']['root'],
        single=True,
        jsonld=False,
    )
    assert loaded['single'] == trwo['target']['single']
    assert loaded['many'] == trwo['target']['many']


def test_load_tabby_import_via_override(tmp_path):
    # minimalistic record in singledir format
    root = tmp_path / 'root.tsv'
    root.write_text('name\tmyname\n')
    comp = tmp_path / 'comp.tsv'
    comp.write_text('sub\tsome\n')
    # and the key bit: the linkage between the sheets is defined
    # in a override
    root_ov = tmp_path / 'root.override.json'
    root_ov.write_text(json.dumps(
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
    #assert loaded['parts'] == {'sub': 'some'}
