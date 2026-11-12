"""AD-2 — registry đóng tám phép (SPEC-REG-03)."""

import ast
import dataclasses
import importlib.util
import subprocess
import sys
from pathlib import Path

from haido_core.domain.registry import (
    CellQuery,
    Classification,
    Classify,
    GroupSkills,
    MapMentions,
    MatchPostings,
    Mention,
    OneOrMany,
    OrderPath,
    PathRequest,
    PercentileRequest,
    Percentiles,
    Population,
    PopulationRequest,
    PostingFacts,
    SelectCell,
    SkillGroupRequest,
    as_batch,
)

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PY = ROOT / "haido_core" / "domain" / "registry.py"
REGISTRY_MD = ROOT / "haido_core" / "domain" / "REGISTRY.md"

PHEP = (
    (MapMentions, "map_mentions", "mapping.py"),
    (SelectCell, "select_cell", "cells.py"),
    (Population, "population", "population.py"),
    (GroupSkills, "group_skills", "skill_groups.py"),
    (Percentiles, "percentiles", "percentiles.py"),
    (Classify, "classify", "classify.py"),
    (MatchPostings, "match_postings", "matching.py"),
    (OrderPath, "order_path", "path_order.py"),
)


def _cong():
    spec = importlib.util.spec_from_file_location(
        "check_gates", ROOT / "tools" / "gates" / "check_gates.py"
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _cay_hop_le(tmp: Path) -> None:
    dest = tmp / "haido_core" / "domain"
    dest.mkdir(parents=True)
    for name in ("REGISTRY.md", "registry.py"):
        (dest / name).write_text((ROOT / "haido_core" / "domain" / name).read_text(encoding="utf-8"), encoding="utf-8")


def test_ad2_registry_md_du_tam_phep() -> None:
    text = REGISTRY_MD.read_text(encoding="utf-8")
    for _, name, install in PHEP:
        assert name in text
        assert install in text
    for phrase in ("mapping", "chọn ô", "dân số", "nhóm kỹ năng", "phân vị", "phân loại", "so khớp", "xếp thứ tự"):
        assert phrase in text


def test_ad2_moi_protocol_dung_mot_method() -> None:
    for cls, name, _install in PHEP:
        defs = [key for key in cls.__dict__ if key == name]
        assert defs == [name]
    tree = ast.parse(REGISTRY_PY.read_text(encoding="utf-8"))
    names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    op_names = {name for _cls, name, _install in PHEP}
    batch_variants = {name for name in names if name.endswith("_batch")}
    assert not any(name.removesuffix("_batch") in op_names for name in batch_variants)


def test_ad2_than_ham_chi_la_dau_ba_cham() -> None:
    tree = ast.parse(REGISTRY_PY.read_text(encoding="utf-8"))
    names = {name for _cls, name, _install in PHEP}
    found = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name not in names:
            continue
        body = node.body
        if isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
            body = body[1:]
        assert len(body) == 1
        assert isinstance(body[0], ast.Expr)
        assert body[0].value.value is ...
        found += 1
    assert found == len(PHEP)


def test_ad2_khong_mac_dinh_nguong_va_khong_doi_pham_vi() -> None:
    expected = {
        CellQuery: {"requested", "min_sample"},
        PopulationRequest: {"cell", "window_days"},
        SkillGroupRequest: {"rates", "theta_core", "theta_common"},
        PercentileRequest: {"values", "percentile", "seed", "draws"},
        PathRequest: {"gaps", "edges", "skills"},
    }
    for cls, names in expected.items():
        fields = dataclasses.fields(cls)
        assert {item.name for item in fields} == names
        for item in fields:
            assert item.default is dataclasses.MISSING


def test_ad2_khong_nhan_van_ban_day_du_va_khong_import_framework() -> None:
    source = REGISTRY_PY.read_text(encoding="utf-8")
    for banned in ("sqlalchemy", "dagster", "fastapi", "jd_text", "cv_text"):
        assert banned not in source
    # #283: phép 6 được nhận văn bản JD (chỉ trong bộ nhớ), mã kỹ năng và số năm; REGISTRY.md đổi cùng lúc.
    assert {item.name for item in dataclasses.fields(PostingFacts)} == {
        "title",
        "source",
        "source_category",
        "seniority_text",
        "location_text",
        "text",
        "skills",
        "years_min",
        "address_text",  # #285: dòng địa chỉ của JD, chỉ trong bộ nhớ
    }
    registry_md = REGISTRY_MD.read_text(encoding="utf-8")
    assert "được nhận văn bản JD đầy đủ" in registry_md
    assert "không gọi mô hình" in registry_md
    assert {item.name for item in dataclasses.fields(Mention)} == {"text", "start", "end"}


def test_ad2_mot_doi_tuong_va_mot_lo() -> None:
    class PhanLoaiThu:
        def classify(self, postings: OneOrMany[PostingFacts]) -> OneOrMany[Classification]:
            batch = as_batch(postings)
            one = Classification("Backend", None, "Junior", "Hà Nội")
            if batch is None:
                return one
            return tuple(one for _item in batch)

    tin = PostingFacts("Backend", "topdev", None, "Junior", "Hà Nội")
    stub = PhanLoaiThu()
    assert isinstance(stub.classify(tin), Classification)
    assert stub.classify([tin, tin]) == (stub.classify(tin), stub.classify(tin))
    assert stub.classify(()) == ()


def test_ad2_str_khong_phai_lo() -> None:
    assert as_batch("Hà Nội") is None
    assert as_batch(()) == ()


def test_ad2_ci_bat_buoc_cong() -> None:
    text = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "--require AD-1 AD-17 AD-25 AD-2 AD-7" in text


def test_ad2_cong_pass_khi_chi_co_chu_ky(tmp_path: Path) -> None:
    gates = _cong()
    _cay_hop_le(tmp_path)
    status, _detail, hits = gates.ad2_status(tmp_path)
    assert status == gates.PASS
    assert hits == []


def test_ad2_cong_fail_khi_thieu_cum_tu(tmp_path: Path) -> None:
    gates = _cong()
    _cay_hop_le(tmp_path)
    md = tmp_path / "haido_core" / "domain" / "REGISTRY.md"
    md.write_text(md.read_text(encoding="utf-8").replace("dân số", "dan so"), encoding="utf-8")
    status, _detail, hits = gates.ad2_status(tmp_path)
    assert status == gates.FAIL
    assert any("dân số" in line for line in hits)


def test_ad2_cong_fail_khi_def_ngoai_domain(tmp_path: Path) -> None:
    gates = _cong()
    _cay_hop_le(tmp_path)
    folder = tmp_path / "haido_api"
    folder.mkdir()
    (folder / "extra.py").write_text("def classify(postings):\n    return postings\n", encoding="utf-8")
    status, _detail, hits = gates.ad2_status(tmp_path)
    assert status == gates.FAIL
    assert any("haido_api/extra.py" in line for line in hits)


def test_ad2_cong_fail_khi_hai_than_ham(tmp_path: Path) -> None:
    gates = _cong()
    _cay_hop_le(tmp_path)
    domain = tmp_path / "haido_core" / "domain"
    body = "class A:\n    def classify(self, postings):\n        return postings\n"
    (domain / "a.py").write_text(body, encoding="utf-8")
    (domain / "b.py").write_text(body.replace("class A", "class B"), encoding="utf-8")
    status, _detail, hits = gates.ad2_status(tmp_path)
    assert status == gates.FAIL
    assert any("hơn một thân hàm" in line for line in hits)


def test_ad2_cong_fail_khi_file_khong_parse(tmp_path: Path) -> None:
    gates = _cong()
    _cay_hop_le(tmp_path)
    folder = tmp_path / "haido_api"
    folder.mkdir()
    (folder / "broken.py").write_text("def (\n", encoding="utf-8")
    status, _detail, hits = gates.ad2_status(tmp_path)
    assert status == gates.FAIL
    assert any("broken.py" in line for line in hits)


def test_ad2_cong_tren_repo_that() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "gates" / "check_gates.py"), "--require", "AD-1", "AD-17", "AD-25", "AD-2", "AD-7"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "AD-2" in proc.stdout
