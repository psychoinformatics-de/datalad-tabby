from datalad.conftest import setup_package

pytest_plugins = "datalad_next.tests.fixtures"

from datalad_tabby.tests.fixtures import (
    # provides the tabby "demorecord" that is shipped with the sources
    tabby_tsv_record,
    # same again, but in a single-record-per-dir layout
    tabby_tsv_singledir_record,
    # elementary tabby record comprising the key TSV buildiung blocks
    tabby_record_basic_components,
    # no-LD elementary record with overrides
    tabby_record_w_overrides,
)
