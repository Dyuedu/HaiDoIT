# TDD: Cổng tất định cho thứ tự lộ trình

Theo `docs/templates/test-driven-tdd/test-driven-development.md`.

Mỗi test một hành vi. Test phép 8 không mạng, không cơ sở dữ liệu. Test cổng dựng cây thư mục tạm có `registry.py` thật.

Lệnh:

```text
uv run pytest -q tests/domain/test_fr22_order_path.py tests/tools/test_fr22_tat_dinh.py
HAIDO_TEST_DATABASE_URL=postgresql+psycopg://<user>:<mật khẩu local>@127.0.0.1:5433/tst139_test uv run pytest -q
uv run ruff check .
python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22
```

## Các hành vi

`tests/domain/test_fr22_order_path.py` (30 ca):

1. Đồ thị mẫu 12 nút cho đúng thứ tự tính tay (có hòa chặng, nhóm, tỷ lệ; `unused` bị loại; `helm` khai báo chặng 1 nhưng đứng cuối vì cạnh).
2. Xáo `gaps`, `edges`, `skills` (25 hạt giống và đảo ngược) không đổi kết quả; khoảng trống lặp không đổi kết quả.
3. Kéo tổ tiên bắc cầu và chỉ tổ tiên; khoảng trống không tổ tiên; khoảng trống rỗng.
4. Bốn tầng, mỗi tầng một test: chặng; nhóm cốt lõi, thường gặp, hiếm; tỷ lệ lớn trước; mã A–Z.
5. Cạnh thắng chặng khai báo.
6. Vòng ngoài tập được kéo vào bị bỏ qua.
7. Một yêu cầu trả `tuple` mã; lô (`list` và `tuple`) trả `tuple` cùng độ dài; lô rỗng; không đổi đầu vào.
8. Đầu vào sai (13 ca): khoảng trống lạ, cạnh lạ hai đầu, mã lặp, vòng và tự vòng, `rate` NaN, vô cực, âm, trên 1, `stage` 0 và âm, `band` không phải `SkillBand`; lỗi là `PathOrderError`, là `ValueError`; một yêu cầu sai trong lô thì cả lô lỗi.
9. `determinism`: ba tiến trình `PYTHONHASHSEED` 0, 1, 2 in cùng kết quả.

`tests/tools/test_fr22_tat_dinh.py` (12 ca): 4 ca hoãn cũ giữ nguyên (không có `path_order.py`: SKIP khi sổ hợp lệ; FAIL khi quá hạn, sai URL, thiếu sổ); thêm:

10. Bản giả `order_path` trả lại đầu vào phải FAIL (thay cho `test_fr22_with_order_path_function_passes`, cũ khẳng định PASS với đúng bản giả này).
11. Bản chỉ trả theo thứ tự `gaps` (phụ thuộc thứ tự đầu vào) phải FAIL.
12. Bản thật chép sang thư mục tạm PASS, chi tiết nêu 2026-12-13 và #139.
13. Mục hoãn quá hạn FAIL; thiếu mục FAIL.
14. Trên repo thật: PASS, chi tiết nêu #139 và 2026-12-13; sổ hoãn thật chỉ giữ hạn 2026-12-13; `ci.yml` có `FR-22` trong `--require`.

## RED (2026-11-16)

Viết hai file test trước khi có `path_order.py`.

- `uv run pytest -q tests/domain/test_fr22_order_path.py` → 1 error lúc thu thập: `ModuleNotFoundError: No module named 'haido_core.domain.path_order'` (không chạy được ca nào; 30 ca sẽ chạy sau khi có module).
- `uv run pytest -q tests/tools/test_fr22_tat_dinh.py` → 9 failed, 4 passed. Lý do: cổng cũ chỉ kiểm file có mặt, nên bản giả (trả lại đầu vào) được PASS thay vì FAIL; `path_order.py` thật không tồn tại để chép sang thư mục tạm; sổ hoãn thật còn mục `FR-22` hạn 2026-11-22 và real repo vẫn SKIP; `ci.yml` chưa có `FR-22`. 4 ca passed là bốn ca hoãn cũ.

(Lúc đó sổ hoãn dự định đặt tên mục là `FR-22/signals`; xem "Điều chỉnh" bên dưới.)

## GREEN

Thêm `haido_core/domain/path_order.py` (class `PathOrderer`), viết lại `gate_fr22_tat_dinh`, sửa `deferred.json` và `ci.yml`.

- `uv run pytest -q tests/domain/test_fr22_order_path.py tests/tools/test_fr22_tat_dinh.py tests/domain/test_ad2_registry.py` → 57 passed.
- Cổng `AD-2` đỏ ở lần đầu vì tôi để thêm một hàm `order_path` ở mức module (hai thân hàm cho phép 8). Bỏ hàm đó, cổng gọi `PathOrderer().order_path` (vẫn nhận hàm `order_path` ở mức module cho bản giả). AD-2 xanh.
- Điều chỉnh: lần chạy đầy đủ đầu tiên có một ca đỏ ở `tests/tools/test_ad11_ad21_rieng_tu.py` (`set(data) == {"FR-24", "FR-22"}`) vì tôi đã đổi tên mục thành `FR-22/signals`. Giữ nguyên khóa `FR-22`, đổi hạn sang 2026-12-13 và ghi chú AC2: không đụng test AD-11 và dòng FR-24 mà #138 sửa song song. Sửa test cổng tương ứng, bỏ một ca dư (PASS không phụ thuộc hạn cũ: nay cùng một mục).
- Kết quả cuối: xem "Kiểm cuối".

## Kiểm đột biến (2026-11-16)

Phá từng chỗ của `path_order.py`, chạy hai file test, khôi phục đúng nguyên byte (so băm MD5) sau mỗi ca.

| Đột biến | Kết quả |
|---|---|
| Bỏ tầng 1 (chặng cố định 0) | 9 failed |
| Bỏ tầng 2 (nhóm cố định 0) | 9 failed |
| Đảo tầng 3 (tỷ lệ nhỏ trước) | 9 failed |
| Đảo hạng nhóm (hiếm trước cốt lõi) | 9 failed |
| Tầng 4 theo `hash(skill_id)` thay vì mã (phụ thuộc hạt giống băm) | 9 failed (hai lần chạy) |
| Bỏ kéo tổ tiên | 14 failed |
| Bỏ cạnh trong Kahn (bậc vào cố định 0) | 11 failed |
| Duyệt `set` thay hàng đợi ưu tiên | 11 failed |

Ghi chú:

- Đột biến "tầng 4 = hằng 0" sống sót (42 passed): không phải lỗ hổng test mà là đột biến tương đương, vì hàng đợi lưu `(khóa, mã)` và mã trong tuple cũng quyết định khi khóa hòa. Thay bằng đột biến `hash(skill_id)`, bị bắt.
- Một đột biến thứ ba lúc đầu ("bỏ trừ bậc vào": `waiting[child] = 0`) làm vòng lặp không dừng khi gặp test vòng, nên pytest treo thay vì đỏ. Tôi đã dừng nó và khôi phục file; bộ đột biến dùng `waiting = {node: 0}` (không treo) thay cho nó. Không để file sao lưu nào lại.

## Kiểm cuối (2026-11-16)

- `uv run pytest -q` với Postgres local, DB riêng `tst139_test` (đã xóa sau khi xong) → 1271 passed, 0 failed, 0 skipped.
- `uv run ruff check .` → sạch.
- `python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22` → `[v] FR-22 Order path determinism PASS`; tổng 10 cổng: 9 pass, 1 skip (FR-24, của #138), 0 fail. Cổng FR-22 chạy khoảng 0,2 giây.
- `alembic heads` → `0008_haido_fact_city (head)`, không đổi.
- Ghi chú đã sửa ở đợt 2: lúc đầu tôi ghi rằng `test_ad2_cong_tren_repo_that` cần `PYTHONUTF8=1`. Nguyên nhân thật có từ trước đợt này: `main()` của cổng `print` chi tiết FAIL có tiếng Việt qua ống `cp1252` thì ném `UnicodeEncodeError` (mã thoát vẫn là 1). Đợt 2 đã sửa trong `main()` (xem bên dưới).

---

# Đợt 2 (2026-11-16): sửa theo review

Lý do: review chỉ ra (1) các phép kiểm của chính cổng không có test nào bắt khi bị xóa; (2) lời nhắc AC2 không in ra log CI; (3) fixture dùng ngày 2026-11-22 và 2026-12-13 sẽ đỏ theo lịch; (4) probe của cổng sập khi lỗi tiếng Việt trên Windows; (5) `order_path` ném `TypeError`, `AttributeError`, `OverflowError` thô với đầu vào sai kiểu. Đợt 1 ở trên giữ nguyên.

Lệnh:

```text
PYTHONUTF8=1 uv run pytest -q tests/domain/test_fr22_order_path.py tests/tools/test_fr22_tat_dinh.py
```

## Hành vi thêm

`tests/domain/test_fr22_order_path.py` (thêm 24 ca, tổng 54):

15. Sai kiểu thành `PathOrderError`: `stage` là `bool`, `rate` là `bool` hoặc `str` hoặc `10**400`; `skill_id` là `None`, `1`, `[]`; `gaps`, `edges`, `skills` là `str`, `None` hoặc phần tử sai kiểu; đầu cạnh không phải `str`; yêu cầu là `None` hoặc `str`; phần tử của lô không phải `PathRequest`.
16. `rate` = -0.0 hợp lệ và hòa với 0.0 (mã quyết định); cạnh lặp không đổi kết quả.

`tests/tools/test_fr22_tat_dinh.py` (thêm 10 ca, tổng 22):

17. Bốn bản giả đúng hình dạng, mỗi bản FAIL đúng vì một phép kiểm và test khẳng định câu hit cụ thể: A–Z (so thứ tự cứng), theo thứ tự đầu vào (xáo), lô trả một phần tử (lô), thứ tự theo `hash` (so hai hạt giống).
18. Bản giả ném `ValueError("Khoảng trống é à")` (bỏ `PYTHONUTF8` và `PYTHONIOENCODING`) FAIL với hit đọc được, cổng không sập.
19. Probe chạy đủ `FR22_SHUFFLES` (>= 20) biến thể xáo cộng một biến thể đảo ngược; cổng gọi probe với hai hạt giống khác nhau.
20. `main()` in lời nhắc "still deferred: ..." cho cổng PASS; không in chi tiết của cổng PASS khác; không ném `UnicodeEncodeError` trên ống cp1252.
21. Fixture dùng hạn 2099-12-31. Test `test_fr22_real_repo_passes_with_the_signals_deferral_in_the_detail` (đổi tên từ `..._and_prints_...`, vì nó chỉ kiểm chi tiết; việc in nằm ở ca 20) dùng repo thật và cố ý đỏ sau 2026-12-13.

## RED (đợt 2)

- `tests/domain/test_fr22_order_path.py` → 19 failed, 35 passed. Lý do: `request.skills` là `None`, `str` hoặc phần tử sai kiểu cho `AttributeError` hoặc `TypeError` thô (kể cả `unhashable type: 'list'` khi `skill_id` hoặc đầu cạnh là `list`); `10**400` cho `OverflowError` ở `math.isfinite`. 5 ca đã xanh: `stage` bool, `rate` bool, `rate` str, -0.0, cạnh lặp (đợt 1 đã có hàng rào).
- `tests/tools/test_fr22_tat_dinh.py` → 4 failed, 18 passed. Lý do: chi tiết PASS còn chứa "code not present yet" (ca repo thật); `main()` không in chi tiết khi PASS; `main()` ném `UnicodeEncodeError` trên ống cp1252; probe sập `AttributeError: 'NoneType' object has no attribute 'strip'` vì `UnicodeDecodeError` khi đọc stderr cp1252. Các ca bản giả (A–Z, thứ tự đầu vào, lô, hạt giống) và ca số lần xáo xanh ngay vì cổng đã có sẵn phép kiểm; giá trị của chúng được chứng minh bằng bảng đột biến bên dưới.

## GREEN (đợt 2)

Sửa `path_order.py` (`_items`, kiểm kiểu trước, kiểm miền `rate` trước `isfinite`), `check_gates.py` (`_deferral` tách khỏi `check_deferred`, chi tiết PASS mới, probe ép `PYTHONUTF8=1`, `PYTHONIOENCODING=utf-8`, `errors="replace"`, chặn `None`; `main()` in chi tiết PASS có "still deferred" và `sys.stdout.reconfigure(errors="replace")`), ghi chú `deferred.json`.

- `uv run pytest -q tests/domain/test_fr22_order_path.py tests/tools/test_fr22_tat_dinh.py` → 76 passed (54 + 22).

## Kiểm đột biến cho chính cổng (đợt 2)

Sửa từng dòng của `tools/gates/check_gates.py`, chạy `tests/tools/test_fr22_tat_dinh.py`, khôi phục đúng byte (so MD5).

| Đột biến | Kết quả | Test đỏ |
|---|---|---|
| Bỏ phép so thứ tự cứng | 1 failed | `..._fails_on_a_well_formed_but_wrong_order` |
| Bỏ phép xáo đầu vào | 1 failed | `..._depends_on_input_order` |
| Bỏ phép so hai hạt giống | 1 failed | `..._depends_on_the_hash_seed` |
| Bỏ phép kiểm lô | 1 failed | `..._a_batch_gives_a_different_shape` |
| Chỉ một hạt giống | 2 failed | `..._depends_on_the_hash_seed`, `..._compares_two_different_hash_seeds` |
| `FR22_SHUFFLES = 0` | 1 failed | `..._runs_the_configured_number_of_shuffles` |
| Bỏ ép UTF-8 của probe | 1 failed | `..._vietnamese_crash_message_without_crashing` |
| `main()` không in lời nhắc khi PASS | 1 failed | `..._prints_the_signals_deferral_reminder_for_a_pass` |
| `main()` không `reconfigure` stdout | 1 failed | `..._survives_vietnamese_in_a_failing_detail_on_a_cp1252_pipe` |

Bản giả thứ tự theo `hash` khác nhau giữa `PYTHONHASHSEED` 0 và 1 trên đồ thị mẫu (test xanh và đột biến "một hạt giống" làm nó đỏ).

## Giả ngày (đợt 2)

Plugin pytest tạm thay `datetime.date.today()` của `check_gates`, chạy `tests/tools` và `tests/domain`:

| Hôm nay giả | Kết quả |
|---|---|
| 2026-11-23 | 2 failed (cả hai là test FR-24 của #138, hạn 2026-11-22, không thuộc đợt này), 446 passed. Không test FR-22 nào đỏ. |
| 2026-12-14 | 3 failed: hai test FR-24 như trên, và `test_fr22_real_repo_passes_with_the_signals_deferral_in_the_detail` (cố ý, hạn AC2). 445 passed. |

## Kiểm cuối (đợt 2)

- `uv run pytest -q` với DB `fx139_test` (đã xóa sau khi xong) → 1305 passed (1271 của đợt 1 cộng 34 ca mới).
- `uv run ruff check .` → sạch.
- `python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22` (cả `python` thuần, không đặt `PYTHONUTF8`) in:

```text
 [v] FR-22        Order path determinism                            PASS
        order check passed (expected order, 20 shuffles, PYTHONHASHSEED 0/1, batch); still deferred: match level, signals, insight sentences until 2026-12-13 (https://github.com/Dyuedu/HaiDoIT/issues/139)
```
