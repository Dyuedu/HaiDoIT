# Research: Toàn cảnh thị trường trên Insights

## Tham khảo

- Our World in Data grapher, bảng đi cùng biểu đồ: https://github.com/owid/owid-grapher/blob/c94293a6db2ed50486f8f6014072fb0b2cf13edb/packages/@ourworldindata/grapher/src/dataTable/DataTable.tsx
  - Lấy: mỗi biểu đồ có một bảng cùng bộ số để đọc chính xác và cho trình đọc màn hình.
  - Không lấy: bảng có sắp xếp và lọc tại chỗ (web không sắp xếp, AD-22).
- 18F Content Guide (đã dùng ở #324), nhãn giao diện dùng chữ số và `%`: https://github.com/18F/content-guide/blob/1b1723d3d5b8f91d92c16487c88b56265dc0ec3a/_pages/our-style/numbers-and-percentages.md
- Mockup tương tác của chính dự án (artifact ngày 2026-11-19, số thật snapshot 19/11): bố cục, bảng màu đã kiểm, cách vẽ biểu đồ tròn 3D bằng canvas (vẽ lớp thành, mặt trên, miếng phía sau trước).

## Quyết định

- Không dùng thư viện biểu đồ: Highcharts có biểu đồ tròn 3D nhưng cần giấy phép thương mại; ECharts không có tròn 3D. Biểu đồ tròn tự vẽ khoảng 200 dòng.
- Thanh và cột vẽ bằng HTML/CSS thay vì SVG như mockup: tự co giãn ở 360 px, chữ không bị thu nhỏ theo `viewBox`, và đọc được bằng trình đọc màn hình như một danh sách.
- Biểu đồ hai phía theo thứ tự `roles` của API (nhiều tin trước), không theo độ lệch Hà Nội/TP.HCM như mockup, vì web không sắp xếp.
