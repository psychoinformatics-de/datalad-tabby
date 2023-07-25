import json
import pytest

from .. import load_tabby


def test_load_tabby_import_via_jsondata(tmp_path):
    # minimalistic record in singledir format
    root = tmp_path / 'root.json'
    root.write_text(json.dumps({
        'sreq': '@tabby-single-sreq',
        'sopt': '@tabby-optional-single-sopt',
        'mreq': '@tabby-many-mreq',
        'mopt': '@tabby-optional-many-mopt',
    }))
    files = {}
    for name, content in (
            ('sreq.tsv', 'k1\tv1\n'),
            ('sopt.tsv', 'k2\tv1\n'),
            ('mreq.json', '[{"k1":"v1"},{"k1":"v2"}]'),
            ('mopt.json', '[{"k2":"v1"},{"k2":"v2"}]'),
    ):
        f = tmp_path / name
        f.write_text(content)
        files[name] = f

    loaded = load_tabby(
        root,
        single=True,
        jsonld=False,
    )
    assert loaded == {
        'sreq': {'k1': 'v1'},
        'sopt': {'k2': 'v1'},
        'mreq': [{'k1': 'v1'}, {'k1': 'v2'}],
        'mopt': [{'k2': 'v1'}, {'k2': 'v2'}],
    }
    # we can remove the optional imports, and simply not have the info
    files['sopt.tsv'].unlink()
    files['mopt.json'].unlink()
    loaded = load_tabby(
        root,
        single=True,
        jsonld=False,
    )
    assert loaded == {
        'sreq': {'k1': 'v1'},
        'mreq': [{'k1': 'v1'}, {'k1': 'v2'}],
    }
    # but required imports fail
    files['mreq.json'].unlink()
    with pytest.raises(FileNotFoundError):
        loaded = load_tabby(
            root,
            single=True,
            jsonld=False,
        )

