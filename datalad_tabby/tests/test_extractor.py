from datalad.api import meta_extract

from ..extractor import TabbyExtractor


def test_extractor_version():
    ex = TabbyExtractor('someds', 'refcommit')
    assert str(ex.get_id()) == '325fb444-ae7b-54b3-9fdd-621ab1e5005c'


def test_extractor_nometa(existing_dataset):
    res = meta_extract(
        'tabby', dataset=existing_dataset,
        on_failure='ignore', return_type='item-or-list',
        result_renderer='disabled',
    )
    assert res['status'] == 'impossible'


def test_extractor_minimal(existing_dataset):
    ds = existing_dataset
    mfpath = ds.pathobj / '.datalad' / 'tabby' / 'self' / 'dataset.tsv'
    mfpath.parent.mkdir(parents=True)
    mfpath.write_text('title\tmy dataset\n')
    res = meta_extract(
        'tabby', dataset=ds, return_type='item-or-list',
        result_renderer='disabled',
    )
    assert res['status'] == 'ok'
    meta = res['metadata_record']['extracted_metadata']
    assert meta == {'title': 'my dataset'}


def test_extractor_invalidmeta(existing_dataset):
    ds = existing_dataset
    mfpath = ds.pathobj / '.datalad' / 'tabby' / 'self' / 'dataset.tsv'
    mfpath.parent.mkdir(parents=True)
    mfpath.write_text('title\t@tabby-single-missing\n')
    res = meta_extract(
        'tabby', dataset=ds,
        on_failure='ignore', return_type='item-or-list',
        result_renderer='disabled',
    )
    assert res['status'] == 'error'
    assert 'no such file' in res['error_message'].lower()
