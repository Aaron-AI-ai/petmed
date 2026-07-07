"""시설(동물병원/동물약국/동물미용업) 정형 데이터 — SQLite 저장/조회.

위키(md, 비정형 지식)와 분리된 관심사. LOCALDATA 인허가 CSV를 임포트하고
조건 검색(WHERE)으로 조회한다. 표준 라이브러리 sqlite3만 사용.

CLI: mcp-wiki-import <csv...> [-o facilities.db]
"""

import argparse
import csv
import sqlite3
from pathlib import Path

_SCHEMA = """
CREATE TABLE IF NOT EXISTS facilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    facility_type TEXT NOT NULL,
    name TEXT NOT NULL,
    road_address TEXT,
    jibun_address TEXT,
    sido TEXT,
    sigungu TEXT,
    phone TEXT,
    state TEXT,
    licensed_at TEXT,
    closed_at TEXT,
    x REAL,
    y REAL
);
CREATE INDEX IF NOT EXISTS idx_fac_type ON facilities(facility_type);
CREATE INDEX IF NOT EXISTS idx_fac_region ON facilities(sido, sigungu);
CREATE INDEX IF NOT EXISTS idx_fac_state ON facilities(state);
"""

_TYPE_BY_FILENAME = {"병원": "동물병원", "약국": "동물약국", "미용": "동물미용업"}

ACTIVE_STATE = "영업/정상"


class FacilityStoreError(ValueError):
    pass


def _detect_type(path: Path) -> str:
    for token, ftype in _TYPE_BY_FILENAME.items():
        if token in path.name:
            return ftype
    raise FacilityStoreError(f"파일명에서 시설 유형을 판별할 수 없습니다: {path.name}")


def _read_csv(path: Path) -> list[dict]:
    for enc in ("utf-8-sig", "cp949"):
        try:
            with open(path, encoding=enc, newline="") as f:
                return list(csv.DictReader(f))
        except UnicodeDecodeError:
            continue
    raise FacilityStoreError(f"CSV 인코딩을 해석할 수 없습니다 (utf-8/cp949 시도): {path}")


def _split_region(address: str) -> tuple[str, str]:
    parts = address.split()
    sido = parts[0] if parts else ""
    sigungu = parts[1] if len(parts) > 1 else ""
    return sido, sigungu


def _to_float(value: str) -> float | None:
    try:
        return float(value.strip())
    except (ValueError, AttributeError):
        return None


def import_csvs(csv_paths: list[Path], db_path: Path) -> dict[str, int]:
    """LOCALDATA 인허가 CSV들을 SQLite로 임포트. 기존 데이터는 전체 교체."""
    counts: dict[str, int] = {}
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(_SCHEMA)
        conn.execute("DELETE FROM facilities")
        for path in csv_paths:
            ftype = _detect_type(path)
            rows = _read_csv(path)
            for r in rows:
                road = (r.get("도로명주소") or "").strip()
                jibun = (r.get("지번주소") or "").strip()
                sido, sigungu = _split_region(road or jibun)
                conn.execute(
                    "INSERT INTO facilities (facility_type, name, road_address, jibun_address,"
                    " sido, sigungu, phone, state, licensed_at, closed_at, x, y)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        ftype,
                        (r.get("사업장명") or "").strip(),
                        road,
                        jibun,
                        sido,
                        sigungu,
                        (r.get("전화번호") or "").strip(),
                        (r.get("영업상태명") or "").strip(),
                        (r.get("인허가일자") or "").strip(),
                        (r.get("폐업일자") or "").strip(),
                        _to_float(r.get("좌표정보(X)", "")),
                        _to_float(r.get("좌표정보(Y)", "")),
                    ),
                )
            counts[ftype] = counts.get(ftype, 0) + len(rows)
        conn.commit()
    finally:
        conn.close()
    return counts


class FacilityStore:
    def __init__(self, db_path: Path) -> None:
        if not db_path.is_file():
            raise FacilityStoreError(f"시설 DB 파일이 없습니다: {db_path}")
        self._db_path = db_path

    def find(
        self,
        facility_type: str | None = None,
        region: str | None = None,
        name: str | None = None,
        include_closed: bool = False,
        limit: int = 20,
    ) -> list[dict]:
        where, params = [], []
        if facility_type:
            where.append("facility_type LIKE ?")
            params.append(f"%{facility_type.strip()}%")
        if region:
            where.append("(sido LIKE ? OR sigungu LIKE ? OR road_address LIKE ? OR jibun_address LIKE ?)")
            params.extend([f"%{region.strip()}%"] * 4)
        if name:
            where.append("name LIKE ?")
            params.append(f"%{name.strip()}%")
        if not include_closed:
            where.append("state = ?")
            params.append(ACTIVE_STATE)
        sql = (
            "SELECT facility_type, name, road_address, jibun_address, sido, sigungu,"
            " phone, state, licensed_at, closed_at FROM facilities"
        )
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY sido, sigungu, name LIMIT ?"
        params.append(max(limit, 0))

        conn = sqlite3.connect(f"file:{self._db_path}?mode=ro", uri=True)
        try:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute(sql, params)]
        finally:
            conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="LOCALDATA 인허가 CSV → SQLite 임포트")
    parser.add_argument("csv_files", nargs="+", type=Path)
    parser.add_argument("-o", "--output", type=Path, default=Path("facilities.db"))
    args = parser.parse_args()
    counts = import_csvs(args.csv_files, args.output)
    for ftype, n in counts.items():
        print(f"{ftype}: {n}건")
    print(f"→ {args.output}")


if __name__ == "__main__":
    main()
