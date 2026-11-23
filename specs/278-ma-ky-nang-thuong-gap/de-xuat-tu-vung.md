# Đề xuất từ vựng cho #278 (chờ duyệt)

Nguồn: `tools/vocab/skill_gaps.py` trên snapshot 2026-11-20 (4.688 tin IT trong cửa sổ 60 ngày, 4.622 tin có thẻ kỹ năng). 673 kỹ năng có từ 20 tin trở lên; 369 đã có mã; 304 chưa có mã, xử lý như dưới đây.

Ký hiệu *(không quét)*: cách viết chỉ dùng để tra thẻ của site, không dùng để quét văn bản JD (`scan_skip`), vì trong văn bản nó quá chung.

Tóm tắt: 67 thẻ vào 40 mã mới, 73 thẻ thành cách viết của mã có sẵn, 6 thẻ ghép, 158 thẻ loại trừ có lý do.

## 1. Mã mới

| Mã | Tên (en / vi) | Thẻ gắn vào (số tin) |
|---|---|---|
| `devops` | DevOps / DevOps | DevOps (149) |
| `data_science` | Data science / Khoa học dữ liệu | Data Science (142) |
| `artificial_intelligence` | Artificial intelligence / Trí tuệ nhân tạo | AI (195) *(không quét)*, Artificial Intelligence (AI) (80) |
| `cloud_computing` | Cloud computing / Điện toán đám mây | Cloud (153) *(không quét)* |
| `api` | API development / Phát triển API | API (197) *(không quét)*, APIs (61) *(không quét)*, API Gateway (28), API design (23), tích hợp API (22), webhook (21) |
| `http` | HTTP / HTTP | HTTP (26) *(không quét)*, HTTP/HTTPS (26) |
| `tls` | TLS/SSL / TLS/SSL | TLS (22), SSL/TLS (21) |
| `databases` | Databases / Cơ sở dữ liệu | Database (102) *(không quét)*, cơ sở dữ liệu (69), databases (35) *(không quét)*, relational databases (28), RDBMS (24) |
| `windows` | Windows / Windows | Windows (97) *(không quét)* |
| `macos` | macOS / macOS | macOS (20) |
| `operating_systems` | Operating systems / Hệ điều hành | hệ điều hành (21) |
| `code_review` | Code review / Review code | code review (88), code reviews (37), review code (29) |
| `stakeholder_management` | Stakeholder management / Quản lý các bên liên quan | stakeholder management (84) |
| `game_development` | Game development / Phát triển game | Game Development (80) |
| `json` | JSON / JSON | JSON (75) |
| `xml` | XML / XML | XML (25) |
| `sast_dast` | SAST/DAST / Kiểm thử bảo mật SAST/DAST | SAST (22), DAST (21) |
| `sdlc` | SDLC / Quy trình phát triển phần mềm | SDLC (70), quy trình phát triển phần mềm (31) |
| `troubleshooting` | Troubleshooting / Xử lý sự cố | troubleshooting (68), xử lý sự cố (58), phân tích log (22) |
| `debugging` | Debugging / Gỡ lỗi | debugging (43), debug (27) *(không quét)* |
| `integration_testing` | Integration testing / Kiểm thử tích hợp | integration testing (48), integration test (47) *(không quét)*, kiểm thử tích hợp (25) |
| `workflow_automation` | Workflow automation / Tự động hóa quy trình | Power Automate (33), n8n (25) |
| `big_data` | Big data / Dữ liệu lớn | Big Data (33) |
| `system_administration` | System administration / Quản trị hệ thống | quản trị hệ thống (41), System Admin (32), IT Infrastructure (31), System Administration (28), IT Operations (20) |
| `risk_management` | Risk management / Quản lý rủi ro | risk management (33), quản lý rủi ro (26) |
| `presentation` | Presentation / Thuyết trình | thuyết trình (29) |
| `technical_writing` | Technical writing / Viết tài liệu kỹ thuật | viết tài liệu (29), documentation (20) *(không quét)*, technical documentation (20) |
| `analytical_thinking` | Analytical thinking / Tư duy phân tích | tư duy hệ thống (35), analytical skills (29), logical thinking (20) |
| `independent_work` | Working independently / Làm việc độc lập | làm việc độc lập (26) |
| `market_research` | Market research / Nghiên cứu thị trường | Market Research and Analysis (56) |
| `core_banking` | Core banking / Core banking | Core Banking (21) |
| `mes` | Manufacturing execution system (MES) / Hệ thống điều hành sản xuất (MES) | MES (25) *(không quét)* |
| `can_bus` | CAN bus / CAN bus | CAN (22) *(không quét)* |
| `concurrency` | Concurrency / Lập trình đồng thời | concurrency (26) *(không quét)* |
| `memory_management` | Memory management / Quản lý bộ nhớ | memory management (20) |
| `performance_optimization` | Performance optimization / Tối ưu hiệu năng | performance optimization (22) |
| `scripting` | Scripting / Viết script | scripting (23) *(không quét)* |
| `infrastructure_as_code` | Infrastructure as code / Hạ tầng dưới dạng mã (IaC) | Infrastructure as Code (IaC) (22) |
| `system_integration` | System integration / Tích hợp hệ thống | tích hợp hệ thống (29), system integration (27) |
| `process_quality_assurance` | Process quality assurance / Đảm bảo chất lượng quy trình (PQA) | Process Quality Assurance (PQA) (22) |

## 2. Thêm cách viết vào mã có sẵn

| Mã | Thẻ thêm vào (số tin) |
|---|---|
| `agile` | Agile methodologies (28) |
| `ai_agent` | Agentic AI (26), MCP (21) |
| `backup` | backup/restore (28) |
| `business_analysis` | phân tích yêu cầu nghiệp vụ (22) |
| `ci_cd` | CI/CD pipelines (73), Azure DevOps (48) |
| `communication` | Giao tiếp tốt (37) |
| `cybersecurity` | Security (74) *(không quét)*, bảo mật (36), Cloud Security (35), bảo mật hệ thống (29), Vulnerability Management (23), Application Security (21) |
| `data_analysis` | xử lý dữ liệu (27) |
| `design_patterns` | MVC (40), Dependency Injection (20) |
| `docker` | Container (31) *(không quét)* |
| `edr` | Endpoint Security (22) |
| `english` | đọc hiểu tài liệu tiếng Anh (39), đọc hiểu tài liệu kỹ thuật tiếng Anh (30) |
| `etl` | ETL/ELT (47) |
| `helpdesk` | IT Support (41) |
| `iam` | authentication (26) *(không quét)*, phân quyền (24), access control (21) *(không quét)* |
| `itil` | Incident Management (24), Change Management (21) |
| `javascript` | AJAX (20) |
| `leadership` | Team Management (29) |
| `ms_office` | Word (31) *(không quét)* |
| `networking` | Switch (55) *(không quét)*, Router (53) *(không quét)*, Wi-Fi (48), VPC (29), WiFi (28), LAN (26) *(không quét)*, Wireshark (24), Ethernet (23), NAT (22) *(không quét)* |
| `observability` | monitoring (86) *(không quét)*, logging (46) *(không quét)*, CloudWatch (26) |
| `oop` | lập trình hướng đối tượng (OOP) (25) |
| `problem_solving` | problem-solving skills (31) |
| `project_management` | IT Project Management (116), lập kế hoạch (33), MS Project (25) |
| `regression` | Regression (21) *(không quét)* |
| `rest_api` | REST (40) *(không quét)* |
| `siem` | SOC (22) *(không quét)*, MITRE ATT&CK (21) |
| `software_architecture` | Software Design (79), event-driven architecture (39), System Architecture (35), Solution Architecture (27), kiến trúc hệ thống (21), Enterprise Architecture (20) |
| `software_testing` | QA QC (58) |
| `solid` | SOLID (54) *(không quét)* |
| `sql` | SQL cơ bản (21) |
| `sql_server` | MS SQL Server (28) |
| `system_design` | High Availability (24) |
| `ui_design` | UI/UX Design (63), prototype (40) *(không quét)*, Design Systems (21) |
| `unit_testing` | JUnit (31) |
| `virtualization` | OpenStack (20) |

## 3. Thẻ ghép (một thẻ là hai kỹ năng)

| Thẻ (số tin) | Tách thành |
|---|---|
| Agile/Scrum (244) | agile + scrum |
| JavaScript/TypeScript (41) | javascript + typescript |
| HTML/CSS (35) | html + css |
| AI/ML (27) | artificial intelligence + machine learning |
| Agile Scrum (23) | agile + scrum |
| C#/.NET (20) | c# + .net |

## 4. Loại trừ

| Lý do | Số thẻ | Ví dụ (số tin) |
|---|---|---|
| địa điểm, không phải kỹ năng | 81 | Hà Nội (1426), Bà Rịa-Vũng Tàu (519), Bình Dương (519), Hồ Chí Minh (519), Phường Cầu Giấy - Hà Nội (290), Phường Thanh Xuân - Hà Nội (184), Phường Từ Liêm - Hà Nội (183), Phường Yên Hòa - Hà Nội (146) … |
| chức danh; thêm làm bí danh sẽ khớp tên vai trò trong JD và thổi phồng tỷ lệ | 21 | Software Engineer (111), Backend Developer (96), Fullstack Developer (81), Data Engineer (78), IT Project Manager (78), AI Engineer (74), DevOps Engineer (74), System Engineer (59) … |
| thẻ ngành nghề hoặc danh mục của site, không phải kỹ năng | 20 | Công nghệ Thông tin (2037), IT Infrastructure and Operations (365), Công nghệ thông tin khác (151), Business Analyst (Phân tích nghiệp vụ) (146), Product Owner/Product Manager (117), Chuyên môn Công nghệ thông tin khác (108), Điện/Điện tử/Viễn thông (84), IT Helpdesk/IT support (83) … |
| thẻ danh mục của TopCV ("Việc làm … tại …"), không phải kỹ năng | 13 | Việc làm IT (2003), Việc làm Business Analyst tại Hà Nội (69), Việc làm Product Owner tại Hà Nội (51), Việc làm Trưởng Nhóm tại Hà Nội (45), Việc làm DevOps Engineer tại Hà Nội (32), Việc làm Project Manager tại Hà Nội (32), Việc làm Data Engineer tại Hà Nội (27), Việc làm Engineer tại Hà Nội (25) … |
| quá chung | 9 | lập trình (40), Storage (34), Server (33), software development (33), phát triển phần mềm (29), transaction (27), Integration (22), máy chủ (22) … |
| chỉ một nguồn (ITnavi) gắn, nghi là thẻ gắn tự động; xem lại khi có nguồn khác | 4 | Embedded JavaScript (EJS) (52), Azure SQL Data Warehouse (42), Biopython (29), IBM Rational Functional Tester (20) |
| quá chung (kiểm thử tự động hay tự động hóa quy trình?) | 2 | Automation (55), tự động hóa (21) |
| lĩnh vực, không phải một kỹ năng | 1 | Software Engineering (359) |
| quá chung (thiết kế gì?) | 1 | Thiết kế (122) |
| quá chung; kiểm thử cụ thể đã có mã | 1 | testing (40) |
| mảng việc, trùng với vai trò Backend | 1 | Backend (35) |
| mảng việc, trùng với vai trò Fullstack | 1 | Fullstack (28) |
| quá hẹp, thuộc kỹ năng lập trình cơ bản | 1 | exception handling (25) |
| quá chung (công cụ BI cụ thể đã có mã) | 1 | dashboard (24) |
| nền tảng học vấn, không phải kỹ năng | 1 | Computer Science (20) |

## Sửa kèm

- `solid`: bí danh đang là `"solid, "` (dư dấu phẩy) nên thẻ "SOLID" (54 tin) không khớp; sửa thành `solid`.
