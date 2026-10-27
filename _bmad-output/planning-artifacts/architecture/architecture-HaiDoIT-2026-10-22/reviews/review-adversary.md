---
title: Adversarial review of the architecture spine
type: architecture-review
lens: adversary
spine: _bmad-output/planning-artifacts/architecture/architecture-HaiDoIT-2026-10-22/ARCHITECTURE-SPINE.md
verdict: holes
---

# Adversarial review — Hải Đồ IT architecture spine

Verdict: **holes**.

Attack: for each candidate, build two units one level down that obey every AD and still cannot share state. A behavior one story can read from the PRD or EXPERIENCE, with one owner, is not a hole. A deferred item is a hole only when two units can diverge while obeying the deferral. Bound choices are left closed: one shared Supabase, no passwords, offer math in the browser, local Ollama for roadmap prose, no report-source button, no forecast numbers before week 1.

## H1. The open set is one file, and the crawler may write many

- **Units:** `scraper/` and the loader in `backend/`.
- **Build A:** The crawler writes one JSONL per channel per day (`itviec.jsonl`, `topdev.jsonl`, `coccoc.jsonl`, `greenhouse.jsonl`, `lever.jsonl`, `workable.jsonl`). Each line has the AD-5 fields. Both channels exist. The crawler does not open Supabase and does not call the loader.
- **Build B:** The loader treats “the file of the latest successful load” as the entire open set. After it successfully loads the last channel file, every `source_id` absent from that file gets `is_open` false. ITviec rows loaded earlier the same day close.
- **ADs both satisfy:** AD-4 (open means the `source_id` is in the file of the latest successful load; the loader is the only writer of job rows; a repeated load of the same file does not increment twice). AD-5 (the crawler writes JSON Lines, both channels exist, the two sides do not call each other, the crawler does not open Supabase). Neither sentence says the daily artifact is one snapshot, nor where it sits on disk.
- **Smallest rule:** Mỗi ngày cào ghi đè đúng một file `data/open-jobs.jsonl`, là ảnh toàn bộ tin đang mở của mọi kênh. Một lần nạp thành công đọc đúng file đó. Chỉ máy chạy web chạy lệnh nạp, một lần tại một thời điểm. Cùng nội dung byte (SHA-256 của file) không tăng `seen_count` lần thứ hai.

## H2. The JSONL line and `source_id` have two computers

- **Units:** `scraper/` and the loader.
- **Build A:** The crawler sets `source` to `ITviec`, `TopDev`, `Cốc Cốc`, `Greenhouse`, `Lever`, `Workable`. It sets `source_id` to uppercase hex of `source + U+001F + url`. `skills` is one comma-separated string. Unknown pay is an omitted key.
- **Build B:** The loader recomputes `source_id` as lowercase hex of the pipeline slugs (`itviec`, `topdev`, `coccoc`, `greenhouse`, `lever`, `workable`) plus the URL, and rejects a line whose `skills` is not an array or whose salary keys are absent. The open-set check looks for the file's `source_id` string. Every recomputed id misses. Greenhouse rows with no salary never load.
- **ADs both satisfy:** AD-4 (`source_id` is SHA-256 hex of “tên nguồn”, `U+001F`, and the URL, “the same way as” `compute_source_id`; the pipeline function takes the source string as an argument and the spine never lists the strings; “dạng hex” allows either case). AD-5 (the line has `source`, `source_id`, `skills`, `salary_min_vnd`, `salary_max_vnd`; it does not say array vs string, or null vs omitted). The convention “VND is an integer number of đồng” does not say how an unknown range is encoded. The loader must not call SkillNexus, so it cannot import the one function.
- **Smallest rule:** `source` chỉ là `itviec`, `topdev`, `coccoc`, `greenhouse`, `lever`, `workable`. `skills` là mảng chuỗi. `salary_min_vnd` và `salary_max_vnd` là số nguyên đồng hoặc null. `posted_on` là `YYYY-MM-DD` hoặc null. Lệnh nạp cắt khoảng trắng hai đầu của `source_url`, tự tính `source_id` = SHA-256 hex thường (UTF-8) của `source + U+001F + source_url` đó, và không dùng `source_id` sẵn trong dòng. Bảng `job_posting` dùng đúng các tên đó cộng `role`, `seen_count`, `first_seen`, `last_seen`, `is_open`; `skills` là `text[]`.

## H3. Skill names are a shared vocabulary the crawler is forbidden to read

- **Units:** `scraper/` and the loader plus the FastAPI skill API, which share the AD-10 table.
- **Build A:** The crawler ports the pipeline alias list on the day it is copied and emits those strings. It does not open Supabase. A later rename in the pipeline is invisible to it.
- **Build B:** The table is seeded from a later export, or typed with display names (`Node.js` vs `NodeJS`). The loader exact-matches. Unmatched tokens do not vote, so the job gets no role. Chips and coverage use the table names. Eligible-job matching is string equality against the job's stored skills, so the counts stay empty.
- **ADs both satisfy:** AD-5 (the crawler does not open Supabase and does not call the loader; the file still has `skills`). AD-10 (names “match the pipeline's normalized names”; the team edits weeks, role, and flags in the table; the loader assigns the job role by majority vote; a tie or no assigned role means no role). The deferral covers the role-column contents, not the name list, so leaving roles blank does not authorize two name lists. Nothing names one artifact both sides must load.
- **Smallest rule:** Một file `taxonomy.json` trong repo là danh tên đã chuẩn hóa duy nhất. Cào chỉ ghi tên có trong file. Lệnh nạp seed `skill.name` từ file đó và bỏ token ngoài file. Nhóm sửa `weeks`, `role` và cờ trên bảng, không đổi tên trên Supabase. Bảng `skill` có `name`, `weeks`, `role`, và sáu cờ `required_backend`, `required_frontend`, `required_data_ai`, `required_devops`, `required_mobile`, `required_security`.

## H4. The footer clock has no row

- **Units:** the loader and the FastAPI read API.
- **Build A:** On success the loader updates `last_seen`, `seen_count`, and `is_open` on job rows. It writes no other table. Every write sentence in AD-4 is met.
- **Build B:** The API must return the time of the latest successful load, and that time must not be a job's `last_seen`. It reads `dataset_status.refreshed_at`. The loader never writes that column. The footer is empty. Using `max(last_seen)` would violate the same sentence, so a faithful API will not.
- **ADs both satisfy:** AD-4 (the loader updates `last_seen` and keeps `first_seen`; the API returns one timestamp of the latest successful load; that timestamp is not `last_seen`). No table, column, or writer is named for the load run. The PRD only says the user sees the date, which does not tell the loader where to put it.
- **Smallest rule:** Khi lần nạp thành công, lệnh nạp ghi một dòng `ingest_runs.succeeded_at` timestamptz. API chân trang đọc max của cột đó và hiện ngày lịch `Asia/Ho_Chi_Minh`. Không suy mốc từ `last_seen` hay `posted_on`.

## H5. “Under 30” is two counts

- **Units:** the salary cell in the map / Soi tin API, and the widen step in Học gì tiếp?.
- **Build A:** The salary cell counts open jobs in role × city × level that have a VND range. Twelve salaried jobs hide the median. This build also widens only when that salaried count is under 30.
- **Build B:** Học gì tiếp? widens when the open-job count in role × city × level is under 30, salary or not. Forty open jobs and twelve salaried jobs do not widen. Eligible counts stay on the city. Salary stays hidden because the salaried cell is still under 30. Why? does not say the result was widened.
- **Worked clash:** Hải Phòng × Backend × Junior, 40 open jobs, 12 with a VND range. Build A widens nationwide and, once that scope has 30 salaried jobs, shows that median and says so. Build B does not widen. Same ADs, different before/after counts.
- **ADs both satisfy:** AD-6 binds public salary figures: only VND ranges enter the median, and under 30 the empty sentence is on every screen. AD-15 says widen when “the role × city × level cell is under 30 jobs” and never says “jobs that have a VND range”. AD-6's bind is the salary number, not the widen predicate. Both builds still hide a salary computed from fewer than 30 ranges.
- **Smallest rule:** Ngưỡng 30 để nới của AD-15 đếm đúng tập của AD-6: tin đang mở trong ô có khoảng lương VND. Không đếm tin không có khoảng lương.

## H6. The roadmap row has two writers and two orders

- **Units:** the roadmap save route and the mail sender, both in `backend/`.
- **Build A:** The route inserts the roadmap and the token hash, asks the mailer to send, and deletes the row if the send fails. The mailer does not touch the table.
- **Build B:** The mailer sends first and inserts the row only after the mailbox accepts. The route does not insert. A crash after accept and before insert leaves a link and no row. A crash in Build A after insert and before send leaves a row and no mail.
- **ADs both satisfy:** AD-7 (the roadmap is written only when mail can be sent). AD-8 (send and write are “one outcome”; a failed send leaves no roadmap row; the server stores the token hash next to exactly one roadmap for that email). Neither sentence names the writer or forbids the other order. Handled failure matches both builds. The crash window does not.
- **Smallest rule:** Chỉ route lưu lộ trình ghi bảng lộ trình. Route ghi dòng và hash trong một transaction, gửi thư, rồi commit khi thư được nhận. Thư lỗi thì rollback, không còn dòng. Bộ gửi thư không ghi bảng.

## Not a hole

Checked so they are not re-opened.

- **Forecast, early signal, eight quarters, tin treo.** AD-12, AD-16, and AD-4 already freeze the pre-week-1 sentence or the three raw fields. Two units cannot show a number, a point, a homemade quarter series, or a tin-treo label and still obey the deferral.
- **Offer math, passwords, one Supabase, Ollama prose, no report-source control.** Bound. The browser has one formula and the appendix has the 2026 figures. Naming JSON keys for that one payload is a story, not a second owner.
- **Eligible jobs stay AND, and “đúng vai trò mục tiêu” stays exact at the nearby-role step.** AD-15 states both predicates. Widening the salary cell to the neighbor roles (AD-6) does not revoke the exact-role predicate. A counter that drops it is breaking AD-15, not obeying it.
- **Session fields, `seen_count` as “times seen again”, five nav surfaces, duplicate definition, median of midpoints, seven city strings.** One owner. A story can read the fields from AD-8, EXPERIENCE, or the PRD. Two pages that do not share the one session store are disobeying AD-8, not a second legal store.
- **URL canonicalization beyond trim.** AD-4 already says Soi tin matches the stored `source_url` after trimming whitespace. Both sides can obey that and agree. H2 only stops the loader hashing a different byte string than the one it stores.
