import json

from .. import load_tabby


def test_load_tabby_import_via_jsondata(tmp_path):
    # minimalistic record in singledir format
    root = tmp_path / 'root.json'
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
    assert loaded['parts'] == {'sub': 'some'}


def test_load_tabby_json_only(tmp_path):
    root = tmp_path / 'root.json'
    root.write_text(json.dumps({
        'direct': None,
        'parts': "@tabby-many-comp",
    }))
    comp = tmp_path / 'comp.json'
    comp.write_text(json.dumps(
        [
            {'this': 1.2},
            {'import': '@tabby-single-one'},
        ]
    ))
    single = tmp_path / 'one.json'
    single.write_text(json.dumps(
        {'imported': True}
    ))
    loaded = load_tabby(
        root,
        single=True,
        jsonld=False,
    )
    assert loaded == {'direct': None,
                      'parts': [
                          {'this': 1.2},
                          {'import': {'imported': True}}
                      ]}


def test_load_tabby_many_json_tmpl(tmp_path):
    # and the key bit: the linkage between the sheets is defined
    # in a override
    root_json = tmp_path / 'root.json'
    root_json.write_text(json.dumps(
        {'parts': "@tabby-many-comp"}
    ))
    comp_tmpl = tmp_path / 'comp.json'
    comp_tmpl.write_text(json.dumps({
        'any': 3.2,
    }))
    comp = tmp_path / 'comp.tsv'
    comp.write_text('k1\tk2\nv1\tv2\nva\tvb\n')
    loaded = load_tabby(
        root_json,
        single=True,
        jsonld=False,
    )
    assert loaded == {'parts': [
        {'any': 3.2, 'k1': 'v1', 'k2': 'v2'},
        {'any': 3.2, 'k1': 'va', 'k2': 'vb'}
    ]}
