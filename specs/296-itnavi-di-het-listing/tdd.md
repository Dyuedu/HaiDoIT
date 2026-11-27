# TDD: ITnavi đi hết listing

Theo `docs/templates/test-driven-tdd/test-driven-development.md`.

Lệnh (giống job `scraper` của CI: Python 3.13, `requirements-vps.txt` + pytest; `.venv` cục bộ thiếu `psycopg` nên dùng venv riêng):

```text
cd scraper
python -m pytest tests -q
```

Test nằm trong `scraper/tests/test_observations.py`. `fake_itnavi` nhận thêm `total` (in thẻ `div.js-tab__show h1` như site) và `repeat_last` (site trả lại trang cuối mãi), và ghi lại các trang đã được gọi.

## Các hành vi

1. Trang 2 chỉ có id đã thấy, trang 3 có id mới → id trang 3 có trong file seen, lượt đủ.
2. Site lặp trang cuối → dừng sau đúng `STALE_PAGES` trang không có id mới, lượt đủ.
3. Listing trống từ trang 2, đã gặp 2 tin trong khi site in tổng 100 → lượt chưa xong, `error` "met 2 of 100".
4. Listing trống ở cuối, gặp đủ tổng → lượt đủ, `error` rỗng.
5. Chạm `--pages 2` khi trang 3 còn tin → lượt chưa xong, "hit --pages 2".

## RED (2026-11-15)

`python -m pytest tests -q` → 3 failed, 51 passed, 9 skipped (9 test ingest cần `TEST_DATABASE_URL`).

- Hành vi 1 đỏ: `assert 'https://x/3' in ['https://x/1', 'https://x/2']`. Crawler dừng ở trang 2 vì không có id mới.
- Hành vi 2 đỏ: `AttributeError: module 'crawlers.itnavi' has no attribute 'STALE_PAGES'`.
- Hành vi 3 đỏ: `assert True is False`. Trang trống được coi là hết listing bất kể mới gặp 2/100 tin.
- Hành vi 4 và 5 xanh sẵn: giữ lại để chặn bản sửa làm hỏng đường cũ.

## GREEN (2026-11-15)

- `python -m pytest tests -q` → 54 passed, 9 skipped.
- `ruff check crawlers/itnavi.py --select E,F,W` sạch.
- Chạy thật với site (`--limit 0`, thư mục tạm, không ghi vào DB): 49 trang, 482 id, `end: page 50 is empty`, tổng site in 485 → `listing_complete=True`.

## Kiểm sau merge

| Đêm | listed | complete | gone since last complete run | Ghi chú |
|---|---|---|---|---|
| 16/11 | 447 | true | 16 | so với lượt đủ 15/11 (346, lượt lỗi cũ) |
| 17/11 | 372 | false | 0 | `met 380 of 485`, trang 42 rỗng; snapshot `partial` |

Đêm 17/11 không đạt. Ba đêm liền tính lại từ đêm đầu sau khi bản tải lại trang rỗng (đợt 2) lên VPS.

## Đợt 2: trang rỗng tạm thời (2026-11-17)

Lý do: `daily-2026-11-17.log`, ITnavi trang 1–41 có tin, `end: page 42 is empty`, `seen: 372 jobs, listing_complete=False`, error `met 380 of 485 listed jobs`; snapshot `2026-11-17` chốt `partial`. Quét lại sáng 17/11 từ máy dev (chỉ listing, giãn 3 giây): trang 1–48 mỗi trang 10 tin, trang 49 có 5, trang 50–52 trống, 483 tin, tổng in trên trang 485. Trang 42 đêm qua rỗng tạm thời.

Hành vi mới:

6. Trang 2 trống ở lần tải đầu rồi có tin → tải trang 2 hai lần, file seen có tin trang 2 và 3, lượt đủ.
7. Trang 3 trống mãi → tải trang 3 đúng `EMPTY_PAGE_TRIES` lần.

`fake_itnavi` thêm `empty_first={page: n}`: trang đó trả trống ở n lần tải đầu.

### RED (2026-11-17)

`python -m pytest tests -q -p no:cacheprovider` → 3 failed, 74 passed, 9 skipped (gồm một test của #302).

- Hành vi 6 đỏ: `assert False is True` (`listing_complete`): trang 2 trống lần đầu kết thúc listing, mới gặp 2/5 tin.
- Hành vi 7 đỏ: `AttributeError: module 'crawlers.itnavi' has no attribute 'EMPTY_PAGE_TRIES'`.

### GREEN (2026-11-17)

- `python -m pytest tests -q -p no:cacheprovider` → 77 passed, 9 skipped.
- `uv run pytest -q` → 1018 passed, 217 skipped.

## Đợt #102 (2026-11-19): θ có phiên bản, AC của issue này không đổi

Lý do: #102 đóng băng θ (`config/theta.toml`, `theta-1` = 0,3/0,1), thêm `snapshots.theta_version` (migration 0010) và `meta.thresholds.theta_version`, sửa file mà issue này từng đụng: `config/rules.toml`, `tests/core/test_ad10_rules_config.py`.
Giá trị θ không đổi nên số, nhóm và hành vi của issue này không đổi; test chỉ thêm `theta_version` vào ngưỡng hoặc đổi head migration mong đợi sang 0010. Riêng `tests/core/test_ad10_rules_config.py`: `rules.toml` không còn `theta_core`/`theta_common` nên `BASE` dùng `theta_version`, và các ca kiểm θ cũ (thiếu khóa, giá trị ngoài [0, 1], `theta_common > theta_core`) đã chuyển sang `tests/core/test_gh102_theta_dong_bang.py`, nay kiểm trên `config/theta.toml`. RED, GREEN và đột biến: `specs/102-dong-bang-theta/tdd.md`.

## Đợt sửa 2026-11-27 (#230, hình tin dán "Soi tin")

**Vì sao sửa**: #230 thêm nguồn `posting_check` vào `SOURCE_ENV`, bảng `[posting_match]` vào `config/rules.toml`, ô `vn.backend.junior` vào
`fake_market.json`, route `posting-reads` và `posting-check`. Các file của issue này bị chạm: `config/rules.toml`, `tests/core/test_ad10_rules_config.py`.

**Hành vi của issue này**: không đổi; không AC nào của #296 đúng khác đi. Mọi thay đổi chỉ cộng thêm (khóa nguồn mới, mục cấu hình mới, ô và hàng
fixture mới, hàng tài liệu mới, nguồn `posting_check` trong các lời gọi `create_app` của test).

**RED/GREEN**: RED (chạy thật): trả 13 file test cũ dựng create_app với năm nguồn về bản ở HEAD rồi chạy với code mới thì 109 failed, 54 lỗi, 32 passed (thiếu nguồn posting_check). GREEN: sau khi thêm nguồn và sửa các file, uv run pytest -q toàn bộ được 2029 passed (không còn test nào đỏ của issue này). Chi tiết ở specs/230-hinh-soi-tin/tdd.md.
