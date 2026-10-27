---
title: Rubric review of the architecture spine
type: architecture-review
lens: rubric
spine: _bmad-output/planning-artifacts/architecture/architecture-HaiDoIT-2026-10-22/ARCHITECTURE-SPINE.md
verdict: gaps
altitude: initiative
level_below: epics and stories of one web product
---

# Rubric review — Hải Đồ IT

Verdict: **gaps**. One high hole leaves the Học gì tiếp? before/after block with a single eligible predicate for two numbers. The other adopted rules are enforceable, Deferred does not open a second contract, and the operational envelope is decided. AD-12 is enforceable as written.

Judged against the current spine (2026-10-23). Earlier reconcile notes describe a shorter spine; those holes are closed in the text under review and are not re-filed.

## Checklist

| Check | Result |
| --- | --- |
| Real divergence points for epics and stories are fixed, and none are missed | Gap. Job lifecycle, salary cell, seven cities, six roles, widen order, Why? pointers, shared trend layer, public read model, token reopen, and the offer/server split are fixed. The before/after baseline is not. |
| Every AD Rule is enforceable and prevents its stated divergence | Gap on AD-15. AD-1 through AD-14, AD-16, and AD-17 hold. |
| Nothing under Deferred lets two units diverge | Holds. Each deferred item has a locked stand-in. |
| Named tech is current | Pins match the memlog checks of 2026-10-21/22. This walker did not re-fetch registries. Two version risks below. |
| Brownfield | Greenfield. The scraper copy does not contradict the spine. One homonym in the pipeline is a low copy trap. |
| Parent spine | None. No inherited invariants, `binds` empty. |
| Every dimension this altitude owns is decided, deferred, or an open question | Holds. Deployment, environments, provider, and operations are decided or explicitly deferred. |

## Critical

None.

## High

### H1. The before/after block has one predicate for two numbers

- **What diverges:** Học gì tiếp? must return a before count, an after count, a rank of extra open jobs per study week, and a before salary and an after salary. AD-15 defines one eligible set: open, in the scope being calculated, matching target role and level, containing every owned skill and every hypothetical skill currently selected. That set is the after set. "Số tin trước", "số tin mở thêm", and "lương trước và sau" have no second predicate. One story will use owned-skills-only as the baseline. Another will reuse the single eligible set, or will count every open job in the city, and both will cite AD-15. The rank delta moves with whichever baseline they pick.
- **Salary half of the same block:** AD-6 binds every public salary to the role × city × level cell (midpoint median, hidden under 30, widened scope when Học gì tiếp? widens). That cell does not contain skills, so it does not change when a hypothetical skill is added. AD-15 still asks for lương trước and lương sau. One story will put the AD-6 median in both fields. Another will median the eligible jobs and will show a different number from the map. The product promise is that trying a skill changes the public salary; AD-6 forbids a second aggregator. The spine never says which of those two fields the block carries.
- **AD:** AD-15, with AD-6 on the salary fields.
- **Fix obvious?** The job-count sentence is obvious: trước = eligible jobs using owned skills only; sau = eligible jobs using owned skills plus the hypotheticals currently selected; tin mở thêm = that difference; skills already owned or already selected are not ranked; with no hypothetical selected there is no delta. The salary sentence is a choice, not a mechanical fill-in. Either both salary fields are the AD-6 median of the scope in force, or Học gì tiếp? salary is the median of each eligible set and AD-6 grows that axis.
- **Disposition:** discuss. Autofill the job baseline only after the salary choice is explicit, so the block does not gain a second salary formula by accident.

## Medium

### M1. Map headcount can still follow the session level

- **What diverges:** The map's job count and the salary cell sit on one screen. AD-6 builds the salary cell from the session level, and defaults that level to Junior. AD-14 says the map count follows the role filter and is not limited to Fresher and Junior. It does not say the count ignores the session level. A map story can count Junior-only jobs and still match the salary sample. Another can count every level. City totals then differ.
- **AD:** AD-14, pulled by AD-6.
- **Fix obvious?** Yes. Map headcount is every open job in the city for the role filter, all levels. Level selects the salary cell and the Học gì tiếp? scenario only.
- **Disposition:** autofix.

### M2. The scraper may still extract skills with the local model

- **What diverges:** AD-5 moves the SkillNexus scraper into this repo, bans an external model API, and drops the description after extraction. AD-7 limits Ollama to the roadmap's project name and product sentence. A scraper story can still call that local model to mine skills, then drop the text, and satisfy both sentences. The code being copied (`pipeline/scrapers/skills_text.py`) scans the taxonomy in memory and does not call a model. Those two extractors emit different skill sets, and every count in AD-6, AD-10, and AD-15 moves with them.
- **AD:** AD-5, AD-7.
- **Fix obvious?** Yes. The scraper extracts only with the pipeline taxonomy scan. It does not call Ollama.
- **Disposition:** autofix.

## Low

### L1. Even-count median fights the integer-đồng convention

- **What diverges:** AD-6 sets an even count's median to the average of the two middle midpoints. The conventions say a VND salary is an integer number of đồng. Two formatters can show a `.5` or round it.
- **AD:** AD-6, Consistency Conventions.
- **Fix obvious?** Yes. State the integer rule (one rounding).
- **Disposition:** autofix.

### L2. "Most open jobs" has no tie-break

- **What diverges:** With the Tất cả filter, AD-6 picks the role with the most open jobs in the city at the session level. A tie leaves two salary cells.
- **AD:** AD-6.
- **Fix obvious?** Yes. Break ties by the role order in AD-14.
- **Disposition:** autofix.

### L3. Two pipeline functions share `compute_source_id`

- **What diverges:** AD-4 spells SHA-256 hex of source name, `0x1F`, then URL. That matches `pipeline/scrapers/jobboards.py`. `pipeline/extractors/vietjobs_loader.py` defines another `compute_source_id` over record fields plus a row index. A copy that grabs the VietJobs function will key rows differently. AD-4 also keeps VietJobs out of the open set, so the second function is the wrong one to copy.
- **AD:** AD-4.
- **Fix obvious?** Yes. Name `jobboards.compute_source_id` as the function whose bytes are the rule.
- **Disposition:** autofix.

### L4. Version risk on two unpinned names

- **What diverges:** Python 3.12, FastAPI 0.159.1, SQLModel 0.0.48, Next.js 16.4.2, Ollama 0.40.8, and Docker Compose 5.6.1 match the memlog version checks. Qwen3 8B has no digest or tag. Supabase Postgres is "the managed Postgres" with no major; the memlog had pinned 18.6 before the move to Supabase. Two machines can pull different weights or different major versions of Postgres.
- **AD:** Stack, AD-3, AD-7.
- **Fix obvious?** The Qwen tag is obvious. The Postgres major is Supabase's, so pinning it may fight the provider. Leave the web re-check to the other reviewer.
- **Disposition:** ignore pending that web check. Note the risk only.

### L5. A pasted description can still be shown

- **What diverges:** AD-4 and AD-5 forbid keeping the description, the title, and the company. AD-9 keeps Soi tin off the model and off the server write path. Nothing forbids the screen from echoing text the user pasted. Storage stays clean either way; the show/hide behavior forks on one screen.
- **AD:** AD-4, AD-9.
- **Fix obvious?** Yes. One sentence: do not render a job description, including text the user pasted.
- **Disposition:** autofix.

### L6. The handoff file has a schema and no directory

- **What diverges:** AD-5 locks the JSONL fields, both channels, and a daily load on the web machine. The seed draws scraper → file → loader on that machine. The directory is unnamed, and the scraper is not explicitly on that same machine. Two epics can still honor the schema and miss each other (a laptop path versus a host path).
- **AD:** AD-5.
- **Fix obvious?** Yes. One directory on the web machine; the daily job there scrapes and then loads.
- **Disposition:** autofix. Low because the field contract is already closed and the machine is already named.

### L7. Which skill lands on which stage

- **What diverges:** AD-7 locks three stages, one skill from the selected hypotheticals, and a deepen-an-owned-skill rule when those run out. It does not say the order, or which owned skill is deepened. One roadmap writer can shuffle the saved stages. This is one FastAPI function, so it does not split scraper from API.
- **AD:** AD-7.
- **Fix obvious?** Yes. Take selected hypotheticals in the AD-15 rank order, then deepen one owned skill.
- **Disposition:** autofix.

## Checked, not findings

**AD-12 is enforceable.** Before week 1, the +6, +12, +18 marks and the forecast slot on the today card carry no number and no range. The sentence is «Chưa ghi nhận dự báo cho mốc này.» The today mark stays the open-job count. v1 does not forecast salary. When a measured formula exists, the payload is a labeled range of job counts at 6, 12, and 18 months, the today card uses the 12-month range, and a single point is forbidden. Early signal is a different sentence, «Chưa ghi nhận tín hiệu đáng kể cho thành phố này.», and later it is one event sentence with Vì sao?. Prototype coefficients cannot be shipped before week 1, because any number is forbidden. The rule prevents the divergence it names. The PRD and UX still draw a range in that early window; that difference is the adopted override, and it is testable.

**Deferred.** Forecast formula, early-signal detector, stale-job threshold, and eight-quarter up/down/flat each have a fixed stand-in (the forecast sentence, the signal sentence, seen-count plus two dates, «Chưa đủ mẫu.» with no declining flag). Domain and Supabase region are one choice when the web machine is stood up; feature code talks to same-origin Next and to the single Supabase from `backend/`. The skill-to-role column contents are data in the AD-10 table; the majority-role formula is already locked. None of these let two epics pick incompatible contracts.

**Operational envelope.** Deployment is one always-on machine, Docker Compose 5.6.1 bringing up Next.js, FastAPI, and Ollama, not Postgres (AD-11), drawn in the structural seed. Environments are that machine and the code machines, one shared paid Supabase, code machines not sending user mail (AD-3, AD-11). Providers are Supabase Postgres, the group's mailbox, and local Ollama. Operations place the daily load and real mail on the web machine. L6 is a thin residue inside that envelope, not a silent dimension.

**Spec coverage already closed.** Open-set identity and `seen_count`, the salary cell and the under-30 sentence, seven city names, role vocabulary, eligible-job AND, widen order, Why? pointers, the shared trend layer, no job feed, and no course URL are in AD-4 through AD-17. Offer tax brackets stay in the PRD appendix, with FastAPI as the only publisher (AD-9). Story copy, visual design, and the browser offer arithmetic stay out of this review on purpose.

**Brownfield.** This repo has no product code to ratify. `jobboards.compute_source_id` matches AD-4. The VietJobs hasher does not, and AD-4 keeps VietJobs out of the open set (L3). The current `ScrapedJob` still carries title and company; the handoff file in AD-5 drops them. That is the new boundary. Skill extraction in the pipeline is an in-memory taxonomy scan, which matches the external-API ban; M2 only seals the local-model fork.

**Parent.** No parent spine. Nothing inherited to weaken.

## Counts

- Critical: 0
- High: 1
- Medium: 2
- Low: 7
