# CLAUDE.md

## Cách làm việc

- Khi thực hiện một chức năng chưa quen, không làm từ con số 0. Trước tiên, hãy research các repo GitHub public để so sánh ý tưởng và tham khảo cách làm, rồi mới bắt tay vào làm.
- Yêu cầu của việc cần làm là issue trên GitHub. Thiết kế và nhật ký test của issue nằm trong `specs/` (xem mục SDD và TDD). Không tạo hoặc cập nhật spec trong `_bmad-output/`. Thư mục `_bmad-output/` là lưu trữ tài liệu kế hoạch cũ. Phần máy BMAD (`_bmad/`, skill `bmad-*`) đã gỡ.

## SDD và TDD

**Khi bắt đầu một issue.** Trước khi viết code, tạo thư mục `specs/<số issue>-<slug>/` (ví dụ `specs/262-bat-deploy/`) gồm:

| File | Viết theo |
|---|---|
| `spec.md` | `docs/templates/spec-driven-sdd/spec-template.md`. Dòng `Input` trỏ tới issue. Mỗi AC của issue phải có một scenario tương ứng. |
| `plan.md` | `docs/templates/spec-driven-sdd/plan-template.md`. Liệt kê các file code và test sẽ sửa. |
| `tasks.md` | `docs/templates/spec-driven-sdd/tasks-template.md`. Task test đứng trước task code. |
| `research.md` | Kết quả research repo GitHub public (xem "Cách làm việc"): link có commit, lấy gì, không lấy gì và vì sao. |
| `data-model.md` | Bảng, cột, revision Alembic thay đổi. Không đổi thì ghi rõ là không đổi. |
| `tdd.md` | `docs/templates/test-driven-tdd/test-driven-development.md`. Ghi lệnh test, danh sách hành vi, kết quả RED (bao nhiêu fail và vì sao), rồi kết quả GREEN. |

Bỏ các chỉ dẫn và lệnh riêng của Spec Kit trong template. Given/When/Then trong `spec.md` được dùng; quy định cấm Given/When/Then chỉ áp dụng cho thân issue.

**Làm theo TDD.** Viết test trước, chạy cho thấy đỏ, ghi kết quả RED vào `tdd.md`, rồi mới sửa code cho xanh và ghi GREEN. Không ghi RED mà chưa chạy thật.

**Khi sửa code thuộc một issue đã có spec.** Trước khi sửa một file, tìm các issue đã đụng tới nó:

- `git log --format='%h %s' -- <file>` và lấy các số `#N` trong commit message;
- tìm đường dẫn file trong `specs/*/plan.md` và `specs/*/tasks.md`.

Với mỗi issue tìm được mà có thư mục `specs/`, cập nhật cùng commit với code:

- `spec.md`: hành vi hoặc scenario đã đổi, và dòng `Status`;
- `plan.md`, `tasks.md`, `data-model.md`: file, task, schema thay đổi;
- `tdd.md`: thêm một đợt RED/GREEN mới có ngày và lý do sửa, không xóa các đợt cũ.

Nếu thay đổi làm một AC của issue không còn đúng thì dừng lại và báo người dùng, không lặng lẽ sửa spec cho khớp code. Issue cũ chưa có thư mục `specs/` thì không bắt buộc dựng lại, nhưng phải ghi tên issue đó trong mô tả PR.

## Backlog

**User story.** Một kết quả mà người dùng nhận ra sau một lần mở sản phẩm. Phạm vi là một lần dùng và một kết quả họ kể được. Không gồm bước bên trong (tính tỷ trọng, gán nhãn, chống trùng), không gồm nghĩa vụ của nhóm (trang chính sách, xin phép nguồn, cổng CI), và không chia theo file hay theo sprint. Xong khi người đó làm được việc và thấy kết quả. Trên GitHub giữ nhãn `type:story`. Thân issue viết bằng tiếng Anh:

```
## Description

As a <role>,
I want <kết quả của một lần mở sản phẩm>,
so that <lợi ích người đó kể được>.

## Acceptance Criteria

- [ ] điều kiện kiểm được

## Tasks

- [ ] #số <tên task>
```

Story không có task con thì bỏ mục `## Tasks`.

**Product backlog.** Mọi issue đang mở mà nhóm vẫn định làm: story chưa xong, task của các story đó, và task ràng buộc. Phạm vi là việc còn lại của sản phẩm, không phải issue đã đóng, không phải file trong `_bmad-output/`, không phải ý tưởng chưa thành issue. Thứ tự nhìn theo chuyện người dùng thấy trước, rồi mới tới task phục vụ chuyện đó.

**Sprint backlog.** Những issue nằm trong milestone của một tuần. Phạm vi là story sẽ demo được cuối tuần đó, các task thiếu thì story chưa thành thật, và task ràng buộc đến hạn trong tuần. Không đưa story của tuần sau vào cho đủ chỗ. Không đổi nhãn một task thành story để nó xuất hiện như cam kết với người dùng.

**Task.** Một việc một người làm xong để một story thành thật, hoặc để giữ một ràng buộc của dự án. Phạm vi dừng ở việc đó: thân issue nói việc gì phải đúng và nó phục vụ story nào. Task không có câu "I want" của người dùng, và không tự là thứ mang ra demo. Trên GitHub dùng nhãn `type:chore`. Thân issue viết bằng tiếng Anh:

```
## Description

Một hoặc hai câu: việc gì phải đúng.

## Acceptance Criteria

- [ ] điều kiện kiểm được

## Serves

- #số story
```

Task ràng buộc không phục vụ một story thì thay `## Serves` bằng `## Due` và ghi mốc nó cần xong. Không dùng Given/When/Then. Definition of Done là checklist chung, không chép vào từng issue. Ưu tiên nằm ở nhãn, sprint nằm ở milestone.

## Git

- Commit message và mô tả PR viết bằng tiếng Anh, theo `.github/pull_request_template.md`. Các file trong `specs/` (SDD, TDD) vẫn viết tiếng Việt.
- Khi tạo commit, KHÔNG thêm dòng `Co-Authored-By` (kể cả `Co-Authored-By: Claude ...`) vào commit message.
