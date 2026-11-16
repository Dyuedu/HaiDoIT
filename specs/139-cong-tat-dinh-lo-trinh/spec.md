# Feature Specification: Cổng tất định cho thứ tự lộ trình

**Feature Branch**: `gh-139-cong-tat-dinh-lo-trinh`

**Created**: 2026-11-16

**Status**: AC1 và AC3 đã làm xong, chờ merge. AC2 (mức khớp, tín hiệu, câu Insights, hạn 2026-12-13) ngoài phạm vi đợt này, còn hoãn trong `tools/gates/deferred.json` (mục `FR-22`, hạn 2026-12-13).

**Input**: GitHub issue [#139](https://github.com/Dyuedu/HaiDoIT/issues/139) — Determinism gate for path order, match level, signals, and insight sentences. Task ràng buộc (`type:chore`) phục vụ #110, #117, #121, #125, #126.

**Chồng lấn với #213 (Sprint 4)**: để cổng kiểm được một thứ tự thật, issue này cài thân hàm của phép 8 `order_path` (`haido_core/domain/path_order.py`). #213 vẫn là chủ của việc nối đồ thị đã rà soát (#96) và θ đã chốt (#102) vào phép này, và của việc đưa vào API. Đợt này không sửa `haido_api/learning_path.py` (logic chặng bên API của #212) và không nối API.

**Ghi chú cho #213 và #219 (không sửa issue nào trên GitHub, không AC nào của chúng đổi)**:

- θ đi vào phép này dưới dạng `SkillBand` đã tính sẵn trên từng `PathSkill` (core, common, rare). Phép 8 không tính θ.
- AC2 của #213 ("cùng đồ thị và cùng θ ra cùng thứ tự") đã đạt ở mức miền (domain) nhờ đợt này; #213 vẫn phải nối đồ thị #96 và θ #102. AC của #219 ("chạy thứ tự hai lần trả cùng thứ tự") được phủ ở mức miền bởi test xáo đầu vào và test hai `PYTHONHASHSEED`.
- Cần đối chiếu khi nối: `haido_api/learning_path.py::stage_numbers` (từ #212) dùng `requires: mã -> các mã cần trước` và ném lỗi với mọi vòng trong cả đồ thị, còn `order_path` nhận cạnh `before -> after` và bỏ qua vòng nằm ngoài tập được kéo vào. #213 phải thống nhất hướng cạnh và luật vòng này.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cổng CI chặn thứ tự lộ trình không tất định (Priority: P1)

Người làm #213, #216 sửa luật xếp hoặc đồ thị. Nếu cùng đồ thị và cùng θ mà thứ tự đổi theo thứ tự đầu vào hay `PYTHONHASHSEED`, cổng FR-22 đỏ trước khi merge.

**Why this priority**: AC1 của #139, hạn 2026-11-22.

**Independent Test**: `tests/domain/test_fr22_order_path.py`, `tests/tools/test_fr22_tat_dinh.py`, và `python tools/gates/check_gates.py --require ... FR-22`.

**Acceptance Scenarios**:

1. **Given** đồ thị mẫu 12 nút có hòa chặng, nhóm và tỷ lệ, **When** gọi `order_path`, **Then** kết quả bằng thứ tự đã tính tay: `python, git, linux, sql, http, rest, ci, docker, postgres, kubernetes, helm` (AC1: cùng đồ thị, cùng θ, cùng thứ tự).
2. **Given** cùng yêu cầu nhưng `gaps`, `edges`, `skills` bị xáo (25 hạt giống và một lần đảo ngược), **When** gọi, **Then** kết quả không đổi.
3. **Given** hai tiến trình `PYTHONHASHSEED=0` và `1`, **When** chạy cùng yêu cầu, **Then** kết quả giống hệt.
4. **Given** khoảng trống `rest`, **When** gọi, **Then** kết quả có `rest` cùng mọi tổ tiên bắc cầu (`python`, `http`) và không có nút nào khác (`unused`).
5. **Given** luật bốn tầng, **When** hai nút hòa tầng trước, **Then** tầng kế quyết định: chặng nhỏ trước; cốt lõi, thường gặp, hiếm; tỷ lệ lớn trước; mã kỹ năng. Tầng 4 là so sánh chuỗi theo điểm mã (codepoint) thuần, không chuẩn hóa, trên mã chuẩn đã viết thường: mọi mã trong `haido_core/vocab/skills_seed.json` (225 mã) là chữ thường, số và dấu gạch dưới, nên "A–Z" nghĩa là thứ tự từ điển của chữ thường. Hai mã hoa và thường khác nhau sẽ xếp theo điểm mã (hoa trước), vì phép 8 không viết thường hộ.
6. **Given** một cạnh bắt nút có chặng khai báo nhỏ đứng sau nút có chặng lớn, **When** gọi, **Then** cạnh thắng.
7. **Given** một lô (`list` hoặc `tuple`), **When** gọi, **Then** trả `tuple` cùng độ dài, mỗi phần tử là một thứ tự; một yêu cầu trả một `tuple` mã.
8. **Given** đầu vào sai (khoảng trống hoặc cạnh nhắc mã không có trong `skills`, mã lặp, vòng, `rate` NaN, vô cực, ngoài [0, 1] hoặc là số nguyên rất lớn, `stage` dưới 1 hoặc `bool`, `rate` là `bool`, `band` không phải `SkillBand`), **When** gọi, **Then** `PathOrderError` (là `ValueError`) nói rõ lý do. Vòng ngoài tập được kéo vào không ảnh hưởng đầu ra nên bị bỏ qua.
8b. **Given** sai kiểu (`gaps`, `edges` hoặc `skills` là `str`, `None` hoặc không phải `tuple`/`list`; phần tử sai kiểu; `skill_id` không phải `str`, kể cả `None`, số, `list`; đầu cạnh không phải `str`; yêu cầu không phải `PathRequest`, kể cả `None`), **When** gọi, **Then** cũng là `PathOrderError`, không bao giờ là `TypeError`, `AttributeError` hay `OverflowError` thô. `rate` = -0.0 hợp lệ và hòa với 0.0; cạnh lặp không ảnh hưởng.
9. **Given** cổng FR-22 với `path_order.py` có mặt, **When** chạy, **Then** nó gọi `order_path` thật trên đồ thị mẫu có sẵn trong cổng, so với thứ tự cứng, xáo đầu vào 20 lần, kiểm một lô hai yêu cầu, chạy ở hai tiến trình `PYTHONHASHSEED=0` và `1`, rồi PASS hoặc FAIL kèm hits. Bản thật phải PASS. Mỗi phép kiểm có một bản giả đúng hình dạng nhưng sai riêng phép đó, và phải FAIL đúng vì phép đó: thứ tự sai tất định (A–Z) thì dính phép so thứ tự cứng; phụ thuộc thứ tự đầu vào thì dính phép xáo; lô trả sai hình dạng thì dính phép kiểm lô; thứ tự theo `hash(str)` thì dính phép so hai hạt giống. Bản giả trả lại đầu vào hoặc ném lỗi thì FAIL kèm dòng "crashed", kể cả khi lỗi có tiếng Việt trên Windows (tiến trình con được ép UTF-8, giải mã `errors="replace"`).
10. **Given** CI, **When** chạy bước cổng, **Then** `FR-22` nằm trong `--require`, nên SKIP cũng đỏ.

---

### User Story 2 - Hoãn có tên và có hạn (Priority: P2)

**Why this priority**: AC3 của #139 và hạn 2026-12-13 của AC2.

**Independent Test**: `tests/tools/test_fr22_tat_dinh.py`.

**Acceptance Scenarios**:

1. **Given** chưa có `path_order.py`, **When** chạy cổng, **Then** `deferred.json` mục `FR-22` nêu #139 và 2026-11-22; log CI in ra lời hoãn (AC3). Quá hạn hoặc thiếu mục thì FAIL. Nhánh này vẫn giữ để bảo vệ (xóa `path_order.py` thì cổng lại hoãn, và CI với `--require FR-22` coi SKIP là đỏ). Trong `deferred.json` thật, mục `FR-22` nay mang hạn 2026-12-13 của AC2 (xem kịch bản 2).
2. **Given** `path_order.py` có mặt, **When** chạy cổng, **Then** PASS do phép kiểm thứ tự quyết định, không do sổ hoãn. Chi tiết là "order check passed (...); still deferred: match level, signals, insight sentences until 2026-12-13 (<URL #139>)", lấy hạn và URL từ mục `FR-22`. `main()` in dòng chi tiết này cả khi PASS (chỉ khi nó chứa "still deferred"; các cổng PASS khác vẫn không in chi tiết), nên log CI thấy lời nhắc AC2.
3. **Given** mục `FR-22` quá hạn hoặc thiếu, **When** chạy cổng, **Then** FAIL: để quá 2026-12-13 mà chưa làm AC2 thì CI đỏ.
4. **Given** AC2 của #139 (mức khớp, tín hiệu, câu Insights) hoãn tới 2026-12-13, **When** cổng chạy trước hạn, **Then** log CI in lời nhắc ở kịch bản 2; **When** chạy sau hạn mà mục `FR-22` còn trong `deferred.json`, **Then** cổng FAIL ("deferred deadline expired") và test `test_fr22_real_repo_passes_with_the_signals_deferral_in_the_detail` cũng đỏ, cố ý. Lưu ý: `ci.yml` chỉ chạy khi `pull_request` và `push` lên main, nên màu đỏ chỉ hiện ở PR hoặc lần push kế tiếp sau 2026-12-13, không tự đỏ đúng ngày. Muốn hết đỏ thì làm AC2 và bỏ mục `FR-22`.
5. **Given** cổng in ra ống `cp1252` (Windows), **When** chi tiết FAIL có tiếng Việt, **Then** `main()` không ném `UnicodeEncodeError` mà thay ký tự không mã hóa được, mã thoát vẫn là 1.

---

### User Story 3 - AC2: mức khớp, tín hiệu, câu Insights (Priority: P3, ngoài phạm vi)

**Ngoài phạm vi đợt này.** Hạn 2026-12-13. Khi các phép đó có thân hàm, mở rộng cùng cổng, rồi bỏ mục `FR-22`. Chưa có kịch bản kiểm vì chưa có mã để kiểm.

### Edge Cases

- Fixture của test cổng dùng sổ hoãn hạn 2099-12-31 để không đỏ theo lịch; chỉ test trên repo thật gắn với 2026-12-13.
- Khoảng trống rỗng: trả `()`. Khoảng trống lặp: tính một lần.
- Cạnh lặp: không ảnh hưởng.
- `rate` đúng 0 hoặc 1: hợp lệ.
- Kiểu `bool` không được tính là `stage` hay `rate`; `rate` = -0.0 hòa với 0.0.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-22** (PRD addendum): sắp xếp topo theo Kahn, hàng đợi ưu tiên khóa (chặng, nhóm, −tỷ lệ, mã); kéo tổ tiên bằng truy vết; không phụ thuộc thứ tự cơ sở dữ liệu.
- **AD-2**: một class `PathOrderer` trong `path_order.py`, đúng chữ ký ở `REGISTRY.md` hàng 8; không thêm phép, không đổi chữ ký.
- **AD-1**: module chỉ import thư viện chuẩn và registry.

### Key Entities

- `PathRequest`, `PathSkill`, `GraphEdge`, `SkillBand`: đã có ở `registry.py`, không đổi.
- `PathOrderError(ValueError)`: mới.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- `uv run pytest -q` xanh; `check_gates.py --require ... FR-22` in `FR-22 PASS`.
- Phá từng tầng của luật (bảng ở `tdd.md`) thì có test đỏ.

## Assumptions

- Mã kỹ năng chuẩn là chữ thường (đã kiểm với `skills_seed.json`); phép 8 so mã theo điểm mã, không chuẩn hóa.
- θ đã được tính ở nơi khác và đến phép 8 dưới dạng `SkillBand` trên `PathSkill`.
- Phép 8 nhận cạnh `before -> after`; việc đối chiếu với `requires` của `stage_numbers` (#212) thuộc #213.
- Cổng chạy bằng `python` thuần (CI không cài gói), nên chỉ dùng thư viện chuẩn.
