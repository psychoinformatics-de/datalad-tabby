import pytest

from .. import load_tabby

from . import tabby_tsv_record


@pytest.fixture(scope="session")
def tabby_record_basic_components(tmp_path_factory):
    rdir = tmp_path_factory.mktemp("rec")
    single = rdir / 'rec_singletab.tsv'
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
    many = rdir / 'rec_manytab.tsv'
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
        "f\t\t\tl\n"
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
        {'k1': 'f', 'k3': 'l'},
        {'k1': 'one', 'k2': 'two'},
        {'k1': 'a', 'k2': 'b', 'k3': ['c', '1', '2', '3']},
        {'k1': 'a', 'k2': ['1', '2'], 'k3': 'b'},
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


def test_load_tabby(tabby_record_basic_components):
    trbc = tabby_record_basic_components
    for t in ('single', 'many', 'root'):
        loaded = load_tabby(
            trbc['input'][t],
            single=t != 'many',
            jsonld=False,
        )
        assert loaded == trbc['target'][t]
