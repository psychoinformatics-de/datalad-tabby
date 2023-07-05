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
        "k1\tk2\tk3\n"
        "#headercomment\t\t\n"
        "a\tb\tc\n"
        "#ignoreme\t\t\n"
        # there is no such thing as a field-comment
        "1\t2\t#3\n"
        # empty fields are skipped
        "f\t\tl\n"
    )
    many_t = [
        {'k1': 'a', 'k2': 'b', 'k3': 'c'},
        {'k1': '1', 'k2': '2', 'k3': '#3'},
        {'k1': 'f', 'k3': 'l'},
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
        assert load_tabby(
            trbc['input'][t],
            single=t != 'many',
            jsonld=False,
        ) == trbc['target'][t]
