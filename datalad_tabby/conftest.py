from datalad.conftest import setup_package

from datalad_next.tests.fixtures import datalad_noninteractive_ui

from datalad_tabby.tests.fixtures import (
    # provides the tabby "demorecord" that is shipped with the sources
    tabby_tsv_record,
    # elementary tabby record comprising the key TSV buildiung blocks
    tabby_record_basic_components,
    # no-LD elementary record with overrides
    tabby_record_w_overrides,
)
