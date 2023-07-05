
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
