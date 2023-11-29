from unittest.mock import patch

import pytest

from maas_engine.engine.base import EngineSession

import maas_cds.model as model


from maas_cds.engines.reports.dd_product import DDProductConsolidatorEngine
from maas_cds.engines.reports import PublicationConsolidatorEngine

from maas_cds.model.datatake import CdsDatatake


@patch("maas_cds.model.CdsDatatake.mget_by_ids")
def test_dd_das_product_consolidation(mock_get_by_id, s1_ddas_product_1, dd_attrs):
    datatake_doc = CdsDatatake()

    datatake_doc.datatake_id = "326097"
    datatake_doc.absolute_orbit = "41805"
    datatake_doc.instrument_mode = "IW"
    datatake_doc.timeliness = "NTC"

    mock_get_by_id.return_value = [datatake_doc]

    engine = DDProductConsolidatorEngine(dd_attrs=dd_attrs)
    engine.session = EngineSession()

    product = engine.consolidate_from_DasProduct(s1_ddas_product_1, model.CdsProduct())

    engine.consolidated_documents = [product]
    engine.on_post_consolidate()

    product.full_clean()

    assert product.to_dict() == {
        "absolute_orbit": "41805",
        "datatake_id": "326097",
        "dddas_publication_date": "2022-02-07T12:33:02.606Z",
        "instrument_mode": "IW",
        "key": "5e394d48c5b3eb8dacfa93bbf1ef6dc5",
        "mission": "S1",
        "dddas_name": "S1A_IW_OCN__2SDH_20220207T093448_20220207T093513_041805_04F9D1_820F",
        "polarization": "DH",
        "product_level": "L2_",
        "product_class": "S",
        "product_type": "IW_OCN__2S",
        "satellite_unit": "S1A",
        "sensing_start_date": "2022-02-07T08:34:48.170Z",
        "sensing_end_date": "2022-02-07T08:35:13.169Z",
        "sensing_duration": 24999000.0,
        "timeliness": "NTC",
        "content_length": 6808830,
    }


@patch("maas_cds.model.CdsDatatake.mget_by_ids")
def test_dd_das_publication_consolidation(mock_get_by_id, s1_ddas_product_1):
    datatake_doc = CdsDatatake()

    datatake_doc.datatake_id = "326097"
    datatake_doc.absolute_orbit = "41805"
    datatake_doc.instrument_mode = "IW"
    datatake_doc.timeliness = "NTC"

    mock_get_by_id.return_value = [datatake_doc]

    engine = PublicationConsolidatorEngine()
    engine.session = EngineSession()

    publication = engine.consolidate_from_DasProduct(
        s1_ddas_product_1, model.CdsPublication()
    )

    engine.consolidated_documents = [publication]
    engine.on_post_consolidate()

    publication.full_clean()

    assert publication.to_dict() == {
        "absolute_orbit": "41805",
        "content_length": 6808830,
        "datatake_id": "326097",
        "from_sensing_timeliness": 14269437000.0,
        "instrument_mode": "IW",
        "key": "c43d34bf843b455cdb83505fb49714f2",
        "mission": "S1",
        "name": "S1A_IW_OCN__2SDH_20220207T093448_20220207T093513_041805_04F9D1_820F",
        "polarization": "DH",
        "product_uuid": "7fe19497-072c-4ff0-87a3-903ec8b87903",
        "product_level": "L2_",
        "product_class": "S",
        "product_type": "IW_OCN__2S",
        "publication_date": "2022-02-07T12:33:02.606Z",
        "satellite_unit": "S1A",
        "sensing_start_date": "2022-02-07T08:34:48.170Z",
        "sensing_end_date": "2022-02-07T08:35:13.169Z",
        "sensing_duration": 24999000.0,
        "service_id": "DAS",
        "service_type": "DD",
        "timeliness": "NTC",
    }


@patch("maas_cds.model.CdsDatatake.get_by_id", return_value=None)
def test_action(mock_get_by_id, s1_ddas_product_1, dd_attrs):
    engine = DDProductConsolidatorEngine(dd_attrs=dd_attrs)

    product = engine.consolidate_from_DasProduct(s1_ddas_product_1, model.CdsProduct())

    assert engine.get_report_action("created", product) == "new.cds-product-s1"


@patch("maas_cds.lib.queryutils.find_datatake_from_sensing.find_datatake_from_sensing")
@patch("maas_cds.model.CdsPublication.get_by_id", return_value=None)
def test_ddas_product_consolidation(
    mock_get_by_id, mock_find_datatake_from_sensing, s2_raw_product_l1c_container_das
):
    engine = PublicationConsolidatorEngine()
    # TODO
    product = engine.consolidate_from_DasProduct(
        s2_raw_product_l1c_container_das, model.CdsPublication()
    )

    assert product.product_level == "L1_"
