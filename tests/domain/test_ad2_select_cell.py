"""AD-2, AD-6, FR-19 — phép 2 `select_cell` (#106): chọn ô, thứ tự quay về và nhãn.

Thứ tự đã chốt (#106): `(vai trò, cấp)`, nếu cấp thô thuộc một nhóm thì `(vai trò, nhóm)`, rồi `(vai trò, all)`.
Phạm vi và vai trò không bao giờ đổi. Ô đạt khi cỡ mẫu >= `min_sample`.
"""

from collections.abc import Mapping

import pytest

from haido_core.domain.cells import CellSelector, CellStats
from haido_core.domain.registry import CellChoice, CellKey, CellQuery, SelectCell

SNAP = "2026-11-16"
GROUPS = {"entry": ("intern", "fresher", "junior")}
NAMES = {"backend": "Backend", "fresher": "Fresher", "entry": "Entry", "all": "mọi cấp", "mid": "Mid", "hanoi": "Hà Nội"}


def key(level: str | None, *, role: str = "backend", branch: str | None = "all", scope: str = "vn") -> CellKey:
    return CellKey(SNAP, role, branch, level, scope)


class Table:
    """Bảng ô giả; ghi lại mọi ô đã tra để kiểm phạm vi và vai trò."""

    def __init__(self, cells: Mapping[CellKey, CellStats]) -> None:
        self.cells = dict(cells)
        self.asked: list[CellKey] = []

    def __call__(self, cell: CellKey) -> CellStats | None:
        self.asked.append(cell)
        return self.cells.get(cell)


def selector(table: Table, *, noun: str = "tin") -> CellSelector:
    return CellSelector(table, level_groups=GROUPS, names=NAMES, sample_noun=noun)


def stats(n: int, mix: dict[str, int] | None = None, sample: int | None = None) -> CellStats:
    return CellStats(n=n, seniority_mix=mix or {}, sample_n=sample)


def ask(sel: CellSelector, level: str, *, min_sample: int = 30, **kw) -> CellChoice:
    choice = sel.select_cell(CellQuery(key(level, **kw), min_sample))
    assert isinstance(choice, CellChoice)
    return choice


def test_ad2_select_cell_khop_chu_ky_protocol() -> None:
    sel: SelectCell = selector(Table({}))  # kiểm kiểu tĩnh: gán được cho Protocol của registry
    assert callable(sel.select_cell)


def test_ad2_o_duoc_chon_du_mau_thi_khong_nhan_va_giu_nguyen_o() -> None:
    table = Table({key("fresher"): stats(40), key("entry"): stats(100), key("all"): stats(500)})
    choice = ask(selector(table), "fresher")
    assert choice.cell == key("fresher")
    assert choice.n == 40
    assert choice.label is None
    assert table.asked == [key("fresher")]  # đủ mẫu thì không tra ô rộng hơn


def test_ad2_dung_nguong_la_du_mau_duoi_nguong_mot_la_khong() -> None:
    table = Table({key("fresher"): stats(30), key("entry"): stats(80)})
    assert ask(selector(table), "fresher").cell == key("fresher")
    table = Table({key("fresher"): stats(29), key("entry"): stats(80)})
    assert ask(selector(table), "fresher").cell == key("entry")


def test_ad2_cap_tho_thuoc_nhom_quay_ve_nhom_truoc() -> None:
    table = Table({key("fresher"): stats(26), key("entry"): stats(52), key("all"): stats(500)})
    choice = ask(selector(table), "fresher")
    assert choice.cell == key("entry")
    assert choice.n == 52
    # nhãn gọi tên ô yêu cầu và n của nó, tên ô đã chọn và n của nó; chưa tới bước cuối nên không có câu về Mid trở lên
    assert choice.label == (
        "Backend · Fresher chỉ có 26 tin (dưới 30), chưa đủ để tính riêng, nên số dưới đây lấy từ Backend · Entry (52 tin)."
    )


def test_ad17_nhan_goi_dung_ten_cua_con_so_la_tin_doc_duoc_ky_nang() -> None:
    table = Table({key("fresher"): stats(26), key("entry"): stats(52)})
    choice = ask(selector(table, noun="tin đọc được kỹ năng"), "fresher")
    assert choice.label == (
        "Backend · Fresher chỉ có 26 tin đọc được kỹ năng (dưới 30), chưa đủ để tính riêng, "
        "nên số dưới đây lấy từ Backend · Entry (52 tin đọc được kỹ năng)."
    )
    table = Table({key("fresher"): stats(5), key("entry"): stats(12), key("all"): stats(20)})
    choice = ask(selector(table, noun="tin đọc được kỹ năng"), "fresher")
    assert choice.label == (
        "Chưa có tập nào đủ 30 tin đọc được kỹ năng (Backend · Fresher có 5 tin đọc được kỹ năng; "
        "Backend · Entry có 12 tin đọc được kỹ năng; Backend · mọi cấp có 20 tin đọc được kỹ năng), "
        "nên chưa đủ dữ liệu để hiện số."
    )


def test_ad2_quay_ve_all_khi_nhom_cung_thieu() -> None:
    mix = {"intern": 10, "fresher": 20, "junior": 10, "mid": 40, "senior": 20}
    table = Table({key("fresher"): stats(5), key("entry"): stats(12), key("all"): stats(100, mix)})
    choice = ask(selector(table), "fresher")
    assert choice.cell == key("all")
    assert choice.n == 100
    assert choice.label == (
        "Backend · Fresher chỉ có 5 tin (dưới 30), chưa đủ để tính riêng, nên số dưới đây lấy từ Backend · mọi cấp (100 tin)."
        " Trong tập này 60% tin là Mid trở lên."
    )


def test_fr19_buoc_cuoi_voi_cap_entry_ghi_ty_le_mid_tro_len() -> None:
    mix = {"intern": 10, "fresher": 20, "junior": 10, "mid": 40, "senior": 20}  # Mid trở lên = 60 / 100
    table = Table({key("fresher"): stats(5), key("entry"): stats(12), key("all"): stats(100, mix)})
    assert ask(selector(table), "fresher").label == (
        "Backend · Fresher chỉ có 5 tin (dưới 30), chưa đủ để tính riêng, nên số dưới đây lấy từ Backend · mọi cấp (100 tin)."
        " Trong tập này 60% tin là Mid trở lên."
    )
    # cả nhóm entry đi thẳng tới all cũng vậy
    table = Table({key("entry"): stats(12), key("all"): stats(100, mix)})
    assert ask(selector(table), "entry").label == (
        "Backend · Entry chỉ có 12 tin (dưới 30), chưa đủ để tính riêng, nên số dưới đây lấy từ Backend · mọi cấp (100 tin)."
        " Trong tập này 60% tin là Mid trở lên."
    )


def mid_share_label(mix: dict[str, int]) -> str:
    table = Table({key("entry"): stats(1), key("all"): stats(sum(mix.values()), mix)})
    label = ask(selector(table), "entry").label
    assert label is not None
    return label.rsplit(" Trong tập này ", 1)[1]


def test_fr19_ty_le_mid_tro_len_mau_so_la_moi_tin_ke_ca_unknown_va_lam_tron_len_o_nua() -> None:
    # Mẫu số là mọi tin của ô, kể cả `unknown`: Mid trở lên = mid 15 + senior 10 + lead 5 = 30 / 60 = 50%.
    # (Bỏ `unknown` khỏi mẫu số sẽ ra 30 / 50 = 60%.)
    mix = {"unknown": 10, "lead": 5, "mid": 15, "senior": 10, "intern": 5, "fresher": 10, "junior": 5}
    assert mid_share_label(mix) == "50% tin là Mid trở lên."
    # đúng .5 thì làm tròn lên (round() của Python cho 12): 1 / 8 = 12,5%
    assert mid_share_label({"mid": 1, "fresher": 7}) == "13% tin là Mid trở lên."
    assert mid_share_label({"mid": 7, "fresher": 1}) == "88% tin là Mid trở lên."
    assert mid_share_label({"mid": 1, "fresher": 2}) == "33% tin là Mid trở lên."
    assert mid_share_label({"fresher": 5}) == "0% tin là Mid trở lên."


def test_fr19_cap_mid_quay_ve_all_khong_ghi_ty_le_mid() -> None:
    mix = {"fresher": 20, "mid": 40, "senior": 40}
    table = Table({key("mid"): stats(5), key("all"): stats(100, mix)})
    choice = ask(selector(table), "mid")
    assert choice.cell == key("all")
    assert choice.label is not None and "%" not in choice.label


def test_fr19_khong_ghi_ty_le_mid_khi_khong_co_co_cau_cap() -> None:
    table = Table({key("fresher"): stats(5), key("all"): stats(100)})
    label = ask(selector(table), "fresher").label
    assert label is not None and "%" not in label


def test_ad2_khong_tap_nao_dat_thi_tra_o_cuoi_va_noi_chua_dat() -> None:
    table = Table({key("fresher"): stats(5), key("entry"): stats(12), key("all"): stats(20)})
    choice = ask(selector(table), "fresher")
    assert choice.cell == key("all")
    assert choice.n == 20
    assert choice.label == (
        "Chưa có tập nào đủ 30 tin (Backend · Fresher có 5 tin; Backend · Entry có 12 tin; Backend · mọi cấp có 20 tin),"
        " nên chưa đủ dữ liệu để hiện số."
    )


def test_ad2_khong_tap_nao_dat_o_thieu_han_van_tra_o_cuoi() -> None:
    choice = ask(selector(Table({})), "fresher")
    assert choice.cell == key("all")
    assert choice.n == 0
    assert choice.label is not None


def test_ad2_cap_all_chi_co_mot_ung_vien() -> None:
    table = Table({key("all"): stats(10)})
    choice = ask(selector(table), "all")
    assert choice.cell == key("all")
    assert choice.order == (key("all"),)
    assert choice.label is not None and "30" in choice.label
    assert table.asked == [key("all")]
    assert ask(selector(Table({key("all"): stats(30)})), "all").label is None


def test_ad2_thu_tu_quay_ve_tra_ve_cung_o_da_chon() -> None:
    table = Table({key("fresher"): stats(1), key("entry"): stats(1), key("all"): stats(100)})
    assert ask(selector(table), "fresher").order == (key("fresher"), key("entry"), key("all"))
    assert ask(selector(table), "entry").order == (key("entry"), key("all"))
    assert ask(selector(table), "mid").order == (key("mid"), key("all"))
    assert ask(selector(table), "unknown").order == (key("unknown"), key("all"))


def test_ad6_pham_vi_khong_bao_gio_doi() -> None:
    table = Table({key("all", scope="vn"): stats(500), key("entry", scope="vn"): stats(500)})
    table.cells[key("fresher", scope="hanoi")] = stats(3)
    choice = ask(selector(table), "fresher", scope="hanoi")
    assert choice.cell == key("all", scope="hanoi")  # ô Hà Nội không đủ mẫu, không lùi về `vn`
    assert choice.n == 0
    assert {c.scope for c in table.asked} == {"hanoi"}
    assert {c.scope for c in choice.order} == {"hanoi"}
    assert choice.label is not None and "30" in choice.label


def test_ad6_vai_tro_va_snapshot_khong_bao_gio_doi() -> None:
    table = Table({key("all", role="frontend"): stats(500)})
    choice = ask(selector(table), "fresher")
    assert choice.cell.role == "backend"
    assert {(c.role, c.snapshot_id) for c in table.asked} == {("backend", SNAP)}


def test_ad6_nhanh_giu_cap_truoc_nhanh_sau() -> None:
    java = "java_backend"
    table = Table({})
    ask(selector(table), "fresher", branch=java)
    assert table.asked == [
        key("fresher", branch=java),
        key("fresher"),
        key("entry", branch=java),
        key("entry"),
        key("all", branch=java),
        key("all"),
    ]


def test_ad6_nhanh_quay_ve_vai_tro_cung_cap_truoc() -> None:
    java = "java_backend"
    table = Table({key("fresher", branch=java): stats(26), key("fresher"): stats(52)})
    choice = ask(selector(table), "fresher", branch=java)
    assert choice.cell == key("fresher")
    assert choice.label == (
        "nhánh java_backend · Backend · Fresher chỉ có 26 tin (dưới 30), chưa đủ để tính riêng, "
        "nên số dưới đây lấy từ Backend · Fresher (52 tin)."
    )


def test_ad17_quyet_dinh_theo_co_mau_cua_phep_do_khong_phai_n_cua_o() -> None:
    # ô `fresher` có n = 40 nhưng chỉ 12 cụm đã quét kỹ năng: phải quay về `entry`
    table = Table({key("fresher"): stats(40, sample=12), key("entry"): stats(90, sample=70)})
    choice = ask(selector(table), "fresher")
    assert choice.cell == key("entry")
    assert choice.n == 70
    assert choice.label == (
        "Backend · Fresher chỉ có 12 tin (dưới 30), chưa đủ để tính riêng, nên số dưới đây lấy từ Backend · Entry (70 tin)."
    )


def test_ad2_cung_truy_van_cung_lua_chon() -> None:
    table = Table({key("fresher"): stats(26), key("entry"): stats(52)})
    sel = selector(table)
    query = CellQuery(key("fresher"), 30)
    first = sel.select_cell(query)
    assert all(sel.select_cell(query) == first for _ in range(5))
    assert selector(Table(table.cells)).select_cell(query) == first


def test_ad2_mot_doi_tuong_va_mot_lo_cho_cung_ket_qua() -> None:
    table = Table({key("fresher"): stats(26), key("entry"): stats(52), key("mid"): stats(80)})
    sel = selector(table)
    queries = [CellQuery(key("fresher"), 30), CellQuery(key("mid"), 30), CellQuery(key("entry"), 30)]
    singles = tuple(sel.select_cell(q) for q in queries)
    for batch in (queries, tuple(queries)):
        result = sel.select_cell(batch)
        assert isinstance(result, tuple)
        assert result == singles
    assert sel.select_cell([]) == ()
    assert sel.select_cell(list(reversed(queries))) == tuple(reversed(singles))


def test_ad2_min_sample_khong_hop_le_la_loi() -> None:
    sel = selector(Table({}))
    for bad in (0, -1):
        with pytest.raises(ValueError):
            sel.select_cell(CellQuery(key("all"), bad))
    with pytest.raises(ValueError):
        sel.select_cell(("khong phai query",))  # type: ignore[arg-type]
