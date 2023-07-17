import pytest

from .. import load_tabby


def test_load_tabby(tabby_record_basic_components):
    trbc = tabby_record_basic_components
    for t in ('single', 'many', 'root'):
        loaded = load_tabby(
            trbc['input'][t],
            single=t != 'many',
            jsonld=False,
        )
        assert loaded == trbc['target'][t]


def test_load_tabby_nonrecursive(tabby_record_basic_components):
    trbc = tabby_record_basic_components
    loaded_no_r = load_tabby(
        trbc['input']['root'],
        single=True,
        jsonld=False,
        recursive=False,
    )
    assert loaded_no_r == {
        'many': '@tabby-many-manytab',
        'single': '@tabby-single-singletab'
    }
    loaded_r = load_tabby(
        trbc['input']['root'],
        single=True,
        jsonld=False,
        recursive=True,
    )
    assert loaded_r == trbc['target']['root']


def test_load_circular(tmp_path):
    src = tmp_path / 'selfref_dataset.tsv'
    src.write_text('dummy\t@tabby-single-dataset\n')

    # recursion detected
    with pytest.raises(RecursionError) as exc:
        load_tabby(src)
    assert 'circular import' in exc.value.args[0]

    # works without recursion
    rec = load_tabby(src, recursive=False)
    assert rec['dummy'] == '@tabby-single-dataset'


def test_load_almost_tabby_import(tmp_path):
    # check that a value starting with `@tabby-` that is not
    # an actual import statement works fine
    src = tmp_path / 'strange_dataset.tsv'
    src.write_text('dummy\t@tabby-murks\n')

    rec = load_tabby(src)
    assert rec['dummy'] == '@tabby-murks'
