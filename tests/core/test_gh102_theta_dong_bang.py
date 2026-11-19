"""#102 (DAT.30) — θ_core và θ_common có phiên bản, đóng băng trong `config/theta.toml`.

AC1: θ có phiên bản và không đổi lặng lẽ giữa các snapshot sau khi đóng băng.
AC2: giá trị đã đóng băng được ghi ở chỗ cả nhóm đọc được (`config/theta.toml`, `docs/data/theta.md`).

`PINNED` là bản ghi cứng mọi phiên bản đã đóng băng. Sửa giá trị một phiên bản cũ thì test đỏ; thêm phiên bản mới thì
phải thêm vào `PINNED` ở cùng commit, nên mọi thay đổi θ đều hiện trong diff của test này.
"""

import re
import tomllib
from pathlib import Path

import pytest

from haido_core.config import (
    DEFAULT_THETA_PATH,
    PRE_FREEZE_THETA_VERSION,
    ConfigError,
    ThetaVersion,
    load_rules,
    load_theta_versions,
)

ROOT = Path(__file__).resolve().parents[2]
RULES_TEXT = (ROOT / "config" / "rules.toml").read_text(encoding="utf-8")

PINNED: dict[str, tuple[float, float]] = {
    "theta-1": (0.3, 0.1),
}
"""Phiên bản đã đóng băng -> (θ_core, θ_common). Chỉ thêm dòng mới, không sửa dòng cũ."""

VERSION = (
    '[[versions]]\nid = "{id}"\ntheta_core = {core}\ntheta_common = {common}\n'
    'calibrated_on = "{on}"\nnote = "thử"\n{extra}'
)


def _entry(
    id: str = "theta-1", core: str = "0.3", common: str = "0.1", on: str = "2026-11-19", extra: str = ""
) -> str:
    return VERSION.format(id=id, core=core, common=common, on=on, extra=extra)


def _registry(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "theta.toml"
    path.write_text(body, encoding="utf-8")
    return path


def _rules(tmp_path: Path, version: str = "theta-1") -> Path:
    path = tmp_path / "rules.toml"
    body = re.sub(r'^theta_version = ".*"$', f'theta_version = "{version}"', RULES_TEXT, flags=re.MULTILINE)
    path.write_text(body, encoding="utf-8")
    return path


# ---------------------------------------------------------------- bản ghi cứng


def test_gh102_ac1_moi_phien_ban_da_dong_bang_co_trong_so_dang_ky_dung_gia_tri() -> None:
    registry = {v.id: (v.theta_core, v.theta_common) for v in load_rules().theta_versions}
    for version, values in PINNED.items():
        assert registry.get(version) == values, f"{version} đã đóng băng, không được sửa hay xóa; thêm phiên bản mới."


def test_gh102_ac1_so_dang_ky_khong_co_phien_ban_nao_ngoai_ban_ghi_cung() -> None:
    ids = [v.id for v in load_rules().theta_versions]
    assert ids == list(PINNED), "Thêm phiên bản θ mới thì thêm nó vào PINNED (theo thứ tự) trong cùng commit."


def test_gh102_ac1_phien_ban_dau_la_phien_ban_cua_snapshot_chua_ghi_phien_ban() -> None:
    assert load_rules().theta_versions[0].id == PRE_FREEZE_THETA_VERSION
    assert next(iter(PINNED)) == PRE_FREEZE_THETA_VERSION


def test_gh102_ac1_phien_ban_hien_hanh_nam_trong_ban_ghi_cung_va_dung_gia_tri() -> None:
    rules = load_rules()
    assert rules.theta_version in PINNED
    assert (rules.theta_core, rules.theta_common) == PINNED[rules.theta_version]


def test_gh102_ac1_rules_toml_chi_chon_phien_ban_khong_ghi_so_theta() -> None:
    raw = tomllib.loads(RULES_TEXT)
    assert raw["theta_version"] == load_rules().theta_version
    assert "theta_core" not in raw and "theta_common" not in raw


# ---------------------------------------------------------------- bộ đọc


def test_gh102_so_dang_ky_duoc_doc_va_theta_cua_tung_phien_ban() -> None:
    rules = load_rules()
    assert isinstance(rules.theta_versions[0], ThetaVersion)
    first = rules.theta_versions[0]
    assert (first.id, first.calibrated_on, bool(first.note)) == (PRE_FREEZE_THETA_VERSION, "2026-11-19", True)
    assert rules.theta(PRE_FREEZE_THETA_VERSION) == first
    current = rules.theta(rules.theta_version)
    assert (current.theta_core, current.theta_common) == (rules.theta_core, rules.theta_common)


def test_gh102_theta_cua_phien_ban_la_la_loi() -> None:
    with pytest.raises(KeyError):
        load_rules().theta("theta-khong-co")


def test_gh102_phien_ban_hien_hanh_la_phien_ban_dat_trong_rules_toml(tmp_path: Path) -> None:
    registry = _registry(tmp_path, _entry() + _entry("theta-2", "0.35", "0.12"))
    rules = load_rules(_rules(tmp_path, "theta-2"), theta_path=registry)
    assert rules.theta_version == "theta-2"
    assert (rules.theta_core, rules.theta_common) == (0.35, 0.12)
    assert [v.id for v in rules.theta_versions] == ["theta-1", "theta-2"]
    assert rules.theta("theta-1").theta_core == 0.3  # phiên bản cũ vẫn đọc được


def test_gh102_thieu_file_so_dang_ky_la_config_error(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="theta.toml"):
        load_rules(theta_path=tmp_path / "theta.toml")


def test_gh102_trung_id_la_config_error(tmp_path: Path) -> None:
    registry = _registry(tmp_path, _entry() + _entry(core="0.4"))
    with pytest.raises(ConfigError, match="trùng"):
        load_rules(theta_path=registry)


def test_gh102_phien_ban_hien_hanh_khong_co_trong_so_dang_ky_la_config_error(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="theta-9"):
        load_rules(_rules(tmp_path, "theta-9"))


@pytest.mark.parametrize(
    ("core", "common"),
    [
        ("1.5", "0.1"),
        ("-0.1", "0.1"),
        ('"x"', "0.1"),
        ("0.3", '"x"'),
        ("0.3", "2"),
        ("0.3", "-0.1"),  # dưới cận dưới của theta_common
        ("0", "-0.0001"),  # sát cận dưới
        ("-0.0001", "0"),  # sát cận dưới của theta_core
        ("1.0001", "0.1"),  # sát cận trên
    ],
)
def test_gh102_gia_tri_ngoai_khoang_la_config_error(tmp_path: Path, core: str, common: str) -> None:
    with pytest.raises(ConfigError, match="từ 0 đến 1"):
        load_rules(theta_path=_registry(tmp_path, _entry(core=core, common=common)))


def test_gh102_common_lon_hon_core_la_config_error(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="không được lớn hơn"):
        load_rules(theta_path=_registry(tmp_path, _entry(core="0.3", common="0.5")))


@pytest.mark.parametrize(("core", "common"), [("1", "0"), ("0.2", "0.2"), ("0", "0"), ("1", "1")])
def test_gh102_so_nguyen_va_core_bang_common_duoc_chap_nhan(tmp_path: Path, core: str, common: str) -> None:
    [first] = load_theta_versions(_registry(tmp_path, _entry(core=core, common=common)))
    assert (first.theta_core, first.theta_common) == (float(core), float(common))
    assert isinstance(first.theta_core, float) and isinstance(first.theta_common, float)


@pytest.mark.parametrize("bad", [" theta-1", "theta-1 ", "\\ttheta-1"])
def test_gh102_id_co_khoang_trang_hai_dau_bi_tu_choi_khong_bi_cat(tmp_path: Path, bad: str) -> None:
    body = _entry().replace('id = "theta-1"', f'id = "{bad}"')
    with pytest.raises(ConfigError, match="khoảng trắng"):
        load_theta_versions(_registry(tmp_path, body))


@pytest.mark.parametrize(
    "on", ["2026-13-45", "19/11/2026", "2026-1-5", "20261119", "2026-11-19T00:00", "hôm qua", " 2026-11-19", "2026-02-30"]
)
def test_gh102_calibrated_on_phai_la_ngay_iso(tmp_path: Path, on: str) -> None:
    with pytest.raises(ConfigError, match="YYYY-MM-DD"):
        load_theta_versions(_registry(tmp_path, _entry(on=on)))


def test_gh102_khoa_la_trong_mot_phien_ban_bi_tu_choi(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="theta_cor"):
        load_theta_versions(_registry(tmp_path, _entry(extra="theta_cor = 0.4\n")))


def test_gh102_khoa_la_o_cap_cao_nhat_cua_theta_toml_bi_tu_choi(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="khóa lạ"):
        load_theta_versions(_registry(tmp_path, "theta_core = 0.3\n" + _entry()))


def test_gh102_phien_ban_dau_khong_phai_theta_1_la_config_error(tmp_path: Path) -> None:
    registry = _registry(tmp_path, _entry("theta-2", "0.35", "0.12") + _entry())
    with pytest.raises(ConfigError, match="đầu tiên"):
        load_theta_versions(registry)
    with pytest.raises(ConfigError, match="đầu tiên"):
        load_rules(_rules(tmp_path, "theta-1"), theta_path=registry)


def test_gh102_so_dang_ky_thieu_theta_1_la_config_error(tmp_path: Path) -> None:
    registry = _registry(tmp_path, _entry("theta-2", "0.35", "0.12"))
    with pytest.raises(ConfigError, match="theta-1"):
        load_theta_versions(registry)
    with pytest.raises(ConfigError, match="theta-1"):
        load_rules(_rules(tmp_path, "theta-2"), theta_path=registry)


@pytest.mark.parametrize("legacy", ["theta_core = 0.3\n", "theta_common = 0.1\n"])
def test_gh102_rules_toml_con_khoa_theta_cu_la_config_error(tmp_path: Path, legacy: str) -> None:
    path = tmp_path / "rules.toml"
    path.write_text(legacy + RULES_TEXT, encoding="utf-8")
    with pytest.raises(ConfigError, match="config/theta.toml") as exc:
        load_rules(path)
    assert "theta_version" in str(exc.value)


@pytest.mark.parametrize("body", ["", "versions = []\n", 'versions = "x"\n'])
def test_gh102_so_dang_ky_rong_hoac_sai_dang_la_config_error(tmp_path: Path, body: str) -> None:
    with pytest.raises(ConfigError, match="versions"):
        load_rules(theta_path=_registry(tmp_path, body))


@pytest.mark.parametrize("drop", ["id", "theta_core", "theta_common", "calibrated_on", "note"])
def test_gh102_thieu_khoa_trong_mot_phien_ban_la_config_error(tmp_path: Path, drop: str) -> None:
    body = re.sub(rf"^{drop} = .*\n", "", _entry(), flags=re.MULTILINE)
    with pytest.raises(ConfigError, match=drop):
        load_rules(theta_path=_registry(tmp_path, body))


def test_gh102_id_rong_la_config_error(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="id"):
        load_rules(theta_path=_registry(tmp_path, _entry(id="")))


def test_gh102_rules_toml_thieu_theta_version_la_config_error(tmp_path: Path) -> None:
    path = tmp_path / "rules.toml"
    path.write_text(re.sub(r'^theta_version = ".*"\r?\n', "", RULES_TEXT, flags=re.MULTILINE), encoding="utf-8")
    with pytest.raises(ConfigError, match="theta_version"):
        load_rules(path)


def test_gh102_duong_dan_mac_dinh_la_config_theta_toml() -> None:
    assert DEFAULT_THETA_PATH == ROOT / "config" / "theta.toml"


# ---------------------------------------------------------------- AC2: tài liệu đủ phiên bản


THETA_DOC = (ROOT / "docs" / "data" / "theta.md").read_text(encoding="utf-8")


def _current_table_rows() -> dict[str, list[str]]:
    section = THETA_DOC.split("## Phiên bản hiện hành", 1)[1].split("\n## ", 1)[0]
    rows: dict[str, list[str]] = {}
    for line in section.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and cells[0].startswith("`") and cells[0].endswith("`"):
            rows[cells[0].strip("`")] = cells[1:]
    return rows


def test_gh102_ac2_moi_phien_ban_da_ghim_co_mat_trong_docs_data_theta_md() -> None:
    for version in PINNED:
        assert f"`{version}`" in THETA_DOC, f"docs/data/theta.md thiếu phiên bản {version}."


def test_gh102_ac2_bang_phien_ban_hien_hanh_co_dong_cho_moi_phien_ban_va_danh_dau_rules_theta_version() -> None:
    rows = _current_table_rows()
    assert list(rows) == list(PINNED)
    current = load_rules().theta_version
    marked = [version for version, cells in rows.items() if cells[-1] == "có"]
    assert marked == [current], "Cột Hiện hành phải đánh dấu đúng rules.theta_version."
    for version, cells in rows.items():
        values = PINNED[version]
        assert cells[0].replace(",", ".") == f"{values[0]:g}"
        assert cells[1].replace(",", ".") == f"{values[1]:g}"
