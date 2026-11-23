# Data model: mã kỹ năng cho các thẻ hay gặp (#278)

## Lược đồ DB: không đổi

Không có migration Alembic, không đổi bảng hay cột. Head Alembic giữ nguyên. Từ vựng là file trong `haido_core/vocab/`, không nằm trong DB; `job_posting_facts.skills` (mã → số lượt) và `job_posting_facts.vocab_version` (từ #283) đã đủ chỗ cho mã mới và phiên bản mới.

## `haido_core/vocab/skills_seed.json` (đổi)

| Khóa | Trước | Sau |
|---|---|---|
| `version` | `seed-2026-11-13` | `seed-2026-11-23` |
| `skills[]` | 225 mã | 265 mã (40 mã mới), vẫn xếp theo mã, không trùng |
| `skills[].aliases` | | thêm bí danh vào mã có sẵn (73 thẻ) và cách viết thật của các thẻ của mã mới (67 thẻ vào 40 mã) |
| `composites` | `c/c++`, `python/r`, `r/python` | thêm `agile/scrum`, `agile scrum`, `javascript/typescript`, `html/css`, `c#/.net`, `ai/ml`. Phần của `ai/ml` là `ai`, `ml` (đợt review 2026-11-23; bản đầu dùng `artificial intelligence`, `machine learning` không có trong cụm nên lượt nhắc có vị trí -1). `load_vocabulary` nay từ chối mã ghép có phần không nằm trong cụm |
| `scan_skip` | 22 từ | 58 từ: 47 từ (hợp của 22 từ cũ và 31 từ của quyết định; 6 từ đã có sẵn: `ai`, `soc`, `lan`, `solid`, `word`, `rest`) cộng 11 từ của đợt review 2026-11-23: `bao mat`, `lap ke hoach`, `phan quyen`, `wifi`, `wi-fi`, `it infrastructure`, `it operations`, `it support`, `presentation`, `khoa hoc du lieu`, `tri tue nhan tao` |

### `scan_skip`: file quyết định tự mâu thuẫn

`quyet-dinh-2026-11-20.json` có hai nơi nói về `scan_skip`: danh sách `scan_skip` (31 từ) và cờ `scan_skip: true` trên từng mã mới (`cloud_computing`, `api`, `http`, `databases`, `windows`, `debugging`, `mes`, `can_bus`). Hai nơi không khớp: cờ của mã `debugging` đáng ra bao `debugging`, của `api` bao `api design` và `webhook`, của `http` bao `http/https`, nhưng các khóa đó không có trong danh sách. Đã làm theo **danh sách** (31 từ), không theo cờ: `debugging`, `api design`, `webhook`, `http/https` vẫn được quét trong JD. Danh sách là thứ test kiểm (`test_gh278_scan_skip_khong_nam_trong_tu_duoc_quet_nhung_van_tra_duoc`).

Mã mới có `source = "gh-278: thẻ kỹ năng của snapshot 2026-11-20"`. 40 mã mới: `devops`, `data_science`, `artificial_intelligence`, `cloud_computing`, `api`, `http`, `tls`, `databases`, `windows`, `macos`, `operating_systems`, `code_review`, `stakeholder_management`, `game_development`, `json`, `xml`, `sast_dast`, `sdlc`, `troubleshooting`, `debugging`, `integration_testing`, `workflow_automation`, `big_data`, `system_administration`, `risk_management`, `presentation`, `technical_writing`, `analytical_thinking`, `independent_work`, `market_research`, `core_banking`, `mes`, `can_bus`, `concurrency`, `memory_management`, `performance_optimization`, `scripting`, `infrastructure_as_code`, `system_integration`, `process_quality_assurance`. (Đề xuất và file quyết định đều có 40 mã mới.)

### Khóa trùng giữa mã cũ và mã mới

`load_vocabulary` ném `ValueError` khi một khóa đã bỏ dấu thuộc hai mã. Ba khóa trùng làm `load_vocabulary` lỗi (ba dòng đầu), thêm một khóa phải đi theo để AC2 đúng. Xử lý theo hướng "mã mới giữ khóa" để một kỹ năng không tách thành hai mã:

| Khóa (bỏ dấu) | Mã cũ giữ | Mã mới cần | Xử lý |
|---|---|---|---|
| `can bus` | `protocols_hw` (bí danh) | `can_bus` (tên Anh "CAN bus") | bỏ khỏi `protocols_hw`; `can/lin`, `uart`, `modbus`… vẫn ở `protocols_hw` |
| `infrastructure as code` | `terraform` (bí danh) | `infrastructure_as_code` (tên Anh) | bỏ khỏi `terraform`; tên `terraform` vẫn ra `terraform` |
| `tu duy phan tich` | `problem_solving` (bí danh) | `analytical_thinking` (tên Việt "Tư duy phân tích") | bỏ khỏi `problem_solving` |
| `tu duy logic` | `problem_solving` (bí danh) | không đụng tên, nhưng `logical thinking` (thẻ 20 tin) đã vào `analytical_thinking` | chuyển sang `analytical_thinking`, nếu không "logical thinking" và "tư duy logic" là hai mã (AC2). Khóa này không có trong quyết định đã duyệt; đây là chỗ lệch thêm |

Hệ quả: JD có chữ "infrastructure as code", "can bus" hay "tư duy phân tích" nay ra mã mới thay vì mã cũ; ba mã cũ (`terraform`, `protocols_hw`, `problem_solving`) còn nguyên và vẫn tra được bằng các tên và bí danh còn lại.

## `haido_core/vocab/skills_excluded.json` (mới)

```json
{
  "version": "excluded-2026-11-23",
  "snapshot": "2026-11-20",
  "note": "…",
  "entries": [
    {"key": "ha noi", "spelling": "Hà Nội", "reason": "địa điểm, không phải kỹ năng", "postings": 1426}
  ]
}
```

| Trường | Ý nghĩa |
|---|---|
| `version` | bắt đầu `excluded-`; đổi khi danh sách đổi |
| `snapshot` | snapshot mà số tin lấy ra |
| `entries[].key` | dạng đã bỏ dấu (`fold`), cùng dạng khóa của `lookup`; không trùng, và không được là khóa của `lookup` hay `composites` |
| `entries[].spelling` | cách viết thường gặp nhất, để người đọc |
| `entries[].reason` | không rỗng |
| `entries[].postings` | số tin nhắc thẻ, từ 20 trở lên, là bằng chứng thẻ đủ hay gặp để cần lý do |

158 dòng, xếp theo số tin giảm dần. Nhóm lý do: địa điểm (81), chức danh (21), thẻ ngành nghề hoặc danh mục của site (20), thẻ "Việc làm … tại …" của TopCV (13), quá chung (9 + 2 + 1 + 1 + 1), chỉ một nguồn gắn (4), và các lý do đơn lẻ khác (5).

Loader: `haido_core.vocab.skills.load_exclusions()` (cache), `parse_exclusions(doc, vocab)` (hàm thuần, test được), kiểu `ExcludedSkill`, `ExclusionList`.

## `web/tests/fixtures/skills.json`

Fixture của `GET /api/v1/skills` (#207): cập nhật theo từ vựng mới (`vocab_version`, thêm 40 mã). Không đổi hình dạng response.
