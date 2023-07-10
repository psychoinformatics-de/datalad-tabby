import json
import pytest

from .. import load_tabby

from . import tabby_tsv_record


@pytest.fixture(scope="session")
def tabby_record_w_overrides(tmp_path_factory):
    rdir = tmp_path_factory.mktemp("rec")
    single = rdir / 'rec_singletab.tsv'
    single.write_text(
        "one\t1\n"
        "two\t2\tzwei\n"
    )
    single_ovr = rdir / 'rec_singletab.override.json'
    single_ovr.write_text(json.dumps({
        # new key
        '@id': 'myid-{one[0]}',
        # amend key
        'two': ['{two[0]}', '{two[1]}', 'dwa'],
    }))
    single_t = {
        '@id': 'myid-1',
        'one': '1',
        'two': ['2', 'zwei', 'dwa'],
    }
    many = rdir / 'rec_manytab.tsv'
    many.write_text(
        "k1\tk2\tk2\tk3\n"
        "1\t2\tzwei\t3\n"
        "a\tb\tb\tc\n"
    )
    many_ovr = rdir / 'rec_manytab.override.json'
    many_ovr.write_text(json.dumps({
        # new key
        '@id': 'myid-{k1[0]}',
        # amend key
        'k2': ['{k2[0]}', '{k2[1]}', 'dwa'],
    }))
    many_t = [
        {'@id': 'myid-1', 'k1': '1', 'k2': ['2', 'zwei', 'dwa'], 'k3': '3'},
        {'@id': 'myid-a', 'k1': 'a', 'k2': ['b', 'b', 'dwa'], 'k3': 'c'},
    ]
    root = rdir / 'rec_root.tsv'
    root.write_text(
        "single\t@tabby-single-singletab\n"
        "many\t@tabby-many-manytab\n"
    )
    root_t = {
        'single': single_t,
        'many': many_t,
    }
    yield dict(
        input=dict(root=root, single=single, many=many),
        target=dict(root=root_t, single=single_t, many=many_t),
    )


def test_load_tabby(tabby_record_w_overrides):
    trwo = tabby_record_w_overrides
    loaded = load_tabby(
        trwo['input']['root'],
        single=True,
        jsonld=False,
    )
    assert loaded['single'] == trwo['target']['single']
    assert loaded['many'] == trwo['target']['many']
