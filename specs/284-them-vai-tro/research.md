# Research: danh sách vai trò IT trong repo public

Ngày 13/11/2026.

## kamranahmedse/developer-roadmap (roadmap.sh)

- Link: https://github.com/kamranahmedse/developer-roadmap/tree/01df46b9a27762e8dfafaecaa6ecfb8ed10fa870/roadmaps
- Cách làm: mỗi vai trò có một roadmap riêng. Các roadmap theo vai trò (khác roadmap theo công nghệ như `react`, `docker`):
  `frontend`, `backend`, `full-stack`, `devops`, `qa`, `cyber-security`, `data-analyst`, `bi-analyst`, `data-engineer`,
  `ai-data-scientist`, `ai-engineer`, `mlops`, `android`, `ios`, `game-developer`, `product-manager`, `product-design`,
  `network-engineer`, `engineering-manager`, `devrel`.
- Lấy: tách Fullstack, Security, Data Scientist, Game, Product (PM/PO), Product design (UI/UX) thành vai trò riêng; bước
  Cố vấn của dự án theo kiểu roadmap.sh, nên mã vai trò khớp nhóm roadmap giúp nối vai trò với lộ trình sau này.
- Không lấy: tách nhỏ theo công nghệ (Android/iOS, BI/Data Analyst, AI Engineer/MLOps) ở mức vai trò của bản đồ: #283 đo
  được nhiều nhóm như vậy dưới 30 tin mỗi thành phố; chúng đi vào chức danh con (`branch`) cho #286. Không lấy riêng
  `network-engineer`: dữ liệu Việt Nam gộp quản trị mạng, quản trị hệ thống, helpdesk dưới cùng nhóm "IT" (526 tin ở
  snapshot 12/11), tách ra thì mỗi nhóm đều mỏng.

## Dữ liệu của #283 (bản sao local, snapshot 12/11/2026, đếm theo tin)

BA/PO/PM 843, Hạ tầng/IT support 526, Security 192, Fullstack 186, Game 99, UI/UX 78, Data Scientist 29. Bảy nhóm này nay
nằm trong Other (báo cáo qua `report_as`), khiến Other lên 2044 cụm trên 3748 cụm IT.
