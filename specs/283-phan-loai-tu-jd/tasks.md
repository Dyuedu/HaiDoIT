# Tasks: Phân loại tin ở bước ingest từ chức danh và nội dung JD

**Input**: `specs/283-phan-loai-tu-jd/` (spec.md, plan.md, data-model.md, research.md)

Test đứng trước code. Mỗi test mới phải đỏ trước khi có code (ghi trong tdd.md).

## Phase 1: Tests (RED)

- [x] T001 `tests/domain/test_gh283_posting_text.py`: `fold`; `requirement_text` giữ mục yêu cầu/nhiệm vụ, bỏ quyền lợi/giới thiệu/địa điểm, không có tiêu đề thì giữ hết, che "khoa học máy tính", cắt 50.000 ký tự; `find_mentions` cụm dài trước, đếm mọi lượt; số năm (số tháng của nguồn, giá trị bước trích, "không yêu cầu" → 0, yêu cầu chính, bỏ "thành lập 10 năm")
- [x] T002 `tests/domain/test_gh283_mapping.py`: `map_mentions` một/lô, song ngữ về một mã, chuỗi lạ `None`, "C/C++" ra hai mã, bí danh mơ hồ không có trong từ vựng; 100 mã cũ vẫn còn
- [x] T003 `tests/domain/test_gh283_classify_roles.py`: các scenario của User Story 1 và 2 (vai trò, chức danh con, tất cả lỗi đã thấy ở research.md), xác định
- [x] T004 `tests/domain/test_gh283_classify_levels.py`: User Story 4 (cấp từ chức danh, chữ cấp của nguồn, số năm theo bảng #134; Product Manager không phải Lead; non-manager bị bỏ qua)
- [x] T005 `tests/core/test_gh283_classify_config.py`: đọc `config/classify.toml`; thiếu khóa, cụm rỗng, nhãn vai trò chức danh con không có trong `roles`, bảng số năm không tăng → `ConfigError`; mọi nhãn vai trò có trong `[labels.role]` của `rules.toml`
- [x] T006 `tests/steps/test_gh283_ingest_classify.py` (Postgres): ingest ghi nhãn, mã kỹ năng có số lượt, `classify_version`; làm mới tin trong cửa sổ có phiên bản luật cũ; không thêm phiên bản khi nhãn đã đúng; aggregate dùng nhãn đã lưu, hàng cũ phân loại từ trường đóng
- [x] T007 `tests/db/test_gh283_facts_labels.py` (Postgres): migration 0007 (head, cột, hạ cấp); chuỗi đánh dấu trong mô tả không có ở cột text/jsonb nào của schema `haido`

## Phase 2: Implementation (GREEN)

- [x] T010 `haido_core/vocab/skills_seed.json`, `skills.py`: từ vựng mới, giữ 100 mã cũ
- [x] T011 `haido_core/domain/posting_text.py`, `haido_core/domain/mapping.py`
- [x] T012 `config/classify.toml`, `haido_core/config.py`, `haido_core/domain/classify.py`, `registry.py`, `REGISTRY.md`; `config/rules.toml`
- [x] T013 `haido_core/db/tables.py`, migration 0007, `snapshot_store.py`
- [x] T014 `haido_core/db/scraper_source.py`, `haido_core/steps/ingest.py`
- [x] T015 `haido_core/steps/aggregate.py`
- [x] T016 Sửa test cũ bị đổi kỳ vọng (luật cũ của `classify`, `FactVersion`, schema, từ vựng); ghi từng file trong tdd.md
- [x] T017 `tools/classify_eval/`: nhãn tay 180 tin (43 AI/ML hoặc khoa học dữ liệu) + 40 tin giữ riêng, script đo ba bộ; ghi kết quả và số trước/sau vào tdd.md
- [x] T018 Chạy toàn bộ: `uv run pytest -q`, hai lượt `-m determinism`, `uv run ruff check .`, `python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7`, `uv run alembic heads`; đo thời gian ingest trên bản sao local
- [x] T019 Cập nhật spec của #100, #163, #205, #280 (đợt TDD có ngày; data-model #280, Status #205)

## Phase 3: Sau merge

- [ ] T020 Lượt đêm đầu tiên sau deploy: log bước kho không lỗi, số dữ kiện được làm mới, tỷ lệ "không xác định cấp" và số AI/ML mới vào nghề của snapshot mới
