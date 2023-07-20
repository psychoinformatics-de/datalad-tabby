"""datalad-metalad metadata extractor"""

from typing import (
    Any,
    Dict,
)
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


def yield_dscollection_records(ds: Dataset):
    dscolpath = ds.pathobj / '.datalad' / 'tabby' / 'dscollection'
    if not dscolpath.exists():
        return
    for rpath in dscolpath.glob('*_dataset.tsv'):
        try:
            yield load_tabby(
                rpath,
                single=True,
                jsonld=True,
                recursive=True,
            )
        except Exception:
            # TODO log
            pass


# key terms, we use ful URLs to avoid having to fiddle with context
# prefixes and possibly conflicting definitions
isVersionOf = 'https://purl.org/dc/terms/isVersionOf'
hasVersion = 'https://purl.org/dc/terms/hasVersion'

# id resolver endpoints
# TODO under discussion https://github.com/datalad/datalad-registry/issues/217
dx_dataset = 'https://dx.datalad.org/dataset/'
dx_dataset_version = 'https://dx.datalad.org/dataset-version/'


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
        rootdsmeta = {}
        extraction_success = False
        try:
            rootdsmeta = load_dataset_self_description(self.dataset)
            extraction_success = True
            res = get_status_dict(status='ok')
        except LookupError:
            res = get_status_dict(status='impossible')
            # TODO https://github.com/datalad/datalad-metalad/issues/385
        except Exception as e:
            return ExtractorResult(
                extractor_version=self.get_version(),
                extraction_parameter=self.parameter or {},
                extraction_success=extraction_success,
                datalad_result_dict=get_status_dict(
                    status='error',
                    exception=CapturedException(e),
                    type='dataset',
                ),
                immediate_data={},
            )

        self._amend_tabby(rootdsmeta)
        res['type'] = 'dataset'

        dsmeta = []
        if rootdsmeta:
            dsmeta.append(rootdsmeta)

        for crec in yield_dscollection_records(self.dataset):
            # good enough if we get something here, even when there was
            # no root record
            res['status'] = 'ok'
            extraction_success = True
            if not crec:
                # no point in reporting empty records
                continue
            dsmeta.append(crec)

        if len(dsmeta) > 1:
            dsmeta = {
                # https://github.com/datalad/datalad-metalad/issues/391
                '@graph': dsmeta,
            }
        else:
            # compact, we only have a single (root) record
            dsmeta = dsmeta[0]

        return ExtractorResult(
            extractor_version=self.get_version(),
            extraction_parameter=self.parameter or {},
            extraction_success=extraction_success,
            datalad_result_dict=res,
            immediate_data=dsmeta,
        )

    def _amend_tabby(self, meta):
        # we override the top-level '@id' to force the report into the
        # corset of the datalad ID concept.
        # this report is a "version-level description" in the
        # W3C HCLS recommendation
        # TODO log if exists
        # TODO if there is no concept ID
        meta['@id'] = self.ds_version_id

        # establish an isVersionOf linkage to the dataset concept-ID
        # via which any version of this dataset can be located in a
        # knowledge graph
        summary_lvl = self._get_ds_summary_lvl_desc()
        if summary_lvl:
            _add2meta(meta, isVersionOf, summary_lvl)

        # It is tricky to mess with @type here
        # - without JSON-LD processing it is hard to figure out if any
        #   @type is already declared
        # - without knowing that there is no type, we cannot "enforce"
        #   one, because we do not know which class the report belongs
        #   too
        # However, we specially process the dataset's self-description
        # here, we can document this behavior
        # TODO ^^^
        if '@type' not in meta:
            meta['@type'] = 'https://schema.org/Dataset'

    # TODO migrate to metalad base class
    @property
    def ds_concept_id(self):
        dsid = self.dataset.id
        # ATM metalad does not run on repos without a datalad dataset ID
        assert dsid
        # https://github.com/datalad/datalad-registry/issues/217
        return f'{dx_dataset}{self.dataset.id}'

    # TODO migrate to metalad base class
    @property
    def ds_version_id(self):
        # https://github.com/datalad/datalad-registry/issues/217
        return f'{dx_dataset_version}{self.ref_commit}'

    def _get_ds_summary_lvl_desc(self):
        return {
            '@id': self.ds_concept_id,
            hasVersion: self.ds_version_id,
        }


def _add2meta(meta: Dict, key: str, value: Any) -> None:
    vals = meta.get(key, [])
    if not isinstance(vals, list):
        vals = [vals]
    vals.append(value)
    if len(vals) == 1:
        vals = vals[0]
    meta[key] = vals
