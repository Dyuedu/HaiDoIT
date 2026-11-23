"""#278 — `tools/vocab/skill_gaps.py`: bảng kỹ năng thô chưa có mã và tỷ lệ lượt nhắc có mã theo vai trò (hàm thuần).

Phần cần Postgres (`counted_postings`, `collect`, chỉ-đọc) nằm ở `tests/steps/test_gh278_skill_gaps_db.py`.
"""

import json
from pathlib import Path

import pytest

from haido_core.vocab.skills import Vocabulary, load_exclusions, load_vocabulary
from tools.vocab import skill_gaps
from tools.vocab.skill_gaps import Posting, remap, summarize

SPEC = Path(__file__).resolve().parents[2] / "specs" / "278-ma-ky-nang-thuong-gap"
GAPS_FILE = SPEC / "gaps-2026-11-20.json"

VOCAB = Vocabulary(
    version="seed-test",
    lookup={"python": "python", "co so du lieu": "databases", "database": "databases", "agile": "agile", "scrum": "scrum"},
    scan_terms=("python",),
    composites={"agile/scrum": ("agile", "scrum")},
)


def _by_key(result: dict) -> dict:
    return {s["key"]: s for s in result["skills"]}


def test_gh278_summarize_gop_cach_viet_cung_dang_bo_dau_thanh_mot_khoa() -> None:
    posting = Posting("topcv", "Backend", ("Cơ sở dữ liệu", "Database"))
    other = Posting("itviec", "Backend", ("cơ sở dữ liệu",))
    skills = _by_key(summarize([posting, other], VOCAB))
    row = skills["co so du lieu"]
    assert row["postings"] == 2
    assert row["code"] == "databases"
    assert row["spellings"] == [("Cơ sở dữ liệu", 1), ("cơ sở dữ liệu", 1)]
    assert row["sources"] == ["itviec", "topcv"]
    assert skills["database"]["postings"] == 1


def test_gh278_summarize_moi_tin_chi_dem_mot_lan_cho_mot_khoa() -> None:
    result = summarize([Posting("topcv", "Backend", ("Python", "python ", "PYTHON", "Go"))], VOCAB)
    skills = _by_key(result)
    assert skills["python"]["postings"] == 1
    assert result["roles"]["Backend"] == {"postings": 1, "mentions": 2, "mapped": 1, "share": 0.5}


def test_gh278_summarize_the_ghep_tinh_la_co_ma() -> None:
    result = summarize([Posting("topcv", "Backend", ("Agile/Scrum", "Zzz"))], VOCAB)
    assert _by_key(result)["agile/scrum"]["code"] == "agile+scrum"
    assert _by_key(result)["zzz"]["code"] is None
    assert result["roles"]["Backend"]["mapped"] == 1
    assert result["roles"]["Backend"]["share"] == 0.5


def test_gh278_summarize_ty_le_theo_vai_tro_va_vai_tro_khong_co_luot_nhac() -> None:
    postings = [
        Posting("topcv", "Backend", ("Python", "Database", "Foo", "Bar")),
        Posting("topcv", "Backend", ("Python",)),
        Posting("itviec", "DevOps", ("Foo",)),
        Posting("itviec", "Embedded", ()),
    ]
    roles = summarize(postings, VOCAB)["roles"]
    assert roles["Backend"] == {"postings": 2, "mentions": 5, "mapped": 3, "share": 0.6}
    assert roles["DevOps"] == {"postings": 1, "mentions": 1, "mapped": 0, "share": 0.0}
    assert roles["Embedded"] == {"postings": 1, "mentions": 0, "mapped": 0, "share": None}


def test_gh278_summarize_xep_so_tin_giam_dan_roi_theo_khoa() -> None:
    postings = [Posting("a", "R", ("b", "c")), Posting("a", "R", ("c", "a"))]
    assert [s["key"] for s in summarize(postings, VOCAB)["skills"]] == ["c", "a", "b"]


def test_gh278_remap_tinh_lai_o_muc_khoa_voi_tu_vung_moi() -> None:
    gaps = {
        "meta": {"vocab_version": "seed-cu"},
        "roles_before": {"Backend": {"postings": 1, "mentions": 4, "mapped": 1, "share": 0.25}},
        "skills": [
            {"key": "python", "postings": 50, "code_before": "python"},
            {"key": "co so du lieu", "postings": 30, "code_before": None},
            {"key": "agile/scrum", "postings": 20, "code_before": None},
            {"key": "ha noi", "postings": 100, "code_before": None},
            {"key": "la hoac", "postings": 20, "code_before": None},
        ],
    }
    report = remap(gaps, VOCAB, frozenset({"ha noi"}))
    assert report["keys"] == 5
    assert (report["keys_mapped_before"], report["keys_mapped_after"]) == (1, 3)
    assert report["keys_excluded"] == 1
    assert report["keys_unresolved"] == ["la hoac"]
    assert report["tag_mentions"] == 220
    assert (report["tag_mentions_mapped_before"], report["tag_mentions_mapped_after"]) == (50, 100)
    assert report["tag_mention_share_after"] == pytest.approx(100 / 220)
    assert (report["vocab_version_before"], report["vocab_version_after"]) == ("seed-cu", "seed-test")
    assert report["roles_before"] == gaps["roles_before"]


def test_gh278_ac3_so_lieu_sau_cua_snapshot_2026_11_20_khong_con_khoa_bo_sot() -> None:
    gaps = json.loads(GAPS_FILE.read_text(encoding="utf-8"))
    report = remap(gaps, load_vocabulary(), load_exclusions().keys)
    assert report["vocab_version_before"] == "seed-2026-11-13"
    assert report["vocab_version_after"] != "seed-2026-11-13"
    assert report["keys"] == 673
    assert (report["keys_mapped_before"], report["keys_mapped_after"]) == (369, 515)
    assert report["keys_excluded"] == 158
    assert report["keys_unresolved"] == []
    assert (report["tag_mentions_mapped_before"], report["tag_mentions_mapped_after"]) == (26750, 32802)
    assert report["tag_mentions"] == 47444
    # Bảng "trước" theo vai trò lấy từ lần chạy trên prod (chưa có "sau": cần chạy lại script trên prod).
    assert len(report["roles_before"]) >= 10
    assert report["roles_before"]["Backend"]["share"] == pytest.approx(0.4406, abs=1e-4)


def test_gh278_cli_after_in_bao_cao_ngoai_tuyen(capsys: pytest.CaptureFixture[str]) -> None:
    assert skill_gaps.main(["--after", str(GAPS_FILE)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["keys_unresolved"] == []
    assert report["keys_mapped_after"] == 515


# --- review 2026-11-23: remap đọc đúng đầu ra của chính script -----------------------------------------------------


def test_gh278_remap_nhan_dau_ra_cua_summarize_khong_can_doi_ten_khoa() -> None:
    postings = [
        Posting("topcv", "Backend", ("Python", "Database", "Foo")),
        Posting("itviec", "Backend", ("Python", "Agile/Scrum")),
    ]
    raw = json.loads(json.dumps(summarize(postings, VOCAB)))  # đúng dạng script in ra: khóa `code`, `roles`
    report = remap(raw, VOCAB, frozenset(), min_postings=1)
    assert report["keys"] == 4
    assert report["keys_mapped_before"] == 3
    assert report["tag_mentions_mapped_before"] == 4
    assert report["tag_mention_share_before"] == pytest.approx(4 / 5)
    assert report["roles_before"]["Backend"]["mentions"] == 5


def test_gh278_remap_van_nhan_khoa_code_before_va_roles_before_cua_file_da_loc() -> None:
    gaps = {
        "roles_before": {"X": {"postings": 1}},
        "skills": [{"key": "python", "postings": 30, "code_before": "python"}],
    }
    report = remap(gaps, VOCAB, frozenset())
    assert report["keys_mapped_before"] == 1
    assert report["roles_before"] == {"X": {"postings": 1}}


def test_gh278_remap_loc_khoa_duoi_min_postings_mac_dinh_20() -> None:
    gaps = {
        "skills": [
            {"key": "python", "postings": 20, "code": "python"},
            {"key": "zzz", "postings": 19, "code": None},
        ]
    }
    assert remap(gaps, VOCAB, frozenset())["keys"] == 1
    assert remap(gaps, VOCAB, frozenset())["keys_unresolved"] == []
    assert remap(gaps, VOCAB, frozenset(), min_postings=1)["keys_unresolved"] == ["zzz"]


def test_gh278_cli_after_nhan_tuy_chon_min_postings(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    raw = {"skills": [{"key": "python", "postings": 3, "code": "python"}], "roles": {}}
    path = tmp_path / "raw.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    assert skill_gaps.main(["--after", str(path)]) == 0
    assert json.loads(capsys.readouterr().out)["keys"] == 0
    assert skill_gaps.main(["--after", str(path), "--min-postings", "1"]) == 0
    assert json.loads(capsys.readouterr().out)["keys"] == 1


def test_gh278_strings_chuoi_khong_phai_json_tach_theo_dau_phay() -> None:
    assert skill_gaps._strings("Python, Java ,, Go") == ["Python", "Java", "Go"]
    assert skill_gaps._strings('["Python", " Go "]') == ["Python", "Go"]
    assert skill_gaps._strings(None) == []
    assert skill_gaps._strings("") == []
