# Tasks: Tìm kỹ năng bằng tiếng Anh và tiếng Việt

**Input**: `specs/207-tim-ky-nang-song-ngu/`

**Tests**: Viết trước theo `tdd.md`.

## Phase 1: Test

- [x] T001 Test `foldText`, `searchSkills` ("học máy", "hoc may", "HỌC MÁY", "machine", "ml", "reactjs"; thứ tự; trần 8), trong `web/tests/fr13-tim-ky-nang-song-ngu.test.tsx`
- [x] T002 Test màn: gõ "học máy" → tick Machine Learning → vào hồ sơ; không kết quả; ô trống

## Phase 2: Implementation

- [x] T003 `web/lib/vocab.ts`
- [x] T004 `skill-search.tsx` và nối vào màn hồ sơ kỹ năng
