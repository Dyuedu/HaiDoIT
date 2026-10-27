---
title: Version review of the architecture spine
type: architecture-version-review
spine: _bmad-output/planning-artifacts/architecture/architecture-HaiDoIT-2026-10-22/ARCHITECTURE-SPINE.md
checked: 2026-10-23
verdict: confirmed
---

# Version review — Hải Đồ IT architecture spine

Verdict: **confirmed**.

Checked the Stack table and the same pins in AD-1, AD-2, AD-3, AD-7, and AD-11. The spine was not edited. Every version below was read from a page or JSON document fetched in this review. Nothing here is filled from memory.

No committed row is missing, yanked, canary, or a release candidate. Newer tags exist beside two pins; they do not replace the committed versions.

## Stack

| Name | Spine | Found | Result |
| --- | --- | --- | --- |
| Python | 3.12 | 3.12, security support through 2028-10. Latest patch 3.12.15 (2026-09-30), source only. | Confirmed |
| FastAPI | 0.159.1 | 0.159.1 on PyPI, not yanked, uploaded 2026-10-21. | Confirmed |
| SQLModel | 0.0.48 | 0.0.48 on PyPI, not yanked, and it is the latest release. | Confirmed |
| Next.js | 16.4.2 | 16.4.2. npm `latest` is 16.4.2. GitHub release is not a pre-release. | Confirmed |
| Ollama | 0.40.8 | v0.40.8, `prerelease: false`, published 2026-10-21. | Confirmed |
| Qwen3 | 8B | Library tag `qwen3:8b`, 5.2GB, pull command `ollama run qwen3:8b`. | Confirmed |
| Docker Compose | 5.6.1 | v5.6.1, `prerelease: false`, published 2026-10-21. | Confirmed |
| Supabase Postgres | Pro, version managed by Supabase | Pro includes a hosted Postgres database. Free projects can pause. No self-hosted version pin is required. | Confirmed |

## Python 3.12

Confirmed. Still a supported, installable CPython line. 3.13 and 3.14 exist, and so does 3.15. That does not fail 3.12.

- https://devguide.python.org/versions/ lists branch 3.12 under Supported versions. Status: security. First release: 2023-10-02. End of life: 2028-10. PEP 693.
- The same page lists 3.13 as security (end of life 2029-10), 3.14 as bugfix (end of life 2030-10), and 3.15 as bugfix (first release 2026-10-09, end of life 2031-10). `main` is the future 3.16 and is still pre-release.
- https://www.python.org/downloads/ lists 3.12 under Active Python releases, maintenance status security, with a download link and end of support 2028-10. The same page lists Python 3.12.15 on Sept. 30, 2026, Python 3.13.17 on Oct. 21, 2026, Python 3.14.9 on Oct. 21, 2026, and Python 3.15.1 on Oct. 21, 2026.
- https://www.python.org/downloads/release/python-31215/ is the current 3.12 patch. Release date: Sept. 30, 2026. The page says this is a security release, that 3.12 only accepts security fixes in source-only form until October 2028, and that binary installers are no longer provided. It names Python 3.12.10 as the last full bugfix release that shipped binary installers. Source tarballs for 3.12.15 are on that page.
- https://www.python.org/downloads/windows/ still lists the Python 3.12.10 Windows release (April 8, 2025). The 3.12 line can be installed from that binary or from the 3.12.15 source tarball.

Note, not a failure: new Windows installers stop at 3.12.10. Security patches after that are source-only. The pin stays valid because 3.12 is still supported through October 2028 and is still installable. The scraper being copied is Python 3.12, which matches this line.

## FastAPI 0.159.1

Confirmed. The pin is a real, non-yanked PyPI release.

- https://pypi.org/pypi/fastapi/0.159.1/json reports `"version": "0.159.1"`, `"yanked": false`, `"requires_python": ">=3.10"`. Wheel `fastapi-0.159.1-py3-none-any.whl` uploaded `2026-10-21T20:59:27.580381Z`. Classifiers include Python 3.12.
- Project page: https://pypi.org/project/fastapi/0.159.1/
- https://pypi.org/pypi/fastapi/json reports the newest FastAPI release as 0.160.0, uploaded `2026-10-22T16:54:44.189628Z`, also not yanked.

Note, not a failure: 0.160.0 is one release newer than the pin. 0.159.1 is the version the spine commits, and that exact release is on PyPI.

## SQLModel 0.0.48

Confirmed. This is the current PyPI release, and it declares Python 3.12.

- https://pypi.org/pypi/sqlmodel/0.0.48/json reports `"version": "0.0.48"`, `"yanked": false`, `"requires_python": ">=3.10"`. Wheel `sqlmodel-0.0.48-py3-none-any.whl` uploaded `2026-10-06T21:44:35.326642Z`. Classifiers include Python 3.10 through 3.14, including 3.12.
- https://pypi.org/pypi/sqlmodel/json reports the same version, 0.0.48, as the latest release.
- Project page: https://pypi.org/project/sqlmodel/0.0.48/

## Next.js 16.4.2

Confirmed. Stable release. Not a canary.

- https://registry.npmjs.org/next/16.4.2 reports `"version": "16.4.2"`. The version string has no `-canary` suffix. Package name `next`. Engines: Node `>=20.9.0`.
- https://registry.npmjs.org/-/package/next/dist-tags reports `"latest": "16.4.2"` and `"canary": "16.5.0-canary.23"`. The stable dist-tag is the pinned version. The canary line is a different version.
- https://api.github.com/repos/vercel/next.js/releases/tags/v16.4.2 reports `tag_name` `v16.4.2`, `draft` false, `prerelease` false, `published_at` `2026-10-15T20:44:37Z`. Release page: https://github.com/vercel/next.js/releases/tag/v16.4.2

Note, not a failure: that GitHub release has `target_commitish` `canary`. That is the branch Next.js tags from. The release itself is not marked pre-release, and the npm `latest` tag is 16.4.2, while `canary` points at 16.5.0-canary.23.

## Ollama 0.40.8

Confirmed. Stable release. Not an RC.

- https://api.github.com/repos/ollama/ollama/releases/tags/v0.40.8 reports `tag_name` `v0.40.8`, `draft` false, `prerelease` false, `published_at` `2026-10-21T16:20:30Z`. Release page: https://github.com/ollama/ollama/releases/tag/v0.40.8
- https://api.github.com/repos/ollama/ollama/releases?per_page=5 lists, in order: `v0.40.9-rc1` (`prerelease` true, published `2026-10-22T01:33:10Z`), then `v0.40.8` (`prerelease` false).

Note, not a failure: a newer tag exists, and it is an RC. The spine pins the stable release, which is 0.40.8.

## Qwen3 8B

Confirmed. `qwen3:8b` is a real Ollama library tag a team can pull. The size was the one chosen; this review does not ask for a different model.

- https://ollama.com/library/qwen3 lists tag `qwen3:8b` at 5.2GB with a 40K context window, among the other published sizes (0.6b, 1.7b, 4b, 14b, 30b, 32b, 235b). The library page shows 58 tags and says the model was updated 1 year ago.
- https://ollama.com/library/qwen3:8b is the tag page and shows the pull command `ollama run qwen3:8b`.

The age of the tag does not remove it from the library. The page still offers the tag.

## Docker Compose 5.6.1

Confirmed. Stable GitHub release, not a pre-release.

- https://api.github.com/repos/docker/compose/releases/tags/v5.6.1 reports `tag_name` `v5.6.1`, `draft` false, `prerelease` false, `published_at` `2026-10-21T07:54:18Z`. Release page: https://github.com/docker/compose/releases/tag/v5.6.1
- The release body says it updates to go1.26.10 and includes a security fix for CVE-2026-111943.
- https://docs.docker.com/compose/releases/release-notes/ resolved to the docker/compose releases list with `v5.6.1` at the top, dated 21 Oct 07:54, commit `6cbc19a`. The GitHub API record above is the release itself.

## Supabase Postgres on Pro

Confirmed. Hosted Postgres on the paid Pro plan. The free plan can pause. The spine does not pin a self-hosted Postgres version, and this review does not require one.

- https://supabase.com/pricing says a Supabase project can be used as a standalone Postgres database, connected with any Postgres client. Pro starts at $25/month. The database comparison lists Dedicated Postgres Database as Included on Free, Pro, Team, and Enterprise. The Pausing row says Free is "After 1 week of inactivity" and Pro is "Never". The FAQ "Can I pause a free project?" answers yes: the Free plan includes 2 free projects, and paused projects are not limited to that count.
- https://supabase.com/docs/guides/platform/free-project-pausing says Supabase pauses Free Plan projects that show low activity over a 7-day period. It also says projects on a paid plan cannot be paused and are not paused for inactivity. A paid project has to move to a Free organization before it can be paused.
- https://supabase.com/docs/guides/platform/migrating-and-upgrading-projects describes Supabase upgrading the hosted database: the dashboard upgrade creates a new instance on the current Supabase Postgres and copies data with `pg_upgrade`. Upgrade notes on that page name Postgres 15 and Postgres 17, including minor lines 15.19 and 17.11. The version a new project receives is the one Supabase is shipping, and existing projects move when the project is upgraded. That matches "bản Postgres do Supabase quản lý".

## Mismatches

None.

## Unconfirmed

None. Each row above has a fetched official URL and the version or plan fact quoted from it.

## Not failures

- Python 3.13, 3.14, and 3.15 are also current lines. 3.12 remains in security support through October 2028. Patches after 3.12.10 are source-only.
- FastAPI 0.160.0 is newer than the committed 0.159.1. The committed release is published and not yanked.
- Ollama v0.40.9-rc1 is newer than v0.40.8 and is a pre-release. v0.40.8 is the stable release.
- Next.js canary 16.5.0-canary.23 exists. npm `latest` is 16.4.2.
