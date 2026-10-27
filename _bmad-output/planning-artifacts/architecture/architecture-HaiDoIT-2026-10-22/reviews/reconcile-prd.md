---
title: Reconcile PRD against the architecture spine
type: architecture-reconcile
source: _bmad-output/planning-artifacts/prds/prd-HaiDoIT-2026-10-22/prd.md
spine: _bmad-output/planning-artifacts/architecture/architecture-HaiDoIT-2026-10-22/ARCHITECTURE-SPINE.md
verdict: gaps
---

# Reconcile PRD against the architecture spine

Verdict: **gaps**.

The spine binds who computes public numbers, the median and the under-30 empty sentence, what a job row may store, offer text staying off the server, and token reopen. It contradicts the 18-month forecast display. Several shared vocabularies and write/read rules are unbound, so two builders can ship incompatible counts, salaries, or a job feed.

Checked against `prd.md` only. The spine and the PRD were not edited. Feature behavior that one unit can implement from the PRD is marked story-detail, not a hole.

## Findings

### F1. Forecast display is replaced by the early-signal sentence

- **Severity:** critical
- **Class:** contradiction
- **PRD:** §4 Dự báo 18 tháng, §5.1 FR-2, §7.1, §10 Ước tính, §12 question 1. v1 shows job-count ranges at 6, 12, and 18 months, each labeled as a forecast, not a figure that already happened. Why? of a range points at the job counts used to compute it. On the today view, the city forecast slot still shows the 12-month range. The "now" mark is the open-job count, not a range. v1 does not forecast salary. Prototype coefficients are not the formula. Question 1 defers only early-signal detection. The card may say that no signal has been recorded, and that sentence is not the forecast.
- **Spine:** AD-12 binds both the 18-month forecast and early signals to one rule: before week 1 the screen uses the "chưa ghi nhận" sentence, and a measured rule replaces it later. Deferred repeats that. A builder who follows the spine ships no range. A builder who follows FR-2 ships labeled ranges and still refuses a salary forecast. AD-2 correctly stops Next.js from inventing the forecast, but it does not say the API must return a range rather than the empty sentence.

### F2. Under-30 salary is bound; the cell, the widen, and the abnormal verdict are not

- **Severity:** high
- **Class:** spine-hole
- **PRD:** §4 Ô mẫu, Ngưỡng 30 tin, Lương bất thường; §5.1 FR-3; §5.2 FR-7; §5.6 FR-17; §11 NFR-1; §13 SM-C1. One public salary number is hidden everywhere when the cell has fewer than 30 postings: map header, city card, Học gì tiếp?, and the Soi tin salary verdict. The cell is role × city × level. On the map, a single role filter uses that role, the selected city, and the session level, and an unset level uses Junior. Filter Tất cả uses the role with the most postings in that city. No city selected means the header salary stays blank. Học gì tiếp? widens in order: nationwide, same role and level, then the nearby role group. Why? names the thin original cell and which step is in use. Salary is never taken from the thin cell. If the widened scope is still under 30, salary stays hidden. Nearby groups are an assumption (Data/AI alone; Backend with Frontend; DevOps/Cloud with Bảo mật; Mobile alone) but they are the current order. Soi tin may call a salary abnormal only when that posting's own cell has 30 or more and the public salary falls outside the posting's range. Under 30 it must not call the salary abnormal. The threshold must not be lowered to show more salaries. v1 shows no percentile band.
- **Spine:** AD-6 binds the aggregator: VND ranges only, midpoint of a range, median, even count averages the two middle points, under 30 the empty-sample sentence, no USD conversion. It says "the cell being calculated" and never defines the axes, the Junior default, the largest-role rule, the widen order, or "thin cell forbids an abnormal verdict." Map, Học gì tiếp?, and Soi tin are three readers. They can hide or show different numbers and still satisfy AD-6. The median math itself does not contradict the PRD.

### F3. A repeat sighting has dates, not an identity, a count, or an open/closed rule

- **Severity:** high
- **Class:** spine-hole
- **PRD:** §4 Lần làm mới của tin, Tin trùng; §5.1 FR-1; §5.6 FR-17; §7.1; §10 Làm mới and Số mỏng; §12 question 2. Open postings are refreshed daily. The map shows the date of the latest dataset refresh, which is not the same as a posting's last-seen date. Soi tin shows a refresh count plus first-seen and last-seen. Those three are testable without a "tin treo" label. The stale threshold (second refresh, or still open 30 days after first seen) is an assumption. It must not be treated as truth, and tests must not assert the label, before week 1. A duplicate is another open posting, different link, same skills, city, level, and salary range. VietJobs is historical credit, not open inventory.
- **Spine:** AD-4 keys the row on `source_id`, updates last-seen, and keeps first-seen. The conventions call `source_id` a pipeline hash and do not say the hash is stable across days. There is no seen-count, no dataset refresh timestamp, and no rule for a posting missing from today's file (still open, or closed). Nothing excludes a historical corpus from the open set. Nothing defers the tin-treo label the way AD-12 defers early signals. The loader and Soi tin can disagree about whether one URL seen on two days is one posting, and the map can keep counting jobs that yesterday's file no longer contains. AD-11 draws the loader on the always-on machine and does not bind a daily run.

### F4. Seven cities and the role filter are not a shared vocabulary

- **Severity:** high
- **Class:** spine-hole
- **PRD:** §4 Bản đồ nhu cầu, Toàn quốc, Cấp bậc; §5.1 FR-1 and the map description; §3.3; §6; §7.2. The map is exactly seven cities: Hà Nội, Hải Phòng, Đà Nẵng, Quy Nhơn, Nha Trang, TP. Hồ Chí Minh, Cần Thơ. All seven stay visible when a city has few postings. Toàn quốc is a widen step inside Học gì tiếp?, not an eighth city. The role filter is Tất cả, Backend, Frontend, Data/AI, DevOps/Cloud, Mobile, Bảo mật. Scenario level is Fresher or Junior. City headcount follows the role filter and is not restricted to those two levels. Remote and Japan are not markets. Extra cities are after v1.
- **Spine:** AD-4 stores city and level as fields. AD-10 canonicalizes skill names to the pipeline list. Cities, roles, and levels are free text. The scraper and the API can use different spellings, drop Quy Nhơn, or add Remote. Skill weeks being team-edited in Supabase is already bound and is not this hole.

### F5. Why? can point at a number and still miss the source the launch gate requires

- **Severity:** high
- **Class:** spine-hole
- **PRD:** §4 Nguồn, Vì sao?; §5.3 FR-10; §13 SM-4. Every claim on the roadmap has one Why?, including a claim dropped for thin data. A job-based claim points at the extracted record set or the original link, not the raw description. A report-based claim names the report. A thin-data rejection says the data is missing and does not state a salary. On saved roadmaps, 100% of claims must point at a posting or a source figure. That bar is not 95%.
- **Spine:** AD-7 says Why? points at the numbers, so the model cannot invent a count or a salary. It does not require a pointer to extracted rows, the original link, or a named report, and it does not forbid a thin-data claim from stating a salary. The UI and the model can both satisfy AD-7 and still fail FR-10. Grounding the prose in computed numbers is the right half of the rule.

### F6. The skill-trend layer is shared by two features and is absent

- **Severity:** high
- **Class:** spine-hole
- **PRD:** §4 Xu hướng và hạn dùng kỹ năng; §5.1 ngoài phạm vi; §5.4 FR-14; §7.1; §9. The trend layer is shared data for Học gì tiếp? and the roadmap. It is not a screen and has no nav item. A skill marked as declining is not rank 1, and Why? states the drop when a claim uses the layer. The roadmap must not describe that skill as if demand were flat. v1 does not ask people to submit their own salary. The prototype's shelf-life screen is not a v1 screen.
- **Spine:** No AD, no capability-map row, and no deferral. Học gì tiếp? and the roadmap can each invent a trend, or one can build the shelf-life screen. There is also no shared place for the classification the way AD-10 is a shared place for skill names and weeks.

### F7. Nothing stops a job feed, employer scores, or a contract reader

- **Severity:** high
- **Class:** spine-hole
- **PRD:** §3.3, §6, §7.2, §13 SM-C2. v1 does not match a person to an open job and does not suggest a newly unlocked job. It does not rate employers, show a response score, or collect application-experience reports. It does not read contracts or give legal advice. Suggested applications are a counter-metric, not success. Matching later requires a license and is not this two-month build.
- **Spine:** AD-4 stores the original link, skills, city, level, and salary range, which is enough to build a match list. The capability map says FastAPI reads Supabase and Next draws the map, Học gì tiếp?, and Soi tin. It never says the public read model is aggregates plus lookup of a link the user pasted. One builder can add a jobs feed or an employer-rating table; the other can omit it. AD-9 only keeps Soi tin from writing the server.

### F8. No price and no course link are only half covered

- **Severity:** medium
- **Class:** spine-hole
- **PRD:** §1, §5.3 FR-11, §6, §8, §13 SM-3. These two months have no candidate payment, no price, and no package on the site. A school or bootcamp trial is a dated note, not a screen. There is no course link, no commission label, and no click counter. A stage with no course link can still be saved. Offer compare and Soi tin work with no email. The email field stands on the roadmap after it appears, not on the map.
- **Spine:** AD-8 and AD-9 keep the map, offer compare, and Soi tin usable before a save, and AD-7 writes the roadmap only when mail succeeds. Nothing forbids a paywall, a checkout, a course URL in the model output, or a click counter. The three roadmap sentences can grow a link and still match "three sentences from the numbers."

### F9. Eligible-job counts can be AND in one endpoint and OR in another

- **Severity:** medium
- **Class:** spine-hole
- **PRD:** §4 Tin đủ điều kiện, Độ phủ; §5.2 FR-5, FR-6, FR-8. An eligible posting is open, inside the scope being calculated, matches the target role and level, and contains every owned skill and every selected hypothetical skill. Học gì tiếp? counts those postings. Rank is extra eligible postings per study week. Coverage uses the role's required-skill list, which travels with the fixed skill list. Until city, level, and target role are chosen, there is no before/after delta. Map headcount is a different number: open postings in the city for the role filter, not this eligible set.
- **Spine:** AD-2 puts the counting in FastAPI. AD-7 tells the model to write from numbers already computed. Neither defines the AND-of-skills predicate, nor that the role's required skills sit with the skill list from AD-10. The map endpoint and the Học gì tiếp? endpoint can publish two different "job counts" for the same city.

### F10. Raw description must not be shown, and the email must not ride along to a model

- **Severity:** low
- **Class:** spine-hole
- **PRD:** §6, §10 Việc riêng tư, §11 NFR-2, §5.6 FR-18. Do not store or show the raw job description, including text the user pastes. Email is only for saving and reopening the roadmap. Before an external call, personal data is stripped from what is sent. No password, no social login, no public profile.
- **Spine:** AD-4 already forbids storing the description, the company name, and recruiter name and contact on the job row. AD-9 already forbids an offer API and forbids Soi tin from writing the server. AD-8 already forbids password accounts and showing a roadmap to someone who merely knows the email. AD-3 forbids Supabase login. What is left: NFR-2 also forbids display, and the stored original link makes a fetch-and-show endpoint possible; AD-7 does not say the local prompt excludes the email; social login is not named, so it can still fork the token identity. These are residuals, not a miss of the storage ban.

## Bound already

Not findings. Listed so the quiet constraints are not reread as dropped.

- Who computes public counts, public salary, and the forecast: FastAPI. Next.js only draws the payload and does not open Supabase (AD-2). Offer net and the insurance shortfall are computed in the browser from the 2026 parameter set. No API accepts offer contents (AD-9). That matches §5.5 and UJ-4, where closing the tab leaves nothing on the server.
- Public salary, when shown, is one median of midpoints, hidden under 30 with the empty-sample sentence (AD-6). The hole is the cell, F2, not the aggregator.
- A job row keeps skills, city, level, salary range, posted date, and original link. It does not keep the description, company name, recruiter name, or recruiter contact (AD-4). That matches §10 and §6. The scraper and the loader meet only through a file. The scraper does not open the database (AD-5).
- Skill names and study weeks live in Supabase. The team edits weeks. Names match the pipeline (AD-10). That matches FR-5 and FR-6.
- One email, one roadmap. The server stores a token hash. Day 14 does not expire the link. The profile stays on the device until a save. A failed send does not count as a completed roadmap (AD-7, AD-8). That matches FR-12, FR-13, and UJ-2.
- One local model call, no five-agent chain, fallback sentences from the same numbers (AD-7). That matches §5.3 "no multi-agent step."
- Early-signal empty state, by itself, matches FR-3 and §12 question 1. F1 is only the decision to reuse that sentence for the forecast.
- Vietnamese UI copy is a convention. Phone and desktop widths are not an architecture fork (NFR-5).

## Story-detail, correctly left out

- **Severity:** low. **Class:** story-detail. **PRD:** §5.5 FR-15 and FR-16. **Spine:** AD-9 names who computes and that the server never sees the offer. Gross or net, dependents, bonus months, allowances, remote days not changing net pay, the 1% tie, the insurance shortfall, and the cap at that offer's gross are one browser formula.
- **Severity:** low. **Class:** story-detail. **PRD:** §5.3 FR-9. **Spine:** three stages, day splits, one practice project, and the "what you produce" sentence are the roadmap story. AD-7 already binds the non-obvious part: numbers first, one local call, save only after mail.
- **Severity:** low. **Class:** story-detail. **PRD:** §5.1 FR-3 role mix. **Spine:** shares within one city summing to 100% with a remainder bucket is one card, computed in FastAPI.
- **Severity:** low. **Class:** story-detail. **PRD:** §5.1 FR-4, §5.1 first visit. **Spine:** owned-skill marks, no sample profile, and the default role filter Tất cả are one screen's state. AD-8 already keeps that profile on the device until save.
- **Severity:** low. **Class:** story-detail. **PRD:** §11 NFR-3 and NFR-4. **Spine:** failed load keeps the last payload and offers retry; an empty filter says so and resets to Tất cả. One client.
- **Severity:** low. **Class:** story-detail. **PRD:** §9. **Spine:** five nav items and the map as the front door are IA, not a seam between scraper and API.
- **Severity:** low. **Class:** story-detail. **PRD:** §10 pipeline manners and the 2026-10-22 decision to use already extracted ITviec and TopDev data. **Spine:** robots.txt, delay, and stop-when-blocked are the scraper's own rules. AD-5 already stops the backend from calling SkillNexus. VietJobs-not-open is not this item; it is in F3.
- **Severity:** low. **Class:** story-detail. **PRD:** §12 question 3 and §14 on Data/AI cells. **Spine:** "some Data/AI city cells may be under 30" is a week-1 measurement, not a fact to encode. The widen rule in F2 is what must be shared.
- **Severity:** low. **Class:** story-detail. **PRD:** §13 SM-2 and SM-3. **Spine:** counting a reopen inside 14 days is one write on the roadmap record. The non-expiry of the token is already in AD-8. The school trial has no screen.
- **Severity:** low. **Class:** story-detail. **PRD:** §12 question 4. **Spine:** the legal questions do not block v1. The spine correctly does not invent a compliance design. F7 still needs to forbid a contract-reading feature.
- **Severity:** low. **Class:** story-detail. **PRD:** §5.6 duplicate listing and the "no score out of 100, no trust label, no AI index" lines. **Spine:** once F3 defines an open posting, the duplicate comparison and the banned labels are the Soi tin story. AD-13 already drops a different control, the "report a bad source" button, which the PRD does not require.
