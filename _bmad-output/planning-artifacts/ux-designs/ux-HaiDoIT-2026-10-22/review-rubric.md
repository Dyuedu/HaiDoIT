# Spine Pair Review — Hải Đồ IT

## Overall verdict

Hai bản là hợp đồng đọc được. Bốn hành trình UJ-1 đến UJ-4 có người, các bước, một nhịp đỉnh và một đường trật; 28 màu đều có mã hex; 27 tên trong mục thành phần của hai bản khớp nhau. Người làm kiến trúc hoặc story vẫn không dựng được chỗ gắn dấu «đã có» trên bản đồ, bảng xếp hạng, và trạng thái lỗi dữ liệu của Học gì tiếp? với Soi tin. Hai bản còn lệch nhau về «bảng thành phố» trên Học gì tiếp?. Ảnh minh họa chưa được gắn, đúng với đường nhanh đã để màn hình chính sang bước sau.

## 1. Flow coverage — strong

Đã đối chiếu bốn tên trong EXPERIENCE.md, mục Key Flows, với mục 3.4 của PRD. UJ-1 (Lan), UJ-2 (Lan), UJ-3 (Khoa) và UJ-4 (Mai) đều có người được gọi tên, các bước đánh số, một nhịp đánh dấu **Đỉnh**, và một đoạn «Khi trật». UJ-1 có ô mẫu mỏng và email không gửi được. UJ-2 có ngày thứ 15, email chưa từng lưu, và một email một lộ trình. UJ-3 có lương dưới ngưỡng và nội dung dán nhầm. UJ-4 có offer thiếu ô, ngày remote, và việc đóng trang. FR-1 đến FR-18 không cần một luồng riêng: hành vi của từng FR nằm trong một bước của bốn luồng này, hoặc trong một hàng thành phần, hoặc trong một hàng trạng thái.

### Findings

Không có chỗ hổng ở bốn hành trình.

## 2. Token completeness — adequate

Frontmatter của DESIGN.md có 28 màu, 11 vai chữ, 5 bán kính, 12 khoảng cách, và 6 token thành phần. Mọi màu là chuỗi hex sáu ký tự. Mặt sáng không áp dụng: Brand & Style ghi giả định kỳ này chỉ dùng mặt tối. Mọi đường `{colors…}`, `{typography…}`, `{spacing…}`, `{rounded…}` và `{components…}` trong cả hai bản trỏ tới một token đã khai. Ba cặp tương phản được nêu ở mục Colors: chữ `{colors.ink}` trên `{colors.surface}`, chữ `{colors.ink-on-accent}` trên `{colors.accent-hot}`, chữ `{colors.warning-ink}` trên `{colors.warning-surface}`.

### Findings

- **medium** Vài cặp chữ chịu lực chưa có mục tiêu tương phản, trong khi Accessibility Floor giao việc đó cho mục Colors. Thiếu chữ `{colors.ink}` trên `{colors.surface-card}` (thẻ thành phố, thẻ chặng, panel offer), chữ `{colors.accent-hot}` khi nó là số lương và dấu «đã có», chữ `{colors.ink-lead}` trên `{colors.surface}` (Accessibility Floor gọi đây là chữ bắt buộc), chữ `{colors.ink-on-accent}` trên `{colors.ink}` (chip vai trò đang bật, token `chip-selected`), và chữ `{colors.toast-ink}` trên `{colors.toast-surface}`. Nút Vì sao? chỉ nói «chữ mono màu gần `{colors.accent-cold}`», nên màu chữ của nút đó chưa phải một token (DESIGN.md, Colors; Components, Nút Vì sao?; EXPERIENCE.md, Accessibility Floor). *Fix:* liệt kê từng cặp chữ-nền chịu lực với mục tiêu WCAG 2.2 AA, và gán Nút Vì sao? đúng một token chữ.
- **medium** Độ đục của lưới bản đồ («rất thấp»), của header dính («cao»), và của bóng nút chính khi hover («thấp») không có token. Lớp mờ của ngăn Vì sao? (`rgba(3,6,9,.7)`) và bóng toast (`rgba(0,0,0,.5)`) thì đã có số (DESIGN.md, Colors, Layout & Spacing, Elevation & Depth). *Fix:* ghi ba độ đục còn lại thành token hoặc thành giá trị rgba trong frontmatter.
- **low** Bốn màu không có chỗ dùng: `{colors.ink-card}`, `{colors.danger-ink}`, `{colors.danger-surface}`, `{colors.danger-border}`. Mục Colors chỉ cấm dùng `{colors.danger}` như một điểm tin cậy (DESIGN.md, frontmatter `colors`). *Fix:* xóa bốn token này, hoặc ghi một câu cấm dùng cho từng token.

## 3. Component coverage — adequate

Hai mục thành phần cùng 27 tên: Logo, Thanh điều hướng, Viên hồ sơ phiên, Lớp chào, Chip vai trò, Tầm nhìn, Cột thành phố, Thẻ thành phố, Ô lương đầu trang, Dấu đã có, Khối xu hướng tám quý, Nút chính, Nút phụ, Nút Vì sao?, Ngăn Vì sao?, Nút báo nguồn, Chip kỹ năng, Danh nên học tiếp, Thẻ chặng, Ô email, Ô nhận lại liên kết, Panel offer, Thanh thực nhận, Hộp hụt bảo hiểm, Kết quả soi tin, Toast, Khối trạng thái. Hầu hết hàng có quy tắc dùng được: điều kiện hiện, câu trên màn, và việc bấm làm gì. Chip kỹ năng, Danh nên học tiếp, Thẻ chặng, Panel offer, Kết quả soi tin và Khối trạng thái đủ để viết tiêu chí chấp nhận.

### Findings

- **high** Dấu «đã có» không có danh chứa trên Bản đồ nhu cầu. Hàng Dấu đã có nói dấu rơi vào kỹ năng của hồ sơ phiên. Thẻ thành phố chỉ có ba tab Cơ cấu, Lương, Dự báo. Chip kỹ năng chỉ dùng ở Học gì tiếp? và lộ trình. Đỉnh của UJ-2 là Python và SQL còn dấu trên bản đồ, nên người đọc không biết danh đó nằm ở đâu trên màn (DESIGN.md, Components, Thẻ thành phố và Dấu đã có; EXPERIENCE.md, Component Patterns, Dấu đã có; Key Flows, UJ-2). *Fix:* thêm một thành phần cho danh kỹ năng của thành phố, có mặt nhìn ở DESIGN.md và quy tắc gắn hoặc gỡ dấu ở EXPERIENCE.md.
- **high** «Bảng xếp hạng» và «hàng xếp hạng» được gọi tên và bấm được, nhưng không có hàng thành phần. Cột thành phố nói bấm hàng xếp hạng thì chọn thành phố. Khối xu hướng tám quý nói nó nằm dưới bảng đó. Người đọc không thấy cột, thứ tự, hay số nào được phép hiện trên bảng (DESIGN.md, Components, Khối xu hướng tám quý; EXPERIENCE.md, Component Patterns, Cột thành phố). *Fix:* thêm hàng Bảng xếp hạng với các cột còn lại sau khi đã cắt số bị cấm, và với quy tắc bấm một hàng thì chọn đúng thành phố đó.
- **medium** Nút thế khối và nút thế phẳng chỉ xuất hiện trong giả định ở Elevation & Depth. Interaction Primitives đã chốt thế khối trên máy bàn, thế phẳng trên điện thoại và khi giảm chuyển động, cùng thao tác kéo. Nhãn, vị trí và kiểu của hai nút thì chưa có hàng (DESIGN.md, Elevation & Depth; EXPERIENCE.md, Interaction Primitives). *Fix:* thêm hàng cho cụm hai nút, hoặc ghi rằng hai thế chỉ đổi bằng kéo và bằng quy tắc bề rộng, không có nút riêng.
- **medium** Hàng Khối xu hướng tám quý ở EXPERIENCE.md chỉ nói khối đọc lớp xu hướng và không phải một màn. Mặt nhìn có màu cột tăng, giảm và đi ngang. Người đọc không thấy khối hiện những kỹ năng nào, nhãn trục là gì, bấm cột thì chuyện gì xảy ra, và khối trống thì câu nào hiện (EXPERIENCE.md, Component Patterns, Khối xu hướng tám quý; DESIGN.md, Components, cùng tên). *Fix:* viết quy tắc nội dung, tương tác và trạng thái rỗng vào hàng đó. Quy tắc «kỹ năng đang giảm không đứng hạng nhất» đã có ở Danh nên học tiếp, giữ nguyên ở đó.

## 4. State coverage — adequate

Năm bề mặt trong Information Architecture đã được đi hết.

Bản đồ nhu cầu có mở lần đầu, đang tải, lỗi nguồn, hết tin, lương ẩn, chưa có tín hiệu, mất mạng, và giảm chuyển động. Chưa chọn thành phố nằm trong mở lần đầu.

Học gì tiếp? có chưa đủ hồ sơ, chưa có kỹ năng giả định, đã thêm kỹ năng, đã xóa kịch bản, và lương ẩn dùng chung.

Lộ trình 90 ngày có chưa đủ hồ sơ, chưa tạo, đã hiện mà chưa lưu, lưu được, lưu lỗi, mở lại đúng liên kết, và máy khác chưa có liên kết.

So sánh offer có thiếu ô, đủ ô, và đóng bảo hiểm trên mức thấp. Công cụ không lưu trên máy chủ. Từ chối quyền được ghi là không áp dụng, vì không có hồ sơ công khai và không có vai trò bị chặn.

Soi tin có chưa dán, link có trong dữ liệu, link không có, và lương ẩn dùng chung.

Focus được gom một lần: thứ tự Tab, Escape đóng lớp trên cùng, và viền focus 2px màu `{colors.accent-hot}`. Cách gom đó đủ cho mọi bề mặt, vì không có chế độ focus riêng.

### Findings

- **high** Học gì tiếp? và Soi tin không có đang tải, lỗi nguồn, và mất mạng. Cả hai mở thẳng từ thanh điều hướng và đều đọc dữ liệu thị trường. Nút phụ nói «Thử lại» gọi lại nguồn trên Học gì tiếp?, nhưng bảng trạng thái chỉ gắn câu «Không tải được dữ liệu thị trường.» với Bản đồ nhu cầu. UJ-3 khi trật chỉ nói thiếu mẫu lương và không xin nguyên văn mô tả (EXPERIENCE.md, Component Patterns, Nút phụ; State Patterns, Đang tải, Lỗi nguồn, Mất mạng; Key Flows, UJ-3). *Fix:* thêm ba trạng thái đó cho từng bề mặt, dùng lại câu và nút của bản đồ nếu cách xử lý giống nhau, hoặc ghi rõ Học gì tiếp? chỉ đọc số đã tải ở bản đồ.
- **medium** Mở liên kết lộ trình chỉ có trạng thái thành công và trạng thái email chưa từng lưu. Chưa có đang tải khi liên kết đang được đọc, và chưa có câu khi máy chủ không trả lộ trình (EXPERIENCE.md, State Patterns, Mở lại đúng liên kết và Máy khác; Key Flows, UJ-2). *Fix:* thêm một hàng đang tải và một hàng lỗi tải cho lối mở liên kết, với lộ trình trên máy giữ nguyên nếu máy này còn bản đó.
- **low** Giảm chuyển động được gắn với bản đồ phẳng và với toast hiện ngay. Ngăn Vì sao? vẫn được mô tả là trượt từ mép phải, chưa có quy tắc khi giảm chuyển động bật (DESIGN.md, Elevation & Depth; EXPERIENCE.md, State Patterns, Giảm chuyển động; Accessibility Floor). *Fix:* thêm một câu: ngăn hiện ngay tại chỗ, không trượt.

## 5. Visual reference coverage — thin

Thư mục UX không có `mockups/` và không có `wireframes/`. `imports/` chỉ có `.gitkeep`, không phải một ảnh hay một file giao diện. Hai bản không gắn link minh họa trong từng mục. Câu hợp đồng thắng đã có một lần, ở đầu EXPERIENCE.md: khi một bản phác sau này lệch với hai hợp đồng, hai hợp đồng thắng. `visual_priority` trỏ tới file prototype nằm ngoài ba thư mục trên. Đường nhanh đã hoãn màn hình chính. Đây là chỗ trống cần ghi nhận, không phải việc dựng thêm màn trong lần đọc này.

### Findings

- **medium** Chưa có file nhìn để gắn, và thân hai bản cũng chưa có câu «file này minh họa màn nào». Các chỗ viết «đúng prototype» không chỉ một khung cụ thể (EXPERIENCE.md, đoạn mở; DESIGN.md, `visual_priority`). *Fix:* khi màn chính được làm, đặt từng file vào `mockups/` hoặc `imports/`, gắn link ngay mục tương ứng, và ghi file đó minh họa việc gì. Giữ nguyên câu hợp đồng thắng đang có.

## 6. Bloat & overspecification — adequate

Phần lớn hợp đồng nằm trong bảng và trong các mục thành phần ngắn. Mục Ngưỡng, nguồn, và hồ sơ giữ các quyết định người dùng nhìn thấy: câu chân trang, phân biệt ngưỡng 30 tin với mốc 30 người, và việc cách gộp lương thuộc kiến trúc. Mục Giả định đường nhanh là mục lục các câu Duy chưa chốt. Cả hai đều là chỗ người đọc phía sau cần mở. Danh sách số cấm ở Voice and Tone là hợp đồng câu chữ, vì các số đó không được lên màn.

### Findings

- **medium** Mục Typography giao Be Vietnam Pro các độ đậm 400, 500 và 600, và giao Space Grotesk cho chữ trong avatar. Token chữ không có độ đậm 500. Viên hồ sơ phiên đã cấm avatar chữ «M». Người làm mặt chữ không biết độ đậm 500 thuộc vai nào (DESIGN.md, Typography; Components, Viên hồ sơ phiên). *Fix:* gắn độ đậm 500 với đúng vai chữ, hoặc bỏ câu đó; bỏ «chữ trong avatar» khỏi vai Space Grotesk.
- **medium** Định nghĩa tin đủ điều kiện, độ phủ, thứ tự nới toàn quốc rồi nhóm vai gần, và bốn nhóm vai gần nằm trong một đoạn văn sau bảng thành phần. Đây là hợp đồng của Học gì tiếp?, và một bảng sẽ cho người viết story lấy từng quy tắc ra được (EXPERIENCE.md, đoạn ngay sau Component Patterns). *Fix:* chuyển đoạn đó thành bảng: việc, quy tắc, câu trên màn.
- **low** Shapes còn «avatar, chấm bản đồ và lõi cột là hình tròn» và «thanh tiến độ nhỏ bo 4px đến 6px», trong khi không có thành phần avatar và không có thành phần thanh tiến độ (DESIGN.md, Shapes). *Fix:* giữ chấm bản đồ và lõi cột; bỏ avatar và thanh tiến độ.

## 7. Inheritance discipline — adequate

Sáu đường trong `sources` của cả hai bản đều có file: PRD, phụ lục PRD, brief, phụ lục brief, nghiên cứu thị trường, và prototype HTML. `visual_priority` trỏ cùng file prototype. Bốn tiêu đề UJ-1, UJ-2, UJ-3, UJ-4 trùng từng chữ với mục 3.4 của PRD. Hồ sơ phiên, kỹ năng đã có, kỹ năng giả định, ô mẫu, ngưỡng 30 tin, lương công khai, nhận định, Vì sao?, tin treo và lần làm mới giữ cùng nghĩa với mục 4 của PRD ở cả hai bản. Năm token mà EXPERIENCE.md gọi (`{colors.accent-cold}`, `{colors.accent-hot}`, `{colors.ink}`, `{colors.ink-lead}`, `{colors.surface}`) đều có trong DESIGN.md. Không có đường token gãy.

### Findings

- **high** Layout & Spacing của DESIGN.md chia Học gì tiếp? thành «kịch bản bên trái, số và bảng thành phố bên phải». EXPERIENCE.md chỉ có một cặp số trước và sau cho cả kịch bản, và Responsive chỉ nói kịch bản nằm trước các số. PRD, FR-5, cũng là một cặp số. Câu «PRD thắng khi lệch prototype» không nói bản nào thắng khi DESIGN.md và EXPERIENCE.md lệch nhau (DESIGN.md, Layout & Spacing; EXPERIENCE.md, đoạn mở và Responsive & Platform). *Fix:* bỏ «bảng thành phố» khỏi bố cục Học gì tiếp?, và thêm một câu: khi hai hợp đồng lệch nhau, EXPERIENCE.md thắng về hành vi và DESIGN.md thắng về mặt nhìn sau khi hành vi đã khớp.
- **medium** «Độ tin cậy» xuất hiện trong hàng Ngăn Vì sao? của DESIGN.md, với điều kiện «nếu nguồn đã có». EXPERIENCE.md không nói mức nào, lúc nào hiện, và câu đọc màn hình là gì. Mục 4 của PRD không có thuật ngữ này (DESIGN.md, Components, Ngăn Vì sao?; EXPERIENCE.md, Component Patterns, Ngăn Vì sao?). *Fix:* bỏ độ tin cậy, hoặc định nghĩa các mức và câu chữ trong cả hai hàng Ngăn Vì sao?.

## 8. Shape fit — strong

DESIGN.md đi đúng thứ tự khóa: Brand & Style, Colors, Typography, Layout & Spacing, Elevation & Depth, Shapes, Components, Do's and Don'ts. EXPERIENCE.md có đủ Foundation, Information Architecture, Voice and Tone, Component Patterns, State Patterns, Interaction Primitives, Accessibility Floor, và Key Flows. Inspiration & Anti-patterns có mặt vì prototype, ITviec, TopCV, TopDev và Thư Viện Pháp Luật được gọi tên trong nguồn. Responsive & Platform có mặt vì sản phẩm là web responsive, mốc 720px. Hai mục thêm đều đáng giữ: Ngưỡng, nguồn, và hồ sơ khóa những gì người dùng thấy về dữ liệu; Giả định đường nhanh còn để Duy sửa là mục lục các câu chưa chốt.

### Findings

Không có mục nào thừa hoặc sai thứ tự.

## Mechanical notes

Frontmatter hai bản cùng có `name`, `description`, `status: draft`, `created`, `updated`, `sources`, và `visual_priority`. Không có sơ đồ Mermaid. Không có đường token gãy.

Tên 27 thành phần trong hai bảng khớp nhau. Thứ tự khác nhau: DESIGN.md đặt Nút Vì sao? ngay sau Nút phụ, EXPERIENCE.md đặt nhóm đó sau Thẻ chặng. Token máy `button-primary`, `button-ghost`, `why-drawer`, và `salary-hidden` được thân bài trỏ bằng «Xem {components…}». Token `card` và `chip-selected` không được một hàng thành phần gọi tên; `chip-selected` là mặt của Chip vai trò đang bật, còn Chip kỹ năng đang bật lại dùng nền `{colors.accent-hot}`. `{typography.footer}` có trong frontmatter và không được thân bài gọi bằng đường dẫn; mục Colors gán chân trang cho `{colors.ink-meta}`.

Vài tên ngắn hơn tên hàng: «Khối tám quý» và «khối tám quý» thay cho «Khối xu hướng tám quý»; «hàng xếp hạng» và «bảng xếp hạng» là cùng một khối chưa có hàng. «Kịch bản» trong trạng thái «Đã xóa kịch bản» và trong bố cục Học gì tiếp? là chữ của mục 4 PRD cho việc thử cấp Fresher hoặc Junior, không phải tên màn «Mô phỏng Nếu–thì». Nút báo nguồn được mô tả hai lần liền nhau trong DESIGN.md, ở hàng Ngăn Vì sao? và ở hàng Nút báo nguồn. Chân trang không có hàng thành phần; câu chữ của nó nằm ở mục Ngưỡng, nguồn, và hồ sơ.
