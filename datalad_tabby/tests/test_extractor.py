import pytest
from datalad.api import meta_extract

from datalad_next.datasets import (
    Dataset,
    LegacyGitRepo,
)
from datalad_next.exceptions import NoDatasetFound

from ..extractor import (
    TabbyExtractor,
    isVersionOf,
)


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
    # load with unrelated isVersionOf, to force the extractor to
    # amend, rather than override the existing info
    mfpath.write_text(f'title\tmy dataset\n{isVersionOf}\tsomething\n')
    ds.save(result_renderer='disabled')
    res = meta_extract(
        'tabby', dataset=ds, return_type='item-or-list',
        result_renderer='disabled',
    )
    assert res['status'] == 'ok'
    meta = res['metadata_record']['extracted_metadata']
    assert meta['title'] == 'my dataset'
    assert len(meta[isVersionOf]) == 2
    assert meta[isVersionOf][0] == 'something'
    assert meta[isVersionOf][1]['@id']


def test_extractor_minimal_nods(tmp_path):
    # we run on a plain git repo
    repo = LegacyGitRepo(tmp_path)
    repo.call_git(['init'])
    mfpath = repo.pathobj / '.datalad' / 'tabby' / 'self' / 'dataset.tsv'
    mfpath.parent.mkdir(parents=True)
    mfpath.write_text(f'title\tmy dataset\n')
    repo.call_git(['add', '.'])
    repo.call_git(['commit', '-m', 'minimal metadata'])
    ds = Dataset(repo.pathobj)
    with pytest.raises(NoDatasetFound):
        meta_extract(
            'tabby', dataset=ds, return_type='item-or-list',
            result_renderer='disabled',
        )


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


def test_extractor_collection_only(existing_dataset):
    ds = existing_dataset
    mfpath = ds.pathobj / '.datalad' / 'tabby' / 'dscollection' / \
        'something_dataset.tsv'
    mfpath.parent.mkdir(parents=True)
    # load with unrelated isVersionOf, to force the extractor to
    # amend, rather than override the existing info
    mfpath.write_text('title\tcolds1\n')
    # write a second, broken one
    (mfpath.parent / 'broken_dataset.tsv'
     ).write_text('arrgh\t@tabby-single-missing\n')
    # write a third, empty one
    (mfpath.parent / 'empty_dataset.tsv').write_text('\t\t\n')
    ds.save(result_renderer='disabled')
    res = meta_extract(
        'tabby', dataset=ds, return_type='item-or-list',
        result_renderer='disabled',
    )
    assert res['status'] == 'ok'
    meta = res['metadata_record']['extracted_metadata']
    assert '@graph' in meta
    recs = meta['@graph']
    # we still get info on the rootds, but only IDs for linkage
    assert len(recs) == 2
    assert recs[0][isVersionOf]['@id']
    # collection records are relayed as-is
    assert recs[1] == {'title': 'colds1'}
