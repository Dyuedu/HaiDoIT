# Research: Màn lộ trình học theo chặng

## Quyết định

- Cột chặng ở giữa, kỹ năng hai bên, đường cong nét đứt: cách trình bày của roadmap.sh. Không lấy nội dung, màu hay hình của họ; dùng token của DESIGN.md.
- Chặng và thứ tự đã có từ API nên không cần thư viện xếp đồ thị.
- Một DOM, dưới `lg` thành danh sách bằng CSS.
- Ngăn chi tiết không modal; số ở ô riêng, lời dẫn viết sẵn.

## Các repo công khai đã đọc

- [andrico1234/beautiful-skill-tree @ b77551e, `src/components/SkillEdge.tsx`](https://github.com/andrico1234/beautiful-skill-tree/blob/b77551e24c4417cbd84d7fc5930d5fb5c957f16a/src/components/SkillEdge.tsx) (GPL-3.0): đo `getBoundingClientRect` mỗi lần đổi cỡ cửa sổ để vẽ đường nối. **Không lấy mã** (GPL) và **không lấy cách đo DOM**: lệch khi đổi cỡ chữ, không vẽ được trên server. [`src/hooks/useMobile.tsx`](https://github.com/andrico1234/beautiful-skill-tree/blob/b77551e24c4417cbd84d7fc5930d5fb5c957f16a/src/hooks/useMobile.tsx) đổi bố cục bằng JS theo bề rộng; không lấy vì nháy khi hydrate, CSS đủ.
- [bardia1122/Devpath @ d62e666](https://github.com/bardia1122/Devpath/tree/d62e66658aebdf6af70757c014e24498da1e1d86) (MIT, 2 sao): `lib/layout.ts` xếp theo chuỗi tiên quyết dài nhất (cùng ý với chặng của API #212, nên web không làm lại); `components/roadmap/SkillDrawer.tsx` là ngăn bên có nhãn nhóm, trạng thái, danh sách tài liệu mở tab mới với `rel="noopener noreferrer"`. **Lấy ý**: ngăn bên, nút đã có mờ tên đi và có dấu tick. **Không lấy**: React Flow (thêm gói, canvas kéo thả không dùng được bằng bàn phím và điện thoại), sắp nút theo tên (trái FR-22).
- [Preptics/SkillTreeOSS @ b060d2a, `components/canvas/NodeSidebar.tsx`](https://github.com/Preptics/SkillTreeOSS/blob/b060d2a3c3fcb4d9d35eeadb6c00b57dd71475f9/components/canvas/NodeSidebar.tsx) (MIT): ngăn bên liệt kê kỹ năng cần học trước. **Lấy ý**: bấm kỹ năng cần học trước thì chuyển ngăn sang nó. **Không lấy**: framer-motion, tự sắp topo ở trình duyệt (AD-7).
- [nilbuild/developer-roadmap @ 624438e](https://github.com/nilbuild/developer-roadmap/tree/624438ea4e82121ac3d109c75b225b996fc3efa0) (giấy phép riêng): ở commit này chỉ còn nội dung, không còn mã màn hình. Chỉ lấy cách trình bày nhìn thấy trên trang; không lấy nội dung.
- [dagrejs/dagre](https://github.com/dagrejs/dagre), [erikbrinkman/d3-dag](https://github.com/erikbrinkman/d3-dag) (MIT): xếp đồ thị tổng quát, chỉ xem mô tả, không đọc mã. Không cần vì chặng đã có sẵn.

## Đợt 4 (2026-11-25): chủ đề và cụm chọn một

- Ảnh chụp trang Backend của roadmap.sh: trục giữa là chủ đề, nhánh là ô nhỏ hai cột, đường chấm, cụm lựa chọn trong khung. Lấy cách trình bày; không lấy danh sách chủ đề, nội dung, màu vàng hay phông chữ.
- [exercism/javascript @ e9f371a, `config.json`](https://github.com/exercism/javascript/blob/e9f371a689e9393d0903b944da8a2d3deb4a7841/config.json): chỉ xem đầu file; bài học khai báo theo khái niệm trong JSON. Cùng ý với `topics`; không lấy mã hay dữ liệu.
- Chặng chọn một: tự thiết kế (`choose_one` trên chặng), không thấy repo nào trong các repo đã đọc có sẵn.
