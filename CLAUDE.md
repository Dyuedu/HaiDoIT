# CLAUDE.md

## Cách làm việc

- Khi thực hiện một chức năng chưa quen, không làm từ con số 0. Trước tiên, hãy research các repo GitHub public để so sánh ý tưởng và tham khảo cách làm, rồi mới bắt tay vào làm.
- Spec của việc cần làm là issue trên GitHub. Không tạo hoặc cập nhật spec trong `_bmad-output/`. Thư mục `_bmad-output/` là lưu trữ tài liệu kế hoạch cũ. Phần máy BMAD (`_bmad/`, skill `bmad-*`) đã gỡ.

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

- Khi tạo commit, KHÔNG thêm dòng `Co-Authored-By` (kể cả `Co-Authored-By: Claude ...`) vào commit message.
