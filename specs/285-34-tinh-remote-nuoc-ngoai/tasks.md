# Tasks: Đếm theo 34 tỉnh, thành, cộng Remote và Nước ngoài

**Input**: `specs/285-34-tinh-remote-nuoc-ngoai/`

Test đứng trước code. Mỗi test mới phải đỏ trước khi có code (ghi trong tdd.md).

## Phase 1: Tests (RED)

- [x] T001 `tests/domain/test_gh285_city.py`: tỉnh cũ → tỉnh mới, cụm sớm nhất, dòng địa chỉ, Remote, Nước ngoài, thứ tự quyết nơi; `address_text`
- [x] T002 `tests/domain/test_gh285_aggregate_sparse.py`: chỉ nơi có tin cộng `always_cities`; tỷ trọng cộng bằng 1
- [x] T003 `tests/deploy/test_gh285_noi_khop_config.py`: 34 tỉnh trong config và classify, mỗi nhãn có mã; nhãn web khớp config; bản giả không còn `other`
- [x] T004 `tests/steps/test_gh285_ingest_city.py`, `tests/db/test_gh285_fact_city.py` (Postgres): cột `city`, migration 0008, ingest lưu nơi từ dòng địa chỉ, aggregate dùng nơi đã lưu
- [x] T005 `web/tests/fr33-provinces.test.tsx`: ba thanh, ba dòng chú thích, bảng có tỉnh khác theo số tin

## Phase 2: Implementation (GREEN)

- [x] T010 config (`rules.toml`, `classify.toml`, `config.py`)
- [x] T011 `posting_text.address_text`, `registry.py`, `REGISTRY.md`, `classify.py`
- [x] T012 `tables.py`, migration 0008, `snapshot_store.py`, `ingest.py`, `steps/aggregate.py`
- [x] T013 `domain/aggregate.py` (`always_cities`)
- [x] T014 web (`labels.ts`, `city-shares-view.ts`); bản giả và fixture web
- [x] T015 Sửa test cũ theo mã nơi mới; ghi trong tdd.md
- [x] T016 Chạy toàn bộ; chạy lại snapshot 12/11 trên bản sao (tỷ lệ không xác định nơi, số hàng `stat_*`); 360px
- [x] T017 Cập nhật spec của #283, #284, #163, #280, #144, #100

## Phase 3: Sau merge

- [ ] T020 Lượt đêm đầu sau deploy: không còn hàng `other`; có hàng tỉnh ngoài ba thành phố
