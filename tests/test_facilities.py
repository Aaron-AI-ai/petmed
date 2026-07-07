"""시설 데이터 임포트/조회 테스트."""

import pytest

from mcp_wiki.facilities import ACTIVE_STATE, FacilityStore, FacilityStoreError, import_csvs

HEADER = "사업장명,도로명주소,지번주소,전화번호,영업상태명,인허가일자,폐업일자,좌표정보(X),좌표정보(Y)"
ROWS = [
    "행복동물병원,서울특별시 강남구 테헤란로 1,서울특별시 강남구 역삼동 1,021234567,영업/정상,2010-01-01,,199000.1,451000.2",
    "옛날동물병원,서울특별시 강남구 봉은사로 2,,0212345678,폐업,1995-05-05,2020-12-31,,",
    "부산동물병원,부산광역시 해운대구 센텀로 3,,0511111111,영업/정상,2015-03-03,,,",
]


@pytest.fixture
def db(tmp_path):
    csv_path = tmp_path / "동물_동물병원.csv"
    csv_path.write_text("\n".join([HEADER, *ROWS]), encoding="utf-8-sig")
    db_path = tmp_path / "facilities.db"
    counts = import_csvs([csv_path], db_path)
    assert counts == {"동물병원": 3}
    return db_path


def test_active_only_by_default(db):
    results = FacilityStore(db).find(facility_type="병원")
    assert {r["name"] for r in results} == {"행복동물병원", "부산동물병원"}
    assert all(r["state"] == ACTIVE_STATE for r in results)


def test_include_closed(db):
    results = FacilityStore(db).find(include_closed=True)
    assert len(results) == 3


def test_region_filter(db):
    results = FacilityStore(db).find(region="강남구")
    assert [r["name"] for r in results] == ["행복동물병원"]
    assert results[0]["sido"] == "서울특별시"
    assert results[0]["sigungu"] == "강남구"


def test_name_filter_and_limit(db):
    assert FacilityStore(db).find(name="행복")[0]["name"] == "행복동물병원"
    assert len(FacilityStore(db).find(limit=1)) == 1


def test_cp949_and_reimport_replaces(db, tmp_path):
    csv2 = tmp_path / "동물_동물약국.csv"
    csv2.write_text(
        HEADER + "\n약손동물약국,대전광역시 서구 둔산로 9,,,영업/정상,2020-01-01,,,",
        encoding="cp949",
    )
    counts = import_csvs([csv2], db)  # 재임포트 = 전체 교체
    assert counts == {"동물약국": 1}
    results = FacilityStore(db).find(include_closed=True)
    assert [r["facility_type"] for r in results] == ["동물약국"]


def test_unknown_filename_type(tmp_path):
    bad = tmp_path / "기타.csv"
    bad.write_text(HEADER, encoding="utf-8")
    with pytest.raises(FacilityStoreError, match="유형"):
        import_csvs([bad], tmp_path / "x.db")


def test_missing_db_file(tmp_path):
    with pytest.raises(FacilityStoreError, match="DB 파일"):
        FacilityStore(tmp_path / "none.db")
