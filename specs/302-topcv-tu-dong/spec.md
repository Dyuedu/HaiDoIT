# Feature Specification: TopCV chạy trong lượt đêm trên VPS

**Feature Branch**: `gh-302-topcv-tu-dong`

**Created**: 2026-11-16

**Status**: Code xong, test xanh. Chưa build image trên VPS.

**Input**: GitHub issue [#302](https://github.com/Dyuedu/HaiDoIT/issues/302) — Run TopCV in the nightly crawl on the VPS.

## Bối cảnh

Ngày 03/11 nhóm quyết định TopCV chỉ chạy tay trên máy có người ngồi (`deploy/topcv-manual.sh`), không tự động hoá cho tới khi TopCV trả lời thư xin phép. Ngày 16/11 người dùng bỏ quyết định đó và bỏ luật "bị chặn thì dừng" cho TopCV: TopCV chạy trong `daily.sh`, trong image `scraper-browser`. Thư xin phép vẫn chưa gửi.

Khi rà code có một lỗi độc lập: `main()` nạp toàn bộ URL trong `job_queue` vào file seen khi listing không thấy tin nào (ví dụ trang 1 bị chặn). `job_observations` khi đó ghi các tin cũ là "hôm nay vẫn thấy".

## User Scenarios & Testing *(mandatory)*

### User Story 1 - File seen chỉ chứa tin hôm nay thấy (Priority: P1)

**Why this priority**: AC thứ nhất. Sai ở đây làm hỏng vòng đời tin của cả nguồn.

**Independent Test**: `test_topcv_blocked_first_page_writes_no_old_urls`.

**Acceptance Scenarios**:

1. **Given** `job_queue` có một URL cũ và trang listing 1 hiện kiểm tra Cloudflare, **When** `main()` chạy, **Then** file seen của `topcv` có `job_urls = []` và `listing_complete = false`.

---

### User Story 2 - Profile và hàng đợi giữ qua các đêm (Priority: P1)

**Why this priority**: AC thứ hai. Container `--rm` mất mọi thứ ngoài volume `/app/data`.

**Acceptance Scenarios**:

1. **Given** không đặt `TOPCV_DB` và `TOPCV_PROFILE_DIR`, **When** import `crawlers.topcv`, **Then** `DB_PATH` là `data/state/topcv_jobs.db` và `PROFILE_DIR` là đường dẫn tuyệt đối của `data/state/chrome_topcv_profile`.

---

### User Story 3 - Điều khiển TopCV từ pipeline (Priority: P1)

**Why this priority**: AC thứ ba và thứ tư.

**Acceptance Scenarios**:

1. **Given** listing có tin, **When** `topcv.py --skip-details`, **Then** không trang chi tiết nào được mở và listing vẫn `complete`.
2. **Given** listing có 3 tin chờ, **When** `topcv.py --limit 2`, **Then** mở đúng 2 trang chi tiết.
3. **Given** `pipeline.py crawl --sources topcv --skip-details --limit 5`, **When** chạy, **Then** topcv nhận `--skip-details --limit 5`.
4. **Given** Linux không có `DISPLAY`, **When** `run_crawler("topcv")`, **Then** lệnh bắt đầu bằng `xvfb-run` và timeout là 6 giờ.
5. **Given** có `DISPLAY`, hoặc nguồn là `momo`/`itviec`, **When** `run_crawler`, **Then** lệnh không bọc `xvfb-run`.

---

### User Story 4 - Image và lịch đêm (Priority: P1)

**Why this priority**: AC thứ năm, sáu, bảy.

**Acceptance Scenarios**:

1. **Given** `Dockerfile.browser`, **Then** có `google-chrome-stable`, `xvfb`, `CHROME_PATH`, `nodriver==` ghim, và vẫn `playwright==1.64.1`.
2. **Given** `compose.scraper.yml`, **Then** `scraper-browser` có `shm_size: 1g`.
3. **Given** `daily.sh`, **Then** bước trình duyệt là `--sources momo,itviec,topcv`.
4. **Given** `topcv-manual.sh`, **Then** không còn đặt `TOPCV_DB`.
5. README của scraper và `docs/permissions/topcv.md` không còn ghi TopCV chỉ chạy tay.

### Edge Cases

- Container lần trước bị kill: file `Singleton*` trong profile bị xoá trước khi mở Chrome.
- Listing bị chặn giữa chừng: lượt ghi các URL đã thấy với `complete = false`, rồi vẫn cào chi tiết các tin đang chờ, như bản chạy tay.
- Đêm đầu trên VPS hàng đợi rỗng: phải cào chi tiết toàn bộ tin, có thể chạm timeout 6 giờ. File seen đã ghi trước bước chi tiết nên quan sát của ngày không mất. Chép `topcv_jobs.db` từ máy local vào volume thì tránh được.
- Hàng đợi có tiêu đề `NULL`: log in chuỗi rỗng thay vì lỗi.

## Requirements *(mandatory)*

- **FR-001**: `main()` không dùng URL trong `job_queue` để ghi file seen.
- **FR-002**: `TOPCV_PROFILE_DIR` mặc định `data/state/chrome_topcv_profile`, tuyệt đối theo thư mục chạy.
- **FR-003**: `topcv.py` nhận `--skip-details` và `--limit N` (0 = không giới hạn).
- **FR-004**: `pipeline.py` truyền hai cờ trên cho nguồn `nodriver`; bọc `xvfb-run` khi Linux không có `DISPLAY`; topcv timeout `6 * 3600`.
- **FR-005**: Chrome mở với `--no-sandbox`, `--disable-setuid-sandbox`, `--disable-dev-shm-usage`, `--window-size=1920,1080`.

## Success Criteria *(mandatory)*

- **SC-001**: `cd scraper && python -m pytest tests -q` và `uv run pytest tests/deploy -q` xanh.
- **SC-002**: Đêm đầu sau khi build image, `daily-*.log` có `[topcv] OK` và dòng `topcv listed=… complete=True`.
