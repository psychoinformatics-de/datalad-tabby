import json
from pathlib import Path
import pytest

from datalad_next.tests.utils import md5sum

import datalad_tabby.tests as dttests


@pytest.fixture(autouse=False, scope="session")
def tabby_tsv_record():
    srcdir = Path(dttests.__file__).parent / 'data' / 'demorecord'
    sheets = list(srcdir.glob('tabbydemo_*.tsv'))

    root_sheet = srcdir / 'tabbydemo_dataset.tsv'
    assert root_sheet in sheets
    assert root_sheet.exists()

    yield dict(
        root_sheet=root_sheet,
        sheets=sheets,
        md5={s.name: md5sum(s) for s in sheets},
    )


@pytest.fixture(scope="session")
def tabby_record_basic_components(tmp_path_factory):
    rdir = tmp_path_factory.mktemp("rec")
    single = rdir / 'rec__meta_singletab.tsv'
    single.write_text(
        # empty line up top
        "\n"
        "\t\t\t\n"
        "one\t1\n"
        "two\t2\t\n"
        "#ignoreme\t\n"
        "twomany\t1\tb\t3\n"
        "sparse\ts\t\tf\n"
        # keys with no value are skipped
        "undefined\t\t\t\n"
    )
    single_t = {
        'one': '1',
        'two': '2',
        'twomany': ['1', 'b', '3'],
        'sparse': ['s', '', 'f'],
    }
    many = rdir / 'rec__meta_manytab.tsv'
    many.write_text(
        # first row MUST define header
        # there are two k2 columns, indicating that two values can be given
        "k1\tk2\tk2\tk3\n"
        "#headercomment\t\t\n"
        "a\tb\t\tc\n"
        "#ignoreme\t\t\t\n"
        # there is no such thing as a field-comment
        "1\t2\t\t#3\n"
        # empty fields are skipped
        "\t\t\tl\n"
        # t0o few fields are OK, remaining keys are skipped
        "one\ttwo\n"
        # too many fields values are appended to last key
        # this is useful for representing a single
        # "and any number of X..." properties
        "a\tb\t\tc\t1\t2\t3\n"
        # merge values in columns with identical names
        "a\t1\t2\tb\n"
    )
    many_t = [
        {'k1': 'a', 'k2': 'b', 'k3': 'c'},
        {'k1': '1', 'k2': '2', 'k3': '#3'},
        {'k3': 'l'},
        {'k1': 'one', 'k2': 'two'},
        {'k1': 'a', 'k2': 'b', 'k3': ['c', '1', '2', '3']},
        {'k1': 'a', 'k2': ['1', '2'], 'k3': 'b'},
    ]
    root = rdir / 'rec__meta_root.tsv'
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
