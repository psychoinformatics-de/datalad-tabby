from pathlib import Path

import pytest

from datalad_next.tests.utils import md5sum

from ..xlsx import (
    xlsx2tabby,
    tabby2xlsx,
)


def test_tsv2xslx_roundtrip(tmp_path, tabby_tsv_record):
    xlsx_dir = tmp_path / 'xslx'
    tsv_dir = tmp_path / 'tsvs'
    for d in (xlsx_dir, tsv_dir):
        d.mkdir()

    xlsx_fpath = tabby2xlsx(tabby_tsv_record['root_sheet'], xlsx_dir)
    tsvs = xlsx2tabby(xlsx_fpath, tsv_dir)

    # roundtripping via XLSX gives bit identical outcome compared to
    # TSV starting point
    assert tabby_tsv_record['md5'] == {s.name: md5sum(s) for s in tsvs}


def test_raiseon_missing_datasetsheet(tmp_path):
    with pytest.raises(ValueError):
        tabby2xlsx(Path('absurd'), tmp_path)
