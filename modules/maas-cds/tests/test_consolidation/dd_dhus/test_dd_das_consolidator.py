import datetime
from unittest.mock import patch
from maas_model import MAASMessage

import pytest

from maas_engine.engine.base import EngineSession

import maas_cds.model as model


from maas_cds.engines.reports.dd_product import DDProductConsolidatorEngine
from maas_cds.engines.reports import PublicationConsolidatorEngine

from maas_cds.model.datatake import CdsDatatake

from maas_engine.engine.report import EngineReport


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
        "DD_DAS_id": "7fe19497-072c-4ff0-87a3-903ec8b87903",
        "DD_DAS_is_published": True,
        "DD_DAS_publication_date": datetime.datetime(
            2022, 2, 7, 12, 33, 2, 606000, tzinfo=datetime.timezone.utc
        ),
        "absolute_orbit": "41805",
        "datatake_id": "326097",
        "nb_dd_served": 1,
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


@pytest.mark.parametrize(
    "prod_name",
    [
        ("S2B_MSIL1C_20221108T090059_N0400_R007_T38WNV_20221108T092119.SAFE", True),
        ("S2B_MSIL1C_20221108T090059_N0400_R007_T38WNV_20221108T092119.zip", True),
        ("S5B_MSIL1C_20221108T090059_N0400_R007_T38WNV_20221108T092119.zip", False),
        ("S5D_MSIL1C_20221108T090059_N0400_R007_T38WNV_20221108T092119.zip", False),
        ("S5D_MSIL1C_240221108T090059_N0400_R007_T38WNV_20221108T092119.zip", False),
        ("S2B_MSIL1C_20221108T090059_N0400_R007_T38WNV_20221108T092119", True),
        ("S2B_MSIL1C_20221108T090059_N0400_R0007_T38WNV_20221108T092119.SAFE", False),
        ("S2B_MSIL1C_20221108T090059_N0400_R007_20221108T092119", True),
    ],
)
@patch(
    "maas_cds.engines.reports.dd_product.DDProductConsolidatorEngine.fill_common_attributes"
)
def test_dd_product_consolidation_container_reroute(
    mock,
    s2_raw_product_l1c_container_das,
    s2_creodias_product_1,
    s1_dd_product_1,
    prod_name,
):
    engine = DDProductConsolidatorEngine()

    for elements in [
        (s2_raw_product_l1c_container_das, "consolidate_from_DasProduct"),
        (s2_creodias_product_1, "consolidate_from_CreodiasProduct"),
        (s1_dd_product_1, "consolidate_from_DdProduct"),
    ]:
        engine.containers = []
        inp = elements[0]
        inp.product_name = prod_name[0]
        func = getattr(engine, elements[1])
        out = func(inp, model.CdsProduct())

        if prod_name[1]:
            assert out is None
            assert len(engine.containers) == 1
            assert engine.containers[0].product_name == prod_name[0]
        else:
            assert out is not None
            assert len(engine.containers) == 0


@pytest.mark.parametrize(
    "param",
    [
        (
            "S2B_MSIL1C_20221108T090059_N0400_R007_T38WNV_20221108T092119.SAFE",
            datetime.datetime(
                2022, 11, 8, 9, 0, 58, 000000, tzinfo=datetime.timezone.utc
            ),
            True,
        ),
        (
            "S2B_MSIL1C_20221108T090059_N0400_R007_T38WNV_20221108T092119.SAFE",
            datetime.datetime(
                2022, 11, 8, 10, 0, 0, 000000, tzinfo=datetime.timezone.utc
            ),
            False,
        ),
        (
            "S2B_MSIL1C_20221108T090059_N0400_R007_T38WNV_20221108T092119.SAFE",
            None,
            True,
        ),
    ],
)
def test_is_valid_container_function(s2_raw_product_l1c_container_das, param):
    """Check the is_valid_container function of DDProductConsolidatorEngine
    return expected value"""
    engine = DDProductConsolidatorEngine()

    inp = s2_raw_product_l1c_container_das
    inp.product_name = param[0]
    engine.min_doi = param[1]
    assert engine.is_valid_container(inp) == param[2]


def test_DDProductConsolidatorEngine_generate_reports_function(
    s2_raw_product_l1c_container_das,
):
    """Check that an engine report is triggered only when containers array is not empty"""
    engine = DDProductConsolidatorEngine()
    engine.output_rk = "outRK"
    engine.payload = MAASMessage(document_class="PAYLOADCLASS")

    # Case container
    inp = s2_raw_product_l1c_container_das
    inp.product_name = (
        "S2B_MSIL1C_20221108T090059_N0400_R007_T38WNV_20221108T092119.SAFE"
    )
    engine.consolidate_from_DasProduct(
        s2_raw_product_l1c_container_das, model.CdsProduct()
    )
    out = list(engine._generate_reports())
    assert len(out) == 1
    assert isinstance(out[0], EngineReport)

    # Case no container
    engine.containers = []
    # Product name written so that it is not detected as container
    inp.product_name = "S2B_MSIL1C_20221108T090059_N0400_R007_T38WNV_20221108T092119666"
    engine.consolidate_from_DasProduct(
        s2_raw_product_l1c_container_das, model.CdsProduct()
    )

    assert len(list(engine._generate_reports())) == 0
