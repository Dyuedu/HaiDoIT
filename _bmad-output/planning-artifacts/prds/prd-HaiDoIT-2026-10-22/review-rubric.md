# PRD Quality Review — Hải Đồ IT

## Overall verdict

The PRD is strong enough to decide what v1 is: a two-month web with no payment on the product, six surfaces, a hard 30-post floor on every public salary, and a 100% sourcing gate. Thesis, counter-metrics, non-goals, and shape hold, and pushback on the JobsGO line, the legal risk, and the week-1 facts is recorded rather than smoothed. It is not yet safe as the only input to stories for the core loop. Job coverage, the city-card salary, and thin-cell widening are unspecified even where mục 12 calls the widening rule closed; the BHXH check has no input for the insurance base; SM-3 can be met by an unrecorded sentence.

## Decision-readiness — adequate

A reader can act. §1 and §8 state that money on the web is zero and that the only money-shaped event is a school or bootcamp saying yes. §10 records Duy's 2026-10-22 choice to ship extracted ITviec and TopDev figures without permission and without waiting for a lawyer, and says the mục 12 legal questions do not block the build. The addendum names the account designs that were refused (password, browser-only storage) and why. Open questions 1 and 2 are actually open: early-signal detection and the stale-post threshold, each with an interim behavior (the card may say nothing was recorded; tests must not treat the stale label as truth). The single `[NOTE FOR PM]` sits on a real temptation, not a safe checkpoint: do not pull a repo-submission form into v1 to fake a revenue path.

The continuation contract is softer than the product contract. All four §13 gates must pass, and three of them name a count, a window, and a floor. SM-3 does not. Someone pushing back at month two on whether "one school agreed" happened will not find an artifact, only the phrase "một lời đồng ý".

### Findings

- **high** SM-3 can be passed by an unrecorded sentence (§13, §1, §8) — "Bốn mức dưới đây cùng phải đạt thì hai tháng được tính là đi tiếp", and SM-3 is "từ 1" where "Đây là một lời đồng ý, không phải một tính năng trên web." The refusal to build a school portal is right. The gate still has no evidence standard, so the go/no-go the other three metrics make decidable can be argued either way. *Fix:* define the artifact that counts (a dated email or note, named owner, what "thử" means) without adding a screen.

## Substance over theater — strong

Lan, Khoa, and Mai are labeled temporary scenery in §3.4, and the PRD refuses a scene where Lan almost pays for a course. Each journey forces a product rule: UJ-1 places the email at save time, UJ-2 is the SM-2 window and is explicitly not proof that a real person returns, UJ-3 is the two tools that work with nothing stored. That is not persona theater.

The competitive claim was narrowed on purpose. §2 and the addendum's "Khoảng trống cạnh tranh đã thu hẹp" say HireJack already lets someone try a skill and count new jobs, and ITviec already shows posting movement and a salary survey. The gap kept is city-level public salary in Vietnam plus a sourced 90-day plan, without matching and without employer scores. §11 is six product bounds (the 30-post hide, no job-text storage, last-known counts on source failure, empty-filter reset, Vietnamese at phone and desktop width, reopen on another machine), not a scalable/secure/reliable block. §1 cannot be dropped into a generic career PRD: it names the three surfaces, zero revenue, two months, and the four gates in mục 13.

## Strategic coherence — strong

The bet is in §2: if the user does not see real data rather than generic advice, Học gì tiếp? and Lộ trình 90 ngày lose their reason to exist. The assumption tag on the JobsGO "thiếu lộ trình" line keeps that bet from being smuggled in as a measured fact. Features follow the bet. The map is the storefront, the skill trial is the experiment, the roadmap is the sourced plan, and the trend layer is a shared input with no screen of its own. §8 says cutting Soi tin or So sánh offer would not produce a course, so those two stay as unpaid pulls rather than as the thesis. v2 (project review, negotiation practice, percentile pay) is deferred because it is the later revenue, and the note in §7.2 says not to drag it forward.

SM-4 (100% of claims have a real source, "Không hạ xuống 95%") is the metric that validates the thesis. SM-1 and SM-2 measure the plan being saved and reopened, which is the behavior the thesis needs inside two months, and §3.1 says the life outcome (a job or a raise in 3–6 months) is not what these two months measure. SM-C1 forbids inflating visible salaries by lowering the 30-post floor. SM-C2 forbids counting job suggestions and applications as success, so SM-1 cannot be chased by becoming a matcher. The scope kind is a problem-solving experience. Revenue is stated as not the MVP kind.

## Done-ness clarity — thin

FR-1, FR-4, FR-10, FR-11, FR-12, FR-18, and the measurement half of FR-17 tell an engineer what passes. NFR-1, NFR-2, and NFR-4 are bounds. The differentiator is where the consequences stop being tests. Học gì tiếp? turns on "số tin đủ điều kiện" and "độ phủ", neither of which is defined. The city card must show one public salary from an ô mẫu cut by role × city × level, on a first visit that has no profile and a default role filter of "Tất cả". FR-7 allows two widenings and mục 12.3 says the widening rule is already closed. A roadmap stage passes FR-9 with a project name. FR-14's ranking rule has an exception that makes any ranking pass. FR-16's shortfall cannot be entered with the fields FR-15 lists.

The addendum is honest that salary rollup, the 18-month formula, and early-signal detection are for architecture or week 1, and that the PRD only locks what the user sees. That split is right for early signals, because FR-3 already says the card ships with "chưa ghi nhận". It is not enough for the skill trial and the city salary, where the visible number is the product and the test can be satisfied by a placeholder.

### Findings

- **high** Job coverage is undefined (§5.2, FR-5, FR-6, FR-8) — the screen "thấy ba thứ đổi: số tin đủ điều kiện, lương công khai, thời gian học", and FR-8 says "Thêm một kỹ năng đã có thì độ phủ trước tăng". Neither "tin đủ điều kiện" nor "độ phủ" is in mục 4. FR-6 ranks "số tin mở thêm trên mỗi tuần học" against that same undefined delta. Any before/after pair passes. *Fix:* define when a posting counts as covered before a skill is added and after, and state that study time is the sum of the team-assigned weeks.

- **high** The city card's one salary has no cell (§5.1, FR-3, NFR-1, mục 4) — "Lần đầu không có hồ sơ mẫu", the default role filter is "Tất cả", and ô mẫu is "cắt theo vai trò, thành phố và cấp bậc". FR-3 still requires "Khi ô mẫu đủ ngưỡng 30 tin, thẻ hiện một lương công khai." NFR-1 also names "ô lương trên đầu Bản đồ nhu cầu", which no FR describes. "Cơ cấu vai trò" has no unit. *Fix:* specify, for an empty profile and for each role filter, which role and level supply the header number and the card number, and whether cơ cấu is counts or shares.

- **high** Thin-cell widening is two branches called closed (FR-7, UJ-1, §12.3) — FR-7 "tính số tin trên toàn quốc hoặc trên nhóm vai gần", and UJ-1 repeats the hoặc. Mục 12.3 says "Quy tắc nới ở FR-7 đã chốt." "Nhóm vai gần" is never defined. A story can widen either way, or switch per query, and still match the Why? line that "nói đã nới theo toàn quốc hay theo nhóm vai gần." *Fix:* order the widenings, list the nearby-role groups, and remove "đã chốt" until that text exists.

- **high** The BHXH check has no input (FR-15, FR-16, UJ-3) — FR-15's fields are "lương tháng, loại gross hoặc net, số người phụ thuộc, số tháng thưởng, phụ cấp, và số ngày remote mỗi tuần." FR-16 fires "Khi một offer đóng bảo hiểm trên mức thấp hơn lương" and must show an annual shortfall. Nothing in the field list is the insurance base, including the net-offer case. *Fix:* add the base as an input, or define it as equal to gross unless the user overrides it, and say which salary "lương" means when the offer is net.

- **medium** The trend rule cannot fail (FR-14, mục 4) — "Một kỹ năng đang giảm không đứng đầu danh nên học tiếp chỉ vì số tin tức thời, trừ khi Vì sao? nói rõ cả mức giảm." "Đang giảm" has no window or threshold. The trừ khi clause means a declining skill may still rank first. *Fix:* define tăng/giảm, and state whether a declining skill is demoted or only annotated.

- **medium** A roadmap stage is done when it has a title (FR-9) — "Đủ ba chặng. Mỗi chặng có tên dự án thực hành." The skill-membership line constrains which skills appear, not what a stage contains or what the learner produces. Three titles with sourced sentences pass FR-9 and FR-10. *Fix:* add one content consequence per stage (skills in that stage, and the artifact the project asks for).

- **medium** Any labeled interval passes the forecast (FR-2, addendum) — "Mỗi mốc hiện một khoảng, có nhãn là dự báo, không hiện một số như thể đã xảy ra." The addendum leaves "cách tính dự báo 18 tháng" to architecture or week 1 and locks only the label. A constant band satisfies the consequences. The early-signal half of that same deferral is fine, because FR-3 already has an empty state. *Fix:* require the interval's inputs to be citable from Vì sao?, and forbid a fixed illustrative multiplier from the prototype.

- **medium** Day 14 is a metric window, and access after it is unstated (FR-13, UJ-2, SM-2) — "Cùng email, mở lại trong 14 ngày kể từ lúc lưu, được tính là một lần mở lại cho SM-2." Nothing says whether the link still opens on day 15. An implementer can expire it and still match the sentence. *Fix:* say the 14 days count only for SM-2 and the saved roadmap still opens after, or say the link expires.

- **medium** Abnormal salary compares a range to one number (mục 4, FR-17) — lương bất thường is "khoảng lương trên tin không giao với lương công khai", and lương công khai is "một số lương của ô mẫu". A range does not intersect a scalar until the number is given a width. The addendum also leaves "Cách gộp nhiều khoảng lương thành một lương công khai" unresolved, so FR-17's "không giao" has nothing to intersect with. *Fix:* define non-overlap against that one number, once the rollup exists.

- **low** "Gần ngang nhau" has no band (FR-15) — the result "nói hai offer gần ngang nhau" with no amount or percent. *Fix:* name the band.

- **low** Remote days are an input that must not change the result (FR-15, addendum) — FR-15 lists "số ngày remote mỗi tuần" beside the salary fields. Only the addendum says "Số ngày remote hiện cùng offer và không đổi thực nhận cả năm." A story taken from FR-15 alone can wire the days into take-home. *Fix:* repeat that sentence in FR-15.

## Scope honesty — strong

§3.3 and §6 say who is not served and what is not built: matching, employer scores, contract advice, someone else's roadmap, project review, negotiation practice, percentile pay, Remote and Japan as products, a native app, a school portal, passwords, a price, course-commission links, paid acquisition, and raw job text. §7.2 repeats the deferrals with versions. Inline "Ngoài phạm vi" under FR-4 and FR-16 catches the two omissions a reader of those FRs would otherwise assume (a shelf-life screen, a negotiation gym). Assumptions in §2, §3.4, FR-5, FR-6, FR-7, FR-13, FR-17, and §9 are tagged, and mục 14 roundtrips them. Week-1 items say what to build before the measurement exists. The false closure of the widening rule is judged under done-ness; the feature omissions themselves are not silent.

## Downstream usability — adequate

This PRD feeds UX, architecture, and epics (§0), so extraction matters. FR-1–FR-18, UJ-1–UJ-3, SM-1–SM-4, SM-C1–SM-C2, and NFR-1–NFR-6 are contiguous and unique, and the SM → FR pointers resolve. Mục 4 is used as vocabulary rather than as a preface: ngưỡng 30 tin, lương công khai, nhận định, and Vì sao? keep one meaning across FRs. UJ-1 and UJ-2 carry Lan's context inline.

Two extraction faults remain. UJ-3 is one id with two protagonists and two flows, so a story pass has to split it by hand. Several nouns the core FRs depend on are not in mục 4, which is the section §0 tells a downstream reader to use.

### Findings

- **medium** UJ-3 has two protagonists (UJ-3) — "Khoa soi tin và Mai so sánh offer, cả hai đều chưa lưu", then separate đường đi. Both are named and neither floats. One id still covers two tools. *Fix:* split into two UJs that share the no-email rule, or state in the UJ title that the id is two branches on purpose.

- **medium** Core nouns are missing from mục 4 (mục 4, §5.2, FR-7, FR-8) — stories will source-extract "nhóm vai gần", "tin đủ điều kiện", "độ phủ", "hồ sơ phiên", and cấp bậc. The role filter is enumerated in §5.1 ("Tất cả, Backend, Frontend, Data/AI, DevOps/Cloud, Mobile, Bảo mật"). Cấp bậc is not, beyond the FR-5 assumption that scenarios are "Fresher và Junior". *Fix:* add the entries once the done-ness fixes define them, and list the cấp bậc values.

## Shape fit — strong

Consumer web, meaningful UX, chain-top into UX, architecture, and epics. Three journeys with named people are load-bearing and present, not a capability spec with decorative UJs and not a consumer product with none. §9's five destinations match the feature set. The trend layer correctly has no destination. Legal exposure is a constraint plus non-blocking questions, not a fake compliance matrix. The addendum separates prototype behavior that v1 keeps from prototype furniture (3D, percentile bars, illustrative salary multipliers, multi-agent as a screen step). Weight matches a three-person, two-month build.

## Mechanical notes

- Glossary drift. "Làm mới" is the daily pipeline refresh in §10 ("Tin đang mở được làm mới hằng ngày") and the repost count in FR-17 ("số lần làm mới"). "Hồ sơ phiên" is used from FR-4 on; mục 4 defines "Hồ sơ" only. §3.2 writes "junior" and "fresher"; FR-5 writes "Fresher và Junior".
- ID continuity. No gaps and no duplicates across FR, UJ, SM, SM-C, and NFR. SM-3 points at mục 8, which exists. FR-10's pointers to SM-1 and SM-4 resolve.
- Broken cross-ref. §0 says "Từ vựng nằm ở mục 3." Vocabulary is mục 4. Mục 3 is the users.
- Assumptions index. Every inline `[GIẢ ĐỊNH]` is represented in mục 14. The FR-5 pair shares one index line. FR-13 repeats the UJ-2 one-email assumption; the index cites UJ-2. The addendum's "Giả định đang để Duy sửa" is that same item, not a second assumption.
- Open-item placement. Salary rollup and the forecast formula are deferred in the addendum and are not in mục 12. Early-signal detection is in both. The ITviec and TopDev terms-of-service limit is in the addendum's legal list and not in mục 12; §10 already records the decision to proceed without permission.
- UJ protagonists. UJ-1 and UJ-2 name Lan inline. UJ-3 names Khoa and Mai; see the downstream finding.
- NFR-2 contemplates job text "dù người dùng dán vào một ô." FR-18 says there is no such box. Defensive, not a second feature, as long as stories do not add the box to satisfy the NFR.
