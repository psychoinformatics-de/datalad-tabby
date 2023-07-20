"""datalad-metalad metadata extractor"""

from typing import Dict
import uuid

from datalad_metalad.extractors.base import (
    DatasetMetadataExtractor,
    DataOutputCategory,
    ExtractorResult,
)
from datalad_next.commands import get_status_dict
from datalad_next.datasets import Dataset
from datalad_next.exceptions import CapturedException

from datalad_tabby.io import load_tabby


def load_dataset_self_description(ds: Dataset) -> Dict:
    root_sheet = ds.pathobj / '.datalad' / 'tabby' / 'self' / 'dataset.tsv'
    if not root_sheet.exists():
        raise LookupError

    dsmeta = load_tabby(
        root_sheet,
        single=True,
        jsonld=True,
        recursive=True,
    )
    return dsmeta


class TabbyExtractor(DatasetMetadataExtractor):
    def get_id(self) -> uuid.UUID:
        """Return a fixed UUID that identifies this extractor"""
        return uuid.uuid5(
            uuid.NAMESPACE_URL,
            'https://datalad.org/metalad/extractors/tabby-dataset',
        )

    def get_version(self) -> str:
        """Returns an arbitrary version label"""
        return "0.0.1"

    def get_data_output_category(self) -> DataOutputCategory:
        """This extractor yields its result immediately and directly"""
        return DataOutputCategory.IMMEDIATE

    def get_required_content(self) -> bool:
        """TODO needs to `get()` `.datalad/tabby`"""
        return True

    def extract(self, _=None) -> ExtractorResult:
        dsmeta = {}
        extraction_success = False
        try:
            dsmeta = load_dataset_self_description(self.dataset)
            extraction_success = True
            res = get_status_dict(status='ok')
        except LookupError:
            res = get_status_dict(status='impossible')
            # TODO https://github.com/datalad/datalad-metalad/issues/385
        except Exception as e:
            res = get_status_dict(
                status='error',
                exception=CapturedException(e),
            )

        res['type'] = 'dataset'

        return ExtractorResult(
            extractor_version=self.get_version(),
            extraction_parameter=self.parameter or {},
            extraction_success=extraction_success,
            datalad_result_dict=res,
            immediate_data=dsmeta,
        )
