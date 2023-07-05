from pathlib import Path
import pytest

from datalad_next.tests.utils import md5sum

import datalad_tabby.tests as dttests

from .. import (
    xlsx2tabby,
    tabby2xlsx,
)


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


def test_tsv2xslx_roundtrip(tmp_path, tabby_tsv_record):
    xlsx_dir = tmp_path / 'xslx'
    tsv_dir = tmp_path / 'tsvs'
    for d in (xlsx_dir, tsv_dir):
        d.mkdir()

    xlsx_fpath = tabby2xlsx(tabby_tsv_record['root_sheet'], xlsx_dir)
    tsvs = xlsx2tabby(xlsx_fpath, tsv_dir)

    # roundtripping via XLSX gives bit identicial outcome compared to
    # TSV starting point
    assert tabby_tsv_record['md5'] == {s.name: md5sum(s) for s in tsvs}
