# Từ vựng kỹ năng

Từ vựng ánh xạ chuỗi kỹ năng (thẻ của site, lượt nhắc trong JD) sang mã kỹ năng. Nó là dữ liệu có phiên bản, không phải code: `haido_core/vocab/skills_seed.json` (bản mồi, #205, #283, #278) và `haido_core/vocab/skills_excluded.json` (danh sách loại trừ, #278). Bộ từ vựng v1 có giảng viên duyệt (#96) sẽ thay bản mồi; mã giữ định dạng `snake_case`.

## Từ vựng lớn lên thế nào

1. Chạy `tools/vocab/skill_gaps.py` trên snapshot mới nhất (xem bên dưới). Kết quả liệt kê các thẻ kỹ năng thô có từ 20 tin, mã hiện hành của từng thẻ (hoặc `null`), vài cách viết hay gặp và nguồn.
2. Với mỗi thẻ chưa có mã, người duyệt chọn một trong bốn việc: `new` (mã mới), `alias` (thêm làm cách viết của mã có sẵn), `composite` (một thẻ là hai kỹ năng, như `Agile/Scrum`), `exclude` (không phải kỹ năng, kèm lý do). Bản duyệt của #278 nằm ở `specs/278-ma-ky-nang-thuong-gap/` (`de-xuat-tu-vung.md`, `quyet-dinh-2026-11-20.json`).
3. Sửa `skills_seed.json`: mỗi mã có tên Anh, tên Việt, bí danh (cả Anh và Việt) và `source`. Mã xếp theo thứ tự chữ cái, không trùng. **Một khóa (tên hay bí danh, sau khi bỏ dấu và hạ chữ thường) chỉ thuộc một mã**: `load_vocabulary` ném `ValueError` nếu không. Khi mã mới cần một khóa mà mã cũ đang giữ, chuyển khóa về mã mới và ghi lại ở spec của issue.
4. **Đổi `version`** của file. Phiên bản từ vựng là khóa để `ingest` quét lại tin trong cửa sổ (`job_posting_facts.vocab_version`, #283), nên thêm mã mà quên đổi phiên bản thì tin cũ không được gán mã mới.
5. Không xóa hay đổi tên mã đã có: hồ sơ người dùng đã lưu các mã đó. Test `test_gh278_225_ma_cu_van_con` giữ danh sách.
6. Ánh xạ chỉ tra bảng, không gọi mô hình và không cần mạng (phép 1, #97). Chạy lại ánh xạ khi đổi từ vựng là chạy lại `ingest`, không phải gọi mô hình.

## Danh sách loại trừ

`skills_excluded.json` liệt kê thẻ hay gặp (từ 20 tin) mà **cố ý** không có mã: địa điểm, chức danh, thẻ ngành nghề hay danh mục của site, chữ quá chung (`Software Engineering`, `Thiết kế`). Mỗi dòng:

| Trường | Ý nghĩa |
|---|---|
| `key` | khóa đã bỏ dấu (cùng dạng với khóa của từ vựng) |
| `spelling` | cách viết hay gặp nhất |
| `reason` | lý do, không rỗng |
| `postings` | số tin nhắc thẻ ở snapshot nguồn (bằng chứng) |

`load_exclusions()` (qua `parse_exclusions`) ném lỗi khi:

- gốc file không phải object, `version` không bắt đầu bằng `excluded-`, thiếu `snapshot`, hoặc `entries` thiếu hay rỗng;
- một dòng không phải object;
- `key` rỗng hoặc chưa bỏ dấu (khác `fold(key)`);
- thiếu `reason` (rỗng hay chỉ có khoảng trắng cũng tính là thiếu);
- thiếu `spelling` (cách viết gốc);
- `postings` thiếu, không phải số nguyên, hoặc nhỏ hơn 1;
- hai dòng cùng `key`;
- `key` cũng là khóa của `lookup` hoặc `composites` của từ vựng (vừa loại trừ vừa có mã).

 Thẻ đã loại trừ vẫn tính trong mẫu số của tỷ lệ "lượt nhắc có mã" (tỷ lệ không bao giờ đạt 100%, và đó là chủ ý). Khi lý do không còn đúng (ví dụ nguồn thứ hai bắt đầu gắn thẻ đó), gỡ dòng khỏi danh sách và thêm vào từ vựng.

## `scan_skip`

Danh sách `scan_skip` trong `skills_seed.json` là các khóa **tra được nhưng không được quét** trong văn bản JD, vì chữ đó quá chung khi đứng riêng (`c`, `r`, `go`, `cloud`, `api`, `monitoring`, `windows`, `rest`, `word`). Chúng vẫn nằm trong `Vocabulary.lookup`, nên thẻ kỹ năng của site (`API`, `Cloud`) vẫn ra mã; chỉ `Vocabulary.scan_terms` bỏ chúng. `scan_skip` áp dụng cho mọi khóa của `lookup`, kể cả tên Anh và tên Việt, không chỉ bí danh: `khoa hoc du lieu` và `tri tue nhan tao` (tên Việt của `data_science`, `artificial_intelligence`) nằm trong `scan_skip` vì chúng khớp danh sách chuyên ngành ("tốt nghiệp chuyên ngành Khoa học dữ liệu, Trí tuệ nhân tạo"). Cùng lý do cho các chữ chung của JD: `bao mat`, `lap ke hoach`, `phan quyen`, `wifi`, `wi-fi`, `it infrastructure`, `it operations`, `it support`, `presentation`. Mã ghép (`composites`) luôn được quét; mỗi phần của nó phải nằm nguyên văn trong cụm đã bỏ dấu (`ai/ml` gồm `ai` và `ml`), nếu không `load_vocabulary` ném `ValueError` vì lượt nhắc không neo được vị trí. Thêm một từ chung vào bí danh mà không thêm vào `scan_skip` sẽ làm số tin nhắc kỹ năng đó phồng lên.

## Chạy `skill_gaps.py`

Script chỉ đọc (hai engine đều chỉ-đọc, mọi câu SQL là SELECT), không in thông tin đăng nhập, không đọc văn bản JD. Nó lấy snapshot đọc được mới nhất (`published` hoặc `partial`), mọi tin IT của nguồn không bị loại trong cửa sổ `window_days`, ghép thẻ `skills` và `skills_raw` của bảng `jobs`, và in JSON: `skills` (mỗi khóa một dòng với số tin, mã hiện hành, cách viết, nguồn), `roles` (theo vai trò: tin, lượt nhắc, lượt có mã, tỷ lệ), `meta`.

Trên VPS, qua container API đã deploy:

```bash
ssh <vps> 'docker exec -i haido-prod-api-1 python -' < tools/vocab/skill_gaps.py > skill_gaps.json
```

Ở máy dev (cần URL của kho và của bảng scraper):

```bash
HAIDO_DATABASE_URL=... HAIDO_SCRAPER_DATABASE_URL=... uv run python tools/vocab/skill_gaps.py
```

### Đo lại ngoại tuyến

```bash
uv run python tools/vocab/skill_gaps.py --after skill_gaps.json [--min-postings 20]
```

`--after` đọc đúng đầu ra thô của script (mỗi khóa có `code`, vai trò ở `roles`) và chỉ giữ khóa có từ `--min-postings` tin (mặc định 20, ngưỡng của #278; đầu ra thô có đủ mọi khóa, kể cả khóa 1 tin). Số "trước" lấy từ `code` của file; số "sau" tra lại với từ vựng hiện hành.

File `specs/278-ma-ky-nang-thuong-gap/gaps-2026-11-20.json` suy ra từ đầu ra thô của lần chạy trên prod như sau: giữ các khóa có từ 20 tin, đổi tên `code` thành `code_before` và `roles` thành `roles_before` (để một lần chạy sau không lẫn với số "sau"). `--after` cũng đọc dạng đã lọc này (`code_before`, `roles_before`).

Tra lại từng khóa của file `skills` với từ vựng hiện hành và in số khóa có mã trước/sau, số khóa đã loại trừ, các khóa **chưa có mã mà cũng chưa loại trừ** (`keys_unresolved`; phải rỗng), và tỷ lệ lượt nhắc thẻ có mã. Tỷ lệ theo vai trò không tính lại được từ file này vì file chỉ có tổng theo khóa: muốn số "sau" theo vai trò thì deploy rồi chạy lại script trên prod.

## Tỷ lệ lượt nhắc kỹ năng có mã (#278)

Snapshot 2026-11-20, 4.688 tin IT, từ vựng `seed-2026-11-13` (225 mã). Mẫu số: mọi lượt nhắc thẻ thô (mỗi tin một lượt cho mỗi khóa), gồm cả thẻ địa điểm và danh mục.

| Vai trò | Tin | Lượt nhắc | Có mã (trước) | Tỷ lệ trước | Tỷ lệ sau |
|---|---:|---:|---:|---:|---|
| AI/ML Engineer | 213 | 5.745 | 1.669 | 29,1% | đo sau deploy |
| BA/PO/PM | 992 | 20.646 | 3.912 | 18,9% | đo sau deploy |
| Backend | 556 | 12.626 | 5.563 | 44,1% | đo sau deploy |
| Data Analyst/BI | 183 | 2.914 | 865 | 29,7% | đo sau deploy |
| Data Engineer | 179 | 3.876 | 1.284 | 33,1% | đo sau deploy |
| Data Scientist | 34 | 679 | 232 | 34,2% | đo sau deploy |
| DevOps | 273 | 7.349 | 3.027 | 41,2% | đo sau deploy |
| Embedded | 110 | 2.518 | 549 | 21,8% | đo sau deploy |
| Frontend | 87 | 1.848 | 816 | 44,2% | đo sau deploy |
| Fullstack | 217 | 6.020 | 2.629 | 43,7% | đo sau deploy |
| Game | 114 | 2.078 | 387 | 18,6% | đo sau deploy |
| Hạ tầng/IT support | 648 | 15.310 | 2.903 | 19,0% | đo sau deploy |
| Mobile | 106 | 2.600 | 719 | 27,7% | đo sau deploy |
| Other | 280 | 4.659 | 1.303 | 28,0% | đo sau deploy |
| QA/Tester | 373 | 7.736 | 2.349 | 30,4% | đo sau deploy |
| Security | 234 | 4.903 | 1.399 | 28,5% | đo sau deploy |
| UI/UX | 89 | 2.787 | 432 | 15,5% | đo sau deploy |
| **Tổng** | 4.688 | 104.294 | 30.038 | 28,8% | đo sau deploy |

Ở mức khóa (673 khóa từ 20 tin, 47.444 lượt nhắc), tính ngoại tuyến với `seed-2026-11-23` (265 mã):

| | Trước | Sau |
|---|---:|---:|
| Khóa có mã | 369 | 515 |
| Khóa trong danh sách loại trừ | 0 | 158 |
| Khóa chưa có mã, chưa loại trừ | 304 | 0 |
| Lượt nhắc thẻ của các khóa này có mã | 26.750 (56,4%) | 32.802 (69,1%) |
