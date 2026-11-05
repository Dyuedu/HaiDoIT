---
title: "Đề xuất đổi sprint: lát cắt Bản đồ chạy thật cuối Sprint 1"
created: 2026-11-05
status: approved-tentative
scope: moderate
proposer: GiapPhanQuang
affects:
  - _bmad-output/planning-artifacts/epics.md
  - _bmad-output/planning-artifacts/prds/prd-HaiDoIT-2026-11-02/prd.md
  - _bmad-output/planning-artifacts/briefs/brief-HaiDoIT-2026-11-02/brief.md
  - _bmad-output/planning-artifacts/architecture/architecture-HaiDoIT-2026-11-03/ARCHITECTURE-SPINE.md
  - _bmad-output/planning-artifacts/architecture/architecture-HaiDoIT-2026-11-03/WORK-SPLIT.md
  - _bmad-output/planning-artifacts/ux-designs/ux-HaiDoIT-2026-11-03/EXPERIENCE.md
  - _bmad-output/implementation-artifacts/sprint-status.yaml
  - _bmad-output/implementation-artifacts/spec-gh-2-chot-envelope-meta-endpoint-du-lieu-gia.md
  - GitHub Issues Dyuedu/HaiDoIT
---

# Đề xuất đổi sprint: lát cắt Bản đồ chạy thật cuối Sprint 1

> **Trạng thái:** GiapPhanQuang duyệt tạm ngày 05/11/2026, **chờ Dyuedu và CaoPhanTuanAnh đồng ý**. Các tài liệu ở mục 4.3–4.7 đã được sửa trên nhánh `docs/sprint-change-2026-11-05` để mọi người kéo về xem. GitHub Issues và code `scraper/` **chưa sửa**; chỉ sửa sau khi cả nhóm thống nhất. Góp ý xin ghi thẳng vào file này hoặc nhắn trong nhóm.

## Tóm tắt

- **Yêu cầu mới:** cuối Sprint 1 (Chủ nhật 08/11) phải có **một user story chạy thật, đạt đủ AC và DoD**. Kế hoạch hiện tại không có story nào như vậy: màn hình đầu tiên có số là Sprint 2, và Bản đồ là Sprint 5.
- **Đề xuất:** làm **Story 1.15 "Xem tỷ trọng ba thành phố"** (bảng và biểu đồ 2D, chưa 3D) trên dữ liệu thu thật từ 05/11. Để kịp, tách hai story mới khỏi 1.9 và 1.13 để chuỗi phụ thuộc không phải đi qua LLM, và thêm một chore cầu nối tạm từ crawler cũ vào kho.
- **Đổi lại:** phần còn lại của 1.2, 1.3, cùng 2.2 và 1.19 dời sang Sprint 2. Sprint 5 nhẹ bớt vì 1.15 đã xong. MVP và PRD không đổi phạm vi.
- **Cập nhật thực tế:** từ 04/11, crawler ITviec, TopDev và VietnamWorks đã dùng User-Agent trung thực. Rủi ro R2 trong PRD và AD-16 trong spine đang mô tả code cũ.

## 1. Vấn đề

**Lý do đổi:** yêu cầu mới, không phải lỗi kỹ thuật. Không story nào đã làm bị ảnh hưởng, vì hiện chưa story nào bắt đầu.

**Kế hoạch hiện tại không đáp ứng được, vì:**

- Cổng ra Sprint 1 (mô tả milestone) chỉ có việc nằm dưới màn hình: thu thập hằng ngày, envelope `meta`, `REGISTRY.md`, CI, sao lưu. Các story Sprint 1 có giao diện là 1.1 (khung app, chưa có số), 5.1 (trang tĩnh) và 2.2 (mới làm phần `localStorage`).
- Story 1.15 (#46) ở Sprint 5. Chuỗi chặn chính thức của nó đi qua LLM: #46 ← #27 (1.13) ← #17 (1.11, tỷ lệ kỹ năng) ← #16 (1.9) ← #14 (1.7, mapping kỹ năng). Nguyên nhân là 1.13 gộp tỷ trọng thành phố với tỷ lệ kỹ năng, và 1.9 gộp vai trò, thành phố với nhánh (nhánh cần tập kỹ năng).
- App mở vào Bản đồ, nhưng Bản đồ không có số cho tới Sprint 5. Ở review giữa kỳ (22–28/11), màn đầu tiên hội đồng thấy sẽ trống.

**Bằng chứng khả thi (kiểm ngày 05/11):**

- `robots.txt` của CareerLink, ITNavi, ITviec và TopDev cho phép mọi đường dẫn crawler dùng. Zalo Careers, MoMo Careers và API VietnamWorks không có `robots.txt`.
- Sau commit `1a8e3f6`, ITviec, TopDev và MoMo dùng `browser_polite` (UA trung thực, không giấu dấu hiệu tự động). VietnamWorks dùng `PoliteClient`. Chỉ LinkedIn (đã tắt) và TopCV (chạy tay) còn dùng kỹ thuật né phát hiện bot. Commit `10d4c73` đã xóa step-03.
- Lượt crawl raw VietnamWorks và TopDev **đã bắt đầu ngày 05/11**, ghi vào `scraper/data/raw/2026-11-05/` (nằm trong `.gitignore`).
- Tỷ trọng thành phố chỉ cần vai trò, cấp bậc và thành phố của tin. Ba nhãn này gán được bằng luật tất định, không cần LLM hay bộ từ vựng.

**Vấn đề phát hiện thêm, cần sửa:**

- User-Agent hiện là `HaiDoIT-research-bot/0.1 (non-commercial student research)`, **thiếu địa chỉ liên hệ** mà FR-2, AC của 1.2 và AC của 5.1 yêu cầu. Lượt crawl 05/11 vẫn chạy với UA này (đã quyết ngày 05/11); từ lượt sau phải có email của nhóm.
- Crawler dùng trình duyệt (TopDev, ITviec, MoMo) không kiểm `robots.txt` qua cổng `polite`, nên chưa đạt FR-2 bằng code. Hôm nay đúng là được phép, nhưng đó là do kiểm tay.
- `scraper/pipeline.py` gọi CareerLink với `--force --delay 5`, tức bỏ qua khoảng cách 1 giờ mà README tự đặt.

## 2. Phân tích ảnh hưởng

### 2.1 Epic

| Epic | Ảnh hưởng |
|---|---|
| Epic 1 | Đổi thứ tự: 1.15 từ Sprint 5 lên Sprint 1. Thêm hai story 1.20 và 1.21. 1.9 và 1.13 hẹp phạm vi lại. 1.2 và 1.3 dời sang Sprint 2 |
| Epic 2 | 2.2 dời hẳn sang Sprint 2. Không đổi AC |
| Epic 3–6 | Không đổi |

Không epic nào bị bỏ hay phải thêm mới. Mọi epic vẫn hoàn thành được.

### 2.2 Story

| Story | Hiện tại | Đề xuất |
|---|---|---|
| 1.1 (#1) | P0 · S1 | Giữ. Khung Python do #2 dựng (đã chốt trong spec #2); #1 lo `web/`, `deploy/`, Alembic, CI |
| 1.2 (#4) | P0 · S1 | P0 · **S2**. Sprint 1 thu thập qua cầu nối C-11 |
| 1.3 (#5) | P0 · S1 | P0 · **S2**. Bước `redact` làm trong C-11 rồi 1.3 dùng lại |
| 1.4 (#6) | P0 · S1 | Giữ S1 |
| 1.9 (#16) | gồm vai trò, cấp bậc, thành phố, nhánh | Chỉ còn **nhánh** và đo độ chính xác trên 200 JD. Vai trò, cấp bậc, thành phố chuyển sang 1.20 |
| 1.13 (#27) | gồm tỷ trọng thành phố và tỷ lệ kỹ năng | Chỉ còn **tỷ lệ kỹ năng**. Tỷ trọng thành phố chuyển sang 1.21 |
| 1.15 (#46) | P1 · S5 · chặn bởi #27 | **P0 · S1** · chặn bởi 1.21. Nút 3D có mặt nhưng tắt tới khi 1.17 xong |
| 1.19 (#10) | P1 · S1 | P1 · **S2**. Sprint 1 vẫn chạy `pg_dump` một lần (cổng ra sprint) |
| 2.2 (#7) | P0 · S1–S2 | P0 · **S2** |
| 5.1 (#11) | P1 · S1 | Giữ S1, **là việc cắt đầu tiên** nếu trượt |
| **1.20 mới** | — | P0 · S1: gán vai trò, cấp bậc, thành phố bằng luật tất định |
| **1.21 mới** | — | P0 · S1: tính và đọc tỷ trọng thành phố kèm cỡ mẫu |
| **C-11 mới** | — | P0 · S1 · `khong-duoc-cat`: cầu nối tạm từ crawler cũ vào kho |

### 2.3 Tài liệu bị ảnh hưởng

| Tài liệu | Cần sửa | Lý do |
|---|---|---|
| PRD §6.1 và brief, mục Rủi ro | Dòng R2 | Mô tả crawler đã được viết lại |
| Spine AD-16 | Danh sách nguồn tự động; ngoại lệ có hạn của C-11 | "4 nguồn tự động" đã cũ; C-11 tạm ghi file |
| Spine AD-20 | Crawler dùng trình duyệt phải kiểm `robots.txt` qua cổng | Lỗ hổng mới phát hiện |
| Spine AD-28 | Nhịp một ở Sprint 1 chạy qua C-11 | Cách chạy thật trong Sprint 1 |
| WORK-SPLIT §3, §4 | Bảng Sprint 1, Sprint 2, Sprint 5; đường găng | Thứ tự mới |
| EXPERIENCE, State Patterns | Lối mở Bản đồ khi chưa có 3D | Lối mặc định là 3D |
| `epics.md` | Hai story mới, năm story sửa, bảng thứ tự thực hiện | Thứ tự mới |
| `sprint-status.yaml` | Thêm `1-20`, `1-21` | Story mới |
| Spec #2 | `MarketReadModel` chọn nguồn theo từng phép | Ở Sprint 1, `city_shares` đọc dữ liệu thật trong khi `skill_rates` vẫn là bản giả |

PRD không ghi lịch sprint, nên **FR và MVP không đổi**. DoD không đổi.

### 2.4 Kỹ thuật

- **Không có VPS trong Sprint 1.** Lịch crawl hằng ngày chạy trên máy của một thành viên (Task Scheduler của Windows), và máy đó phải bật vào giờ chạy.
- **File thô có thể chứa liên hệ người đăng tin.** FR-5 và AD-21 yêu cầu xóa trước khi lưu, nên file thô bị xóa ngay sau khi `ingest` thành công.
- **Nợ tạm, phải ghi rõ:**
  - Chưa bỏ trùng trong nguồn theo nội dung (1.5) và chưa gom trùng chéo nguồn (1.8). Mỗi tin tạm là một cụm riêng, nên một tin đăng trên hai sàn bị đếm hai lần.
  - Luật gán vai trò chưa đo độ chính xác; việc đo thuộc 1.9 ở Sprint 2.
  - Crawler cũ bỏ qua tin đã lấy ở lần chạy trước. C-11 ghi mỗi ngày vào thư mục riêng để mỗi lượt đều thấy đủ tin.

## 3. Hướng đi đề xuất

| Phương án | Khả thi | Công | Rủi ro | Ghi chú |
|---|---|---|---|---|
| 1. Điều chỉnh trực tiếp | **Có** | Trung bình | Trung bình–cao | Tách story, đổi thứ tự, thêm cầu nối |
| 2. Quay lui | Không áp dụng | — | — | Chưa story nào xong |
| 3. Xem lại MVP | Không cần | — | — | FR-1..FR-48 giữ nguyên |

**Chọn phương án 1.** Lý do:

- 1.15 là story có số liệu duy nhất mà toàn bộ AC làm được không cần LLM, bộ từ vựng hay đồ thị học trước.
- Hai story mới không phải đồ bỏ đi: luật gán nhãn của 1.20 là phép 6 của registry, 1.9 sẽ mở rộng tiếp; endpoint của 1.21 là đúng route và schema mà #27 dùng.
- Nhịp một được bật thật từ 05/11. Đây là việc spine yêu cầu không được hoãn, vì mỗi ngày không thu là mất một snapshot.
- Review giữa kỳ có thêm một màn chạy trên số thật.

**Công ước tính cho Sprint 1:** khoảng 9–10 ngày công, trong khi nhóm có 12 (3 người × 4 ngày, 05–08/11). Kế hoạch dùng gần hết năng lực, nên không còn chỗ cho việc phát sinh.

**Rủi ro và cách giảm:**

| Rủi ro | Cách giảm |
|---|---|
| #1 chưa bắt đầu (05/11 chưa có nhánh), mọi việc khác chờ nó | #1 làm phần khung web và Compose trước, xong trong thứ Năm |
| Máy dev chưa có Docker hoặc Postgres 18 | Kiểm ngay sáng 06/11; nếu thiếu thì dùng Postgres cài thẳng trên máy |
| Luật gán vai trò sai nhiều | Bản đồ mặc định "Tất cả" (đúng AC); danh sách vai trò lọc hiện ít vai trò nhất có thể |
| Tin trùng chéo nguồn làm phình tỷ trọng | Ghi nợ tạm; 1.8 ở Sprint 3 xử lý |
| Không đủ thời gian rà soát chéo vào Chủ nhật | Rà soát cuốn chiếu từ thứ Bảy, mỗi PR nhỏ |

**Ảnh hưởng tới lịch:**

- Sprint 2 nhận thêm khoảng 3 ngày công: phần còn lại của 1.2, 1.3, cùng 2.2 và phục hồi thử của 1.19.
- Sprint 5 bớt khoảng 1,5 ngày công vì 1.15 đã xong.
- WORK-SPLIT §6 đã khuyên mượn thời gian từ Sprint 5 cho Sprint 2. Đề xuất này đi đúng hướng đó.

**Nếu trượt:** 1.1 và 5.1 vẫn đạt đủ AC, nhưng cả hai không có số liệu. 1.15 khi đó hoàn tất trong hai ngày đầu Sprint 2.

## 4. Thay đổi cụ thể

### 4.1 Story mới trong `epics.md`, Epic 1

```markdown
### Story 1.20: Gán vai trò, cấp bậc và thành phố bằng luật tất định

**Mức ưu tiên:** P0 — Sprint 1

As a sinh viên,
I want mỗi tin có một vai trò, một cấp bậc và một thành phố ngay từ tuần đầu,
So that bản đồ lọc được theo vai trò và không tính tin ngoài ngành IT.

**Acceptance Criteria:**

**Given** một tin đã nạp vào kho
**When** phép phân loại chạy
**Then** tin có đúng một vai trò trong danh sách của cấu hình hoặc nhãn "không thuộc IT", đúng một cấp bậc, và đúng một thành phố: Hà Nội, TP.HCM, Đà Nẵng, Khác, hoặc không xác định
**And** phép là hàm thuần trong `domain`, là phép 6 của registry, gọi được cho một tin và cho một lô. Cùng đầu vào luôn cho cùng nhãn
**And** luật chỉ đọc chức danh, nguồn, danh mục của nguồn, cấp bậc và địa điểm nguồn ghi. Không gọi mô hình
**And** Data/AI tách thành Data Analyst/BI, Data Engineer và AI/ML Engineer. Embedded không nằm trong Other
**And** tin ghi nhiều thành phố được gán theo một quy tắc viết rõ trong cấu hình, có kiểm thử
**And** tin không thuộc IT được gắn nhãn và bị loại khỏi mọi bảng tổng hợp. Tỷ lệ loại báo cáo được theo nguồn
```

```markdown
### Story 1.21: Tính và đọc tỷ trọng thành phố kèm cỡ mẫu

**Mức ưu tiên:** P0 — Sprint 1

As a sinh viên,
I want số tỷ trọng thành phố đến từ snapshot thật, kèm cỡ mẫu, nguồn và ngày,
So that màn Bản đồ không phải tự tính, và mẫu nhỏ được đánh dấu đúng.

**Acceptance Criteria:**

**Given** một snapshot đã nạp và đã phân loại
**When** bước tổng hợp chạy
**Then** có một ô thống kê cho mỗi thành phố × vai trò và một ô toàn quốc cho mỗi vai trò, kể cả "Tất cả". Mỗi ô có n và cơ cấu cấp bậc
**And** bước tổng hợp đếm cụm, không đếm bản ghi thô. Cho tới khi có Story 1.5 và 1.8, mỗi tin là một cụm của riêng nó
**And** với mỗi vai trò, tỷ trọng ba thành phố cộng phần Khác và phần không xác định bằng 100%
**When** client gọi `GET /api/v1/city-shares?role=`
**Then** thân phản hồi theo envelope của AD-17, đọc snapshot mới nhất còn đọc được, và route cùng schema giữ nguyên như bản dữ liệu giả của C-1
**And** `haido_api` không chạy `GROUP BY`, `COUNT` hay `AVG` trên bảng `job_*`
```

### 4.2 Chore mới trên GitHub (không có story trong `epics.md`, theo quy ước của BACKLOG)

```markdown
[C-11] Cầu nối tạm: crawler cũ ghi theo ngày, rồi nạp vào kho

| Mức ưu tiên | P0 | Sprint | Sprint 1 | Loại | chore | Label | khong-duoc-cat |
| Chặn bởi | #1 (1.1) |

## Acceptance Criteria
**Given** các crawler trong `scraper/` và lịch chạy hằng ngày
**When** lượt chạy của một ngày kết thúc
**Then** mỗi nguồn đang bật có file JSONL trong `scraper/data/raw/<YYYY-MM-DD>/`, và nguồn lỗi không làm dừng nguồn khác
**And** bước `ingest` đọc các file đó, xóa tên, email, số điện thoại và Zalo của người đăng tin, rồi ghi `job_postings` và `job_observations` kèm `snapshot_id`, `source`, `pipeline_run_id`. Quan sát chỉ được thêm
**And** không bản ghi nào trong kho khớp mẫu email hoặc số điện thoại Việt Nam
**And** file thô bị xóa ngay sau khi `ingest` thành công
**And** User-Agent có email liên hệ của nhóm

## Task
- [ ] Thêm email liên hệ vào `USER_AGENT` trong `scraper/crawlers/polite.py`
- [ ] Lịch chạy hằng ngày; mỗi nguồn ghi vào thư mục của ngày, không ghi đè ngày cũ
- [ ] Bước `redact` (Story 1.3 dùng lại) và bước `ingest` đọc JSONL
- [ ] Nạp lại lượt 05/11 với `snapshot_id = 2026-11-05`
- [ ] Gỡ cầu nối khi Story 1.3 xong

Nguồn bật trong Sprint 1: VietnamWorks, TopDev (từ 05/11); sau đó ITNavi, Zalo Careers, MoMo Careers, CareerLink. ITviec chờ thư đồng ý (R4). TopCV chạy tay. LinkedIn tắt.
```

### 4.3 Story sửa trong `epics.md`

**Story 1.15, Mức ưu tiên**

```
OLD: **Mức ưu tiên:** P1 — Sprint 5
NEW: **Mức ưu tiên:** P0 — Sprint 1
```

**Story 1.15, Acceptance Criteria**

```
OLD: **And** cụm 3D / 2D / bảng cao tối thiểu 44px. Vòng focus dày 2px, màu `#C5F36A`, lệch 2px
NEW: **And** cụm 3D / 2D / bảng cao tối thiểu 44px. Vòng focus dày 2px, màu `#C5F36A`, lệch 2px
     **And** khi Story 1.17 chưa xong, Bản đồ mở ở lối 2D. Nút 3D có mặt ở trạng thái tắt, có `aria-disabled` và chú thích "Bản đồ 3D sắp có"
```

Lý do: 3D là Story 1.17 riêng. 1.15 không nên phụ thuộc vào nó.

**Story 1.13, Acceptance Criteria**

```
OLD: **When** client gọi API tỷ trọng thành phố hoặc tỷ lệ kỹ năng
NEW: **When** client gọi API tỷ lệ kỹ năng
     ...
     **And** endpoint tỷ trọng thành phố của Story 1.21 qua cùng kiểm thử schema
```

**Story 1.9, Acceptance Criteria**

```
OLD: **Given** một tin đã có cụm
     **When** phép phân loại chạy
     **Then** tin có một vai trò, một cấp bậc, một thành phố, và một nhánh nếu đủ điều kiện
     **And** nhánh chỉ xuất hiện khi có từ 30 tin. Ngưỡng này đọc từ cấu hình
     **And** Data/AI tách thành Data Analyst/BI, Data Engineer và AI/ML Engineer. Embedded không nằm trong Other
     **And** tin không thuộc IT được gắn nhãn và bị loại khỏi mọi bảng tổng hợp. Tỷ lệ loại báo cáo được theo nguồn
     **And** có cách chấm độ chính xác vai trò trên bộ fixture 200 JD
NEW: **Given** một tin đã có cụm, và đã có vai trò, cấp bậc, thành phố từ Story 1.20
     **When** phép phân loại chạy
     **Then** tin có thêm một nhánh nếu đủ điều kiện
     **And** nhánh chỉ xuất hiện khi có từ 30 tin. Ngưỡng này đọc từ cấu hình
     **And** có cách chấm độ chính xác vai trò, cấp bậc và nhánh trên bộ fixture 200 JD
```

**Story 1.2 và 1.3, Mức ưu tiên**

```
OLD: **Mức ưu tiên:** P0 — Sprint 1
NEW: **Mức ưu tiên:** P0 — Sprint 2. Trong Sprint 1, nhịp một chạy qua cầu nối C-11
```

Thêm vào AC của 1.2: `**And** crawler dùng trình duyệt cũng hỏi cổng trước mỗi lần mở trang, nên URL bị robots.txt cấm không bị mở`.

**Story 2.2 (P0 — Sprint 2) và 1.19 (P1 — Sprint 2):** chỉ đổi dòng mức ưu tiên.

**Mục "Mức ưu tiên và thứ tự thực hiện"**

```
OLD: | 1 (2–8/11) | 1.1, 1.2, 1.3, 1.4, 2.2 (phần `localStorage`) |
     | 2 (9–15/11) | 1.5, 1.6, 1.7, 1.9, 1.11, 1.14, 2.1, 2.6, 2.9, 2.10, 2.11 |
NEW: | 1 (2–8/11) | 1.1, 1.4, 1.20, 1.21, 1.15 |
     | 2 (9–15/11) | 1.2, 1.3, 1.5, 1.6, 1.7, 1.9, 1.11, 1.14, 2.1, 2.2, 2.6, 2.9, 2.10, 2.11 |

OLD: Story P1 theo sprint: Sprint 1 — 1.19, 5.1. … Sprint 5 — 1.15, 1.16, 1.17, 5.2–5.5.
NEW: Story P1 theo sprint: Sprint 1 — 5.1. Sprint 2 — 1.19. … Sprint 5 — 1.16, 1.17, 5.2–5.5.

OLD: - **Story 1.15, 1.16, 1.17 (bản đồ 3D) đứng sau cả Epic 2.** …
NEW: - **Story 1.15 (bảng và 2D) ở Sprint 1, là lát cắt chạy thật đầu tiên. Story 1.16 và 1.17 vẫn ở Sprint 5**, vì 1.16 cần tỷ lệ kỹ năng.

OLD: Không được cắt dù trượt, theo `WORK-SPLIT.md` §5: nhịp một hằng ngày (1.2–1.4), …
NEW: Không được cắt dù trượt, theo `WORK-SPLIT.md` §5: nhịp một hằng ngày (C-11 ở Sprint 1, rồi 1.2–1.4), …
```

### 4.4 PRD §6.1 và brief, mục Rủi ro đã chấp nhận

```
OLD: | R2 | Các crawler và bước pipeline kế thừa khác dùng cùng kỹ thuật né phát hiện bot: crawler ITviec, crawler TopDev, và bước lấy mô tả đầy đủ (step-03) | Như R1 | **Rất cao** |
NEW: | R2 | Dữ liệu nền của ITviec và TopDev, cùng bước lấy mô tả đầy đủ (step-03), từng được thu bằng kỹ thuật né phát hiện bot. Từ 04/11/2026 (commit `1a8e3f6`, `10d4c73`), hai crawler này dùng User-Agent trung thực và step-03 đã bị xóa | Chỉ còn áp cho dữ liệu nền. Lượt thu mới không thuộc R2 | **Rất cao** với dữ liệu nền |
```

R4 không đổi: ITviec vẫn chờ thư đồng ý dù crawler đã trung thực.

### 4.5 Spine và WORK-SPLIT

**AD-16, thêm vào Rule:**

```
- Từ 04/11/2026 có sáu nguồn tự động dùng User-Agent trung thực: CareerLink, ITNavi, Zalo Careers, MoMo Careers, VietnamWorks, TopDev. ITviec cũng chạy tự động được, nhưng chờ thư đồng ý (R4).
- Sprint 1 chạy nhịp một qua cầu nối tạm C-11: crawler cũ ghi JSONL theo ngày, rồi bước `ingest` đọc vào. Đây là ngoại lệ có hạn của câu "không ghi file", hết hạn khi Story 1.3 xong. File thô bị xóa ngay sau khi `ingest` thành công (AD-21).
```

**AD-20, thêm vào Rule:**

```
Crawler dùng trình duyệt (TopDev, ITviec, MoMo) phải hỏi `PoliteClient.allowed()` trước mỗi lần mở trang. Hiện chúng chưa làm việc này.
```

**AD-28, thêm vào nhịp một:** `Trong Sprint 1, nhịp một chạy qua cầu nối C-11 (xem AD-16).`

**WORK-SPLIT §3, thay bảng Sprint 1:**

| Ngày | Dyuedu | CaoPhanTuanAnh | GiapPhanQuang |
|---|---|---|---|
| Thứ Năm 05/11 | #1: Compose, khung `web/`, Alembic một head | #3 `REGISTRY.md`: chữ ký phép 2, 3, 6 trước | #2: khung Python, envelope, endpoint giả |
| Thứ Sáu 06/11 | C-11: lịch chạy, `redact`, `ingest`; UA có email | 1.20: luật vai trò, cấp bậc, thành phố | 1.15: màn Bản đồ (bảng và 2D) trên dữ liệu giả |
| Thứ Bảy 07/11 | C-11 xong; cổng CI của #1 | #6 (1.4): snapshot `published`/`partial`, vòng đời | 1.21: tổng hợp tỷ trọng và endpoint thật |
| Chủ nhật 08/11 | Rà soát chéo, demo | Rà soát chéo | Nối 1.15 vào API thật; chạy `pg_dump` một lần |

Việc chung trong Sprint 1: email xin phép (#8), ít nhất ba cổng CI (#9): hướng phụ thuộc, một head Alembic, hình dạng `meta`.

**WORK-SPLIT §4, thêm vào đường găng:** `S1: #1 → C-11 → 1.20 → 1.21 → 1.15 (08/11)`.

### 4.6 UX: EXPERIENCE, State Patterns

```
OLD: | Mở ứng dụng | `ban-do` | Vào Bản đồ. Vai trò mặc định “Tất cả”. Lối xem 3D. Chú thích nguồn, ngày snapshot, và ba lưu ý FR-36 đang hiện. |
NEW: | Mở ứng dụng | `ban-do` | Vào Bản đồ. Vai trò mặc định “Tất cả”. Lối xem 3D; khi Story 1.17 chưa xong thì lối 2D, nút 3D tắt và có chú thích “Bản đồ 3D sắp có”. Chú thích nguồn, ngày snapshot, và ba lưu ý FR-36 đang hiện. |
```

DESIGN.md không đổi.

### 4.7 Việc khác

- **`sprint-status.yaml`, thêm dưới `epic-1`:**
  - `1-20-gán-vai-trò-cấp-bậc-và-thành-phố-bằng-luật: backlog`
  - `1-21-tính-và-đọc-tỷ-trọng-thành-phố: backlog`
- **Spec #2:** `MarketReadModel` cho phép chọn nguồn riêng cho từng phép. Trong Sprint 1, `city_shares` đọc dữ liệu thật, còn `skill_rates` vẫn là bản giả cho tới #27.
- **GitHub, sau khi duyệt:**
  - tạo issue cho 1.20, 1.21 và C-11;
  - đổi milestone của #4, #5, #7, #10 sang Sprint 2, và của #46 sang Sprint 1;
  - đổi label của #46 từ P1 sang P0;
  - đổi dòng "Chặn bởi" của #46 (thành 1.21) và #16 (thêm 1.20);
  - sửa phạm vi của #16 và #27;
  - chuyển task deck.gl của #46 sang #48 (1.17);
  - thêm vào mô tả milestone Sprint 1 dòng "1.15 đạt đủ AC và DoD trên dữ liệu thật".
- **`scraper/`:** thêm email liên hệ vào UA; bỏ `--force` khỏi lệnh gọi CareerLink trong `pipeline.py`.

## 5. Bàn giao

**Mức thay đổi:** vừa. Cần sắp lại backlog và phối hợp ba người. Không phải lập lại kế hoạch từ đầu: kiến trúc chỉ cập nhật ba AD cho khớp thực tế, PRD chỉ sửa một dòng rủi ro.

| Ai | Việc |
|---|---|
| Cả nhóm | Duyệt đề xuất này trong ngày 05/11. Chốt email liên hệ của nhóm cho UA và trang chính sách |
| GiapPhanQuang | Sửa `epics.md`, `sprint-status.yaml`, PRD, brief, spine, WORK-SPLIT, EXPERIENCE và spec #2 theo mục 4; cập nhật GitHub theo mục 4.7 |
| Dyuedu | #1 rồi C-11. Máy chạy lịch crawl hằng ngày |
| CaoPhanTuanAnh | #3, 1.20, #6 |

**Tiêu chí thành công, kiểm tối Chủ nhật 08/11:**

- 1.15 đạt mọi AC (gồm AC sửa về nút 3D) và 14 dòng DoD, trên dữ liệu thật của ít nhất hai nguồn và ít nhất hai snapshot. Có một người khác rà soát.
- `job_observations` có hàng của các ngày 05, 06, 07 và 08/11.
- Ít nhất ba cổng CI xanh; `pg_dump` đã chạy một lần.
- Từ lượt 06/11, User-Agent có email liên hệ.

## Phụ lục: trạng thái checklist

| Mục | Trạng thái |
|---|---|
| 1.1–1.3 Lý do, vấn đề, bằng chứng | [x] |
| 2.1–2.5 Ảnh hưởng tới epic | [x] Epic 1 đổi thứ tự; Epic 2 dời 2.2; Epic 3–6 không đổi |
| 3.1 PRD | [x] Chỉ dòng R2; MVP không đổi |
| 3.2 Kiến trúc | [x] AD-16, AD-20, AD-28 |
| 3.3 UX | [x] Một dòng State Patterns |
| 3.4 Tài liệu khác | [x] `sprint-status.yaml`, spec #2 đã sửa trên nhánh. [!] GitHub, `scraper/` — chờ nhóm |
| 4.1 Điều chỉnh trực tiếp | Khả thi · công trung bình · rủi ro trung bình–cao |
| 4.2 Quay lui | Không áp dụng |
| 4.3 Xem lại MVP | Không cần |
| 4.4 Hướng đi | [x] Phương án 1 |
| 5.1–5.5 Thành phần đề xuất | [x] |
| 6.1–6.2 Rà soát | [x] |
| 6.3 Duyệt | [!] GiapPhanQuang duyệt tạm 05/11; chờ hai thành viên còn lại |
| 6.4 Cập nhật `sprint-status.yaml` | [x] Đã thêm `1-20`, `1-21` trên nhánh |
| 6.5 Bàn giao | [ ] Sau khi duyệt |
