# Implementation Plan: Đếm theo 34 tỉnh, thành, cộng Remote và Nước ngoài

**Branch**: `gh-285-34-tinh` (tách từ `gh-284-them-vai-tro`; PR #287, #288 chưa merge) | **Date**: 2026-11-13 | **Spec**: [spec.md](spec.md)

## Summary

Nơi làm việc phân loại ở `ingest`: tỉnh trong trường `location` (tên mới, tên cũ, thành phố, huyện hay gặp → 34 tỉnh, thành), rồi nước ngoài, rồi tỉnh và nước ngoài trong dòng địa chỉ của JD, rồi remote. Lưu vào `job_posting_facts.city` (migration 0008). Bảng tỉnh nằm ở `config/classify.toml`, mã và nhãn ở `[labels.city]` của `config/rules.toml`. `aggregate_city_shares` chỉ ghi hàng của nơi có tin, cộng `always_cities`. Web thêm nhãn 34 tỉnh, chú thích là Remote, Nước ngoài, Không xác định, bảng liệt kê các tỉnh còn lại theo số tin.

## Technical Context

**Language/Version**: Python 3.13; TypeScript 5, Next.js 16, React 19. Không thêm gói.

**Storage**: migration `0008_haido_fact_city` (cột `city` text, null). `stat_*` không đổi cột; số hàng phụ thuộc số nơi có tin.

**Testing**: pytest (Postgres), vitest, lint, tsc, build; Chrome headless ở 360px.

**Constraints**: không đọc JD ngoài bộ nhớ; tỷ trọng mỗi bộ lọc cộng bằng 1; API không đếm (AD-5); web không cộng chia (AD-22) — web chỉ sắp dòng theo `n` đã có.

## Constitution Check

- AD-2: không thêm phép; phép 6 thêm đầu vào `address_text`; `REGISTRY.md` ghi rõ.
- AD-10: bảng tỉnh và `always_cities` là config có phiên bản.
- AD-17: nơi dưới 30 tin làm mờ qua `suppression_for`.
- AD-25: một head Alembic.

## Project Structure

```text
config/rules.toml, config/classify.toml
haido_core/config.py                       (mã nơi từ config, always_cities, bảng nơi của classify)
haido_core/domain/registry.py, REGISTRY.md (PostingFacts.address_text)
haido_core/domain/posting_text.py          (address_text)
haido_core/domain/classify.py              (_city mới)
haido_core/domain/aggregate.py             (always_cities, bỏ hàng 0)
haido_core/db/tables.py, migrations/0008_haido_fact_city.py, snapshot_store.py
haido_core/steps/ingest.py, steps/aggregate.py
haido_api/fixtures/fake_market.json, web/tests/fixtures/*.json
web/lib/labels.ts, web/lib/city-shares-view.ts
tests/domain/test_gh285_city.py, tests/domain/test_gh285_aggregate_sparse.py,
tests/steps/test_gh285_ingest_city.py, tests/db/test_gh285_fact_city.py,
tests/deploy/test_gh285_noi_khop_config.py, web/tests/fr33-provinces.test.tsx   (mới)
```

## Spec của issue cũ bị đụng

- `classify.py`, `ingest.py`, `aggregate.py`, `classify.toml`: #283; `rules.toml`, `labels.ts`, bản giả: #284, #163, #280, #144; `aggregate.py` (domain): #93 (không có `specs/`), #100, #163, #280.
- #112 (không có `specs/`): AC "Other appears only in the legend" không còn đối tượng; ghi trong mô tả PR và báo người dùng.
