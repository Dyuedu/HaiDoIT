---
name: Hải Đồ IT
description: Mặt nhìn web hướng nghiệp IT, lấy từ prototype ngày 2026-10-22, cho bốn chỗ của kỳ này và So sánh offer ở v1.1.
status: final
created: 2026-10-22
updated: 2026-10-27
sources:
  - _bmad-output/planning-artifacts/prds/prd-HaiDoIT-2026-10-22/prd.md
  - _bmad-output/planning-artifacts/prds/prd-HaiDoIT-2026-10-22/addendum.md
  - _bmad-output/planning-artifacts/briefs/brief-HaiDoIT-2026-10-22/brief.md
  - _bmad-output/planning-artifacts/briefs/brief-HaiDoIT-2026-10-22/addendum.md
  - _bmad-output/planning-artifacts/research/market-hai-do-it-nen-tang-nghe-nghiep-it-viet-n-2026-10-22/research.md
  - prototype/Hải Đồ IT — Bản đồ tuyển dụng & Cố vấn đa agent.html
visual_priority: prototype/Hải Đồ IT — Bản đồ tuyển dụng & Cố vấn đa agent.html
colors:
  surface: '#070B10'
  surface-card: '#0D141C'
  surface-sunken: '#0A1118'
  surface-selected: '#13202B'
  surface-hover: '#111C26'
  ink: '#E6EDF3'
  ink-lead: '#A9B8C7'
  ink-card: '#C4D0DC'
  ink-meta: '#9FB0C2'
  ink-dim: '#6E8091'
  ink-on-accent: '#0A0F05'
  accent-hot: '#C5F36A'
  accent-hot-hover: '#E4FFB5'
  accent-cold: '#62D9EE'
  offer-b: '#B9A6FF'
  warning: '#F5A65B'
  warning-ink: '#FFD3A6'
  warning-surface: '#140F09'
  warning-border: '#5A3E22'
  danger: '#F0605D'
  danger-ink: '#FFC2C2'
  danger-surface: '#160C0C'
  danger-border: '#5A2E2E'
  line: '#1C2A36'
  line-strong: '#243543'
  line-emphasis: '#2E4456'
  toast-surface: '#E6EDF3'
  toast-ink: '#0A0F05'
typography:
  display-map:
    fontFamily: Space Grotesk
    fontSize: clamp(34px, 5vw, 60px)
    fontWeight: '700'
    lineHeight: '1.04'
    letterSpacing: -0.02em
  display:
    fontFamily: Space Grotesk
    fontSize: clamp(26px, 3vw, 34px)
    fontWeight: '700'
    lineHeight: '1.15'
  city:
    fontFamily: Space Grotesk
    fontSize: 38px
    fontWeight: '700'
    lineHeight: '1.1'
  kpi:
    fontFamily: Space Grotesk
    fontSize: 26px
    fontWeight: '700'
    lineHeight: '1.1'
  logo:
    fontFamily: Space Grotesk
    fontSize: 20px
    fontWeight: '700'
    lineHeight: '1'
    letterSpacing: 0.04em
  lead-map:
    fontFamily: Be Vietnam Pro
    fontSize: 17px
    fontWeight: '400'
    lineHeight: '1.6'
  body:
    fontFamily: Be Vietnam Pro
    fontSize: 15px
    fontWeight: '400'
    lineHeight: '1.55'
  nav:
    fontFamily: Be Vietnam Pro
    fontSize: 14px
    fontWeight: '600'
    lineHeight: '1.3'
  button:
    fontFamily: Be Vietnam Pro
    fontSize: 14px
    fontWeight: '600'
    lineHeight: '1.2'
  kicker:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1.4'
    letterSpacing: 0.08em
  footer:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '400'
    lineHeight: '1.4'
rounded:
  sm: 8px
  md: 10px
  lg: 12px
  xl: 16px
  full: 9999px
spacing:
  '1': 4px
  '2': 8px
  '3': 12px
  '4': 16px
  '5': 24px
  '6': 28px
  '7': 32px
  '8': 40px
  '9': 48px
  '10': 72px
  gutter: 24px
  content-max: 1320px
components:
  button-primary:
    background: '{colors.accent-hot}'
    foreground: '{colors.ink-on-accent}'
    radius: '{rounded.md}'
    minHeight: 48px
    font: '{typography.button}'
  button-ghost:
    background: transparent
    foreground: '{colors.ink}'
    border: '{colors.line-strong}'
    radius: '{rounded.md}'
    minHeight: 44px
  card:
    background: '{colors.surface-card}'
    foreground: '{colors.ink}'
    border: '{colors.line}'
    radius: '{rounded.xl}'
  chip-selected:
    background: '{colors.ink}'
    foreground: '{colors.ink-on-accent}'
    radius: '{rounded.full}'
  salary-hidden:
    background: '{colors.warning-surface}'
    foreground: '{colors.warning-ink}'
    border: '{colors.warning}'
    radius: '{rounded.lg}'
  why-drawer:
    background: '{colors.surface-sunken}'
    foreground: '{colors.ink}'
    maxWidth: 560px
---

## Brand & Style

Hải Đồ IT là la bàn kỹ năng cho junior, fresher và người đang chuyển hướng trong ngành IT. Người mở web cần thấy việc đang tuyển ở thành phố của mình, thử một kỹ năng trước khi học, rồi nhận một lộ trình khoảng 90 ngày mà câu nào cũng trỏ được về nguồn.

Mặt nhìn lấy nguyên file prototype ngày 2026-10-22, `prototype/Hải Đồ IT — Bản đồ tuyển dụng & Cố vấn đa agent.html`. Năm file `.working/key-*.html` đã bị Duy từ chối và không được dùng làm chuẩn. Nền là đêm. Một màu chanh giữ việc chính, mức lương được phép hiện, và dấu kỹ năng đã có. Một màu lạnh giữ bản đồ, mục đang mở, và phần bảo hiểm trên thanh offer. Chữ Việt dùng Be Vietnam Pro cho câu, JetBrains Mono cho nhãn và số, Space Grotesk cho tiêu đề và logo.

[GIẢ ĐỊNH: kỳ này chỉ dùng mặt tối đó. Không có mặt sáng.]

Sản phẩm đứng về phía người đang học và đang cầm offer. Câu trên màn là số, ngày, và nguồn. Logo giữ chữ «HẢI ĐỒ·IT» của prototype, kèm dấu chấm màu {colors.accent-hot}.

## Colors

Bảng màu là các mã quan sát được trong iframe sản phẩm của prototype. Khung giấy bên ngoài file prototype, nền `#f5f4ef`, không thuộc sản phẩm.

- **Nền đêm (`{colors.surface}`)** là canvas. Lưới 40px phủ lên bằng màu {colors.accent-cold} ở độ đục rất thấp, đúng lớp lưới của prototype.
- **Thẻ (`{colors.surface-card}`)** là panel, thẻ thành phố, thẻ chặng và lớp chào. Viền là {colors.line}.
- **Lớp lõm (`{colors.surface-sunken}`)** là ô nhập, nền bản đồ phụ, và ngăn Vì sao?.
- **Chữ (`{colors.ink}`)** là câu người dùng phải đọc. **Dẫn (`{colors.ink-lead}`)** là đoạn mở đầu. **Meta (`{colors.ink-meta}`)** là chân trang và nhãn phụ. **Mờ (`{colors.ink-dim}`)** chỉ để đánh số thứ tự trang trí.
- **Chanh (`{colors.accent-hot}`)** là nút chính, một lương công khai khi ô mẫu đủ 30 tin, phần thực nhận trên thanh ba màu, dấu «đã có», và viền focus. Hover của link chanh là {colors.accent-hot-hover}. Chữ trên nền chanh là {colors.ink-on-accent}.
- **Lạnh (`{colors.accent-cold}`)** là gạch chân mục đang mở, cột thành phố, khung dự báo nét đứt, và phần bảo hiểm trên thanh offer.
- **Offer thứ hai (`{colors.offer-b}`)** chỉ để phân biệt offer B với offer A. Offer A dùng {colors.accent-cold} ở viền trên.
- **Hổ phách (`{colors.warning}`)** là lương đang ẩn, kỹ năng đang giảm, thuế trên thanh offer, và câu cần thận trọng. Nền cảnh báo là {colors.warning-surface}, chữ là {colors.warning-ink}, viền là {colors.warning-border}.
- **Đỏ (`{colors.danger}`)** có trong prototype cho rủi ro cao và điều khoản bị gọi là trái luật. Kỳ này không có huy hiệu «rủi ro cao» và không có màn đọc hợp đồng, nên không thành phần nào của năm chỗ đeo màu này như một điểm tin cậy.
- **Toast** đảo màu: nền {colors.toast-surface}, chữ {colors.toast-ink}.

Hàng đang chọn dùng nền {colors.surface-selected}. Hover hàng dùng {colors.surface-hover}.

Mục tiêu tương phản là WCAG 2.2 AA. Các cặp chữ chịu lực là: {colors.ink} và {colors.ink-lead} trên {colors.surface}, {colors.ink} trên {colors.surface-card}, {colors.ink-on-accent} trên {colors.accent-hot}, {colors.ink-on-accent} trên {colors.ink}, {colors.warning-ink} trên {colors.warning-surface}, {colors.accent-hot} khi nó là số lương hoặc dấu «đã có» trên {colors.surface}, và {colors.toast-ink} trên {colors.toast-surface}. Viền của ô nhập và gạch của mục đang chọn dùng {colors.accent-cold}, mục tiêu 3:1 với nền tối. Viền focus dày 2px màu {colors.accent-hot} và cách mép control 2px, để vòng luôn nằm trên nền tối.

## Typography

Ba họ chữ nhúng như prototype. Thân và điều hướng là Be Vietnam Pro, độ đậm 400, 500 và 600. Nhãn kicker, số và chân trang là JetBrains Mono, độ đậm 400 và 600. Tiêu đề và logo là Space Grotesk, độ đậm 500 và 700.

Bản đồ dùng {typography.display-map}. Các màn còn lại dùng {typography.display}. Tên thành phố trong panel phải dùng {typography.city}. Ba số đầu bản đồ dùng {typography.kpi}. Đoạn dẫn bản đồ dùng {typography.lead-map}. Câu thường dùng {typography.body}. Mục điều hướng dùng {typography.nav}. Kicker viết hoa dùng {typography.kicker}.

[GIẢ ĐỊNH: chữ mà người dùng phải đọc để hiểu một số, một cảnh báo, hoặc một việc cần bấm thì dùng {colors.ink} hoặc {colors.ink-lead}. {colors.ink-dim} không mang một mình một sự kiện bắt buộc.]

## Layout & Spacing

Khung nội dung rộng tối đa {spacing.content-max}, padding ngang {spacing.gutter}. Bản đồ cách đỉnh {spacing.8}. Các màn khác cách đỉnh {spacing.9}. Đáy trang chừa {spacing.10}. Khối trên bản đồ cách nhau {spacing.6}. Khối trên các màn khác cách nhau {spacing.7}.

Header dính trên cùng, nền {colors.surface} ở độ đục cao, gạch dưới bằng {colors.line}. Hàng điều hướng là bốn mục phẳng: Bản đồ nhu cầu, Học gì tiếp?, Lộ trình 90 ngày, Soi tin. So sánh offer thành mục thứ năm ở v1.1, đứng trước Soi tin. Logo về Bản đồ nhu cầu.

[GIẢ ĐỊNH: không dựng bốn nhóm «01 Thị trường» đến «04 Quyết định» của prototype, vì các nhóm đó tồn tại để chứa artboard ngoài kỳ này.]

[GIẢ ĐỊNH: dưới 720px, mọi khối đang chia hai cột xếp thành một cột. Thứ tự đọc là tiêu đề, việc chính, rồi panel phụ.]

Bản đồ trên bề rộng máy bàn chia hai: cột thành phố bên trái, thẻ thành phố bên phải. Học gì tiếp? trên máy bàn chia hai: kịch bản bên trái, ba số trước và sau bên phải. Lộ trình 90 ngày trên máy bàn chia hai: hồ sơ phiên bên trái, ba chặng bên phải. So sánh offer xếp hai panel cạnh nhau khi còn chỗ, rồi xếp dọc. Soi tin xếp ô dán link trên cùng, kết quả bên dưới.

## Elevation & Depth

Độ sâu chủ yếu là tầng màu, đúng prototype. Thẻ không có bóng thường. Header dính tách khỏi trang bằng đường {colors.line}. Hàng và nhóm đang chọn có viền trong 1px màu {colors.line-emphasis}.

Nút chính khi hover nhấc 2px và có bóng `0 10px 30px` từ {colors.accent-hot} ở độ đục thấp. Toast nằm giữa đáy, cách đáy {spacing.5}, bóng `0 12px 40px rgba(0,0,0,.5)`.

Ngăn Vì sao? đè lên một lớp mờ `rgba(3,6,9,.7)` và trượt từ mép phải. Rộng tối đa 560px.

Bản đồ nhu cầu dùng đúng khối bản đồ 3D của prototype. Bản đồ Việt Nam nằm dưới các cột. Cột đứng tại thành phố. Cột đang chọn có mặt {colors.ink}. Cột không chọn có mặt {colors.accent-cold}. Khi tầm nhìn là mốc dự báo, cột có khung nét đứt {colors.accent-hot}. Sau khi mở, bản đồ nghiêng vào thế 3D. Kéo ngang để xoay. Kéo dọc để nghiêng. Trên bản đồ có nút 3D, 2D, xoay trái, xoay phải và đặt lại. Dòng dưới bản đồ ghi «Kéo để xoay · kéo dọc để nghiêng» và «Cột = tin hiện tại».

Khi `prefers-reduced-motion` bật, prototype tắt animation và transition. Kỳ này giữ quy tắc đó. Nút 3D vẫn còn.

## Shapes

Viên thuốc, chip và hồ sơ dùng {rounded.full}. Thẻ và panel dùng {rounded.xl}. Lớp chào và toast dùng {rounded.lg}. Nút, ô nhập và hàng bảng dùng {rounded.md}. Logo dùng {rounded.sm}. Chấm bản đồ và lõi cột là hình tròn. Thanh tiến độ nhỏ bo 4px đến 6px.

Ô lương đang ẩn là hộp nét đứt màu {colors.warning}, đúng kiểu prototype khi số tin công khai lương dưới 30. Kỳ này không vẽ trục P25–P75.

## Components

- **Logo.** Hình vuông 34px, bo {rounded.sm}, viền {colors.accent-hot} dày 1.5px. Bên trong có ba chấm của prototype: hai chấm {colors.accent-cold}, một chấm {colors.accent-hot}. Chữ cạnh logo là {typography.logo}, nội dung «HẢI ĐỒ·IT».
- **Thanh điều hướng.** Bốn mục (năm từ v1.1), mỗi mục cao ít nhất 44px, chữ {typography.nav}. Mục đang mở có gạch chân 2px màu {colors.accent-cold}. Nền header dính như mục Layout. Dưới 720px các mục xuống dòng, vẫn cao ít nhất 44px.
- **Viên hồ sơ phiên.** Viên thuốc cao khoảng 44px. [GIẢ ĐỊNH: chỉ hiện khi hồ sơ phiên đã có thành phố, cấp bậc và vai trò. Chữ là ba mục đó, không có tên người, không có avatar chữ «M». Bấm thì tới chỗ sửa hồ sơ trên Học gì tiếp?.]
- **Lớp chào.** Thẻ {colors.surface-card}, viền {colors.line-emphasis}, bo {rounded.xl}. [GIẢ ĐỊNH: chỉ trên Bản đồ nhu cầu, mở một lần trên mỗi máy, không gọi tên người. Ba dòng nói xem một thành phố, thử một kỹ năng ở Học gì tiếp?, rồi tạo lộ trình. Nút «Đã hiểu» là nút chính và đóng lớp.]
- **Chip vai trò.** Viên thuốc, cao tối thiểu 44px, chữ 14px đậm 600. Đang bật thì nền {colors.ink} và chữ {colors.ink-on-accent}. Vai trò của kỳ này là Tất cả, Backend, Frontend, Data/AI, DevOps/Cloud, Mobile, Bảo mật.
- **Tầm nhìn.** Hộp {colors.surface-sunken}, bo {rounded.md}. [GIẢ ĐỊNH: bốn nhãn giữ kiểu prototype, «NAY», «+6T», «+12T», «+18T».] Mỗi mốc cao ít nhất 44px. Mốc đang chọn có gạch chân 2px màu {colors.accent-cold}.
- **Bản đồ 3D.** Đúng khối trong artboard «Thị trường · Bản đồ nhu cầu». Không thay bằng biểu đồ cột phẳng. Ba cột: Hà Nội, TP. Hồ Chí Minh, Đà Nẵng. Nhãn nổi ghi tên thành phố và số tin. Ở mốc dự báo, khi chưa có công thức đã đo, cột giữ chiều cao của «NAY» với khung nét đứt và nhãn «Chưa ghi nhận dự báo»; khi đã có công thức, nhãn gồm tên thành phố, chữ «Dự báo», và khoảng.
- **Nút thế bản đồ.** Đúng cụm của prototype: 3D, 2D, xoay trái, xoay phải, đặt lại. Mỗi nút cao ít nhất 44px. 3D bật thế nghiêng và cho kéo. 2D đặt bản đồ phẳng. Xoay trái và xoay phải đổi góc. Đặt lại đưa về thế vừa mở.
- **Thẻ thành phố.** Nền {colors.surface-card}. Tên dùng {typography.city}. Ba tab «Cơ cấu», «Lương», «Dự báo». Tab lương đủ mẫu thì hiện một số màu {colors.accent-hot}. Tab lương thiếu mẫu thì hiện {components.salary-hidden}; đây là trạng thái thường gặp nhất lúc ra mắt nên phải trông chủ ý, không giống lỗi. Khi số lương có dùng tin USD, dưới số có một dòng {typography.body} màu chữ meta ghi tỷ giá và ngày áp dụng. Tab dự báo hiện «Chưa ghi nhận dự báo cho mốc này.» cho đến khi có công thức đã đo, rồi một khoảng có nhãn «Dự báo»; kèm tín hiệu hoặc câu chưa ghi nhận tín hiệu.
- **Ô lương đầu trang.** Cùng một số với tab lương của thành phố đang chọn, cùng màu {colors.accent-hot}, cỡ {typography.kpi}. Khi chưa chọn thành phố, hoặc khi ô mẫu dưới 30 tin, ô này để trống và hiện câu chưa đủ mẫu nếu đã chọn thành phố mà vẫn thiếu mẫu.
- **Danh kỹ năng thành phố.** Nằm trong tab Cơ cấu của thẻ thành phố. Mỗi dòng là một kỹ năng đang được nhắc trong tin của thành phố đó. Kỹ năng thuộc hồ sơ phiên có dấu «đã có».
- **Dấu đã có.** Dấu tick màu {colors.accent-hot} và chữ «đã có» trên danh kỹ năng thành phố. Kỹ năng ngoài hồ sơ không có dấu.
- **Bảng xếp hạng.** Nằm dưới bản đồ, cạnh khối xu hướng. Cột là hạng, tên thành phố, và số tin đang mở. Không có cột mức tăng theo năm và không có cột lương. Hàng đang chọn có gạch chân 2px màu {colors.accent-cold}.
- **Khối xu hướng tám quý.** [GIẢ ĐỊNH: nằm trên Bản đồ nhu cầu, dưới bảng xếp hạng, đúng vùng prototype gọi là «Xu hướng kỹ năng».] Cột tăng màu {colors.accent-hot}, cột giảm màu {colors.warning}, cột đi ngang màu {colors.accent-cold}. Cạnh biểu đồ có chú giải chữ «tăng», «giảm» và «đi ngang». Cột cuối đậm hơn cột đầu. Không có dải ticker chạy ngang.
- **Nút chính.** Xem {components.button-primary}. Cao 48px. [GIẢ ĐỊNH: chữ trên Bản đồ nhu cầu là «Thử một kỹ năng cho thành phố này», vì nút prototype «Nhận lộ trình cho thị trường này» nhảy thẳng sang màn cố vấn, còn luồng đã chốt đi qua Học gì tiếp? trước.] Chữ trên Học gì tiếp? và trên Lộ trình 90 ngày là «Tạo lộ trình 90 ngày». Chữ trên Soi tin là «Soi tin».
- **Nút phụ.** Xem {components.button-ghost}. Cao 44px. Dùng cho «Thử lại», «Bỏ lọc», và «Đặt lại» hồ sơ phiên.
- **Nút Vì sao?.** Viên thuốc cao ít nhất 44px, chữ {typography.kicker} màu {colors.accent-cold}. Mỗi nhận định có một nút.
- **Ngăn Vì sao?.** Xem {components.why-drawer}. Có câu nguồn và nút đóng cao ít nhất 44px. Rộng bằng phần nhỏ hơn giữa bề rộng viewport và 560px. Không có nút báo nguồn.
- **Chip kỹ năng.** Viên thuốc. Kỹ năng đã có có dấu tick. Kỹ năng giả định đang bật dùng nền {colors.accent-hot} và chữ {colors.ink-on-accent}. Kỹ năng đang giảm có tem chữ {colors.warning-ink}.
- **Danh nên học tiếp.** Danh sách này nằm trên Học gì tiếp?, và dùng chữ {typography.body}. Mỗi dòng là một hàng bo {rounded.md}, có tên kỹ năng, số tin tăng, số tuần, số tin trên mỗi tuần, và nút «Thêm» cùng kiểu {components.button-ghost}. Kỹ năng đang giảm có tem chữ {colors.warning-ink}.
- **Thẻ chặng.** Ba thẻ, nhãn «Ngày 1–30», «Ngày 31–60», «Ngày 61–90». Mỗi thẻ có các kỹ năng của chặng, tên một dự án thực hành, và một câu nói người học làm ra cái gì. Nền {colors.surface-card}, bo {rounded.xl}.
- **Ô email.** Ô nhập bo {rounded.md}, viền 2px màu {colors.accent-cold}, nền {colors.surface-sunken}. [GIẢ ĐỊNH: nhãn «Email để mở lại lộ trình này».] Ô đứng dưới ba chặng, sau khi lộ trình đã hiện. Ô offer và ô link của Soi tin dùng cùng viền này.
- **Ô nhận lại liên kết.** Ô nhập cùng kiểu với Ô email: bo {rounded.md}, viền 2px màu {colors.accent-cold}, nền {colors.surface-sunken}, và chữ {typography.body}. Câu «Chưa có lộ trình cho email này.» dùng chữ {colors.ink}.
- **Panel offer.** Hai thẻ. Offer A viền trên {colors.accent-cold}. Offer B viền trên {colors.offer-b}. Bên trong là các ô của PRD: tên công ty, lương tháng, gross hoặc net, người phụ thuộc, tháng thưởng, phụ cấp, ngày remote mỗi tuần, căn cứ đóng bảo hiểm, và mức đóng khi chọn mức thấp hơn.
- **Thanh thực nhận.** Ba khúc cộng đủ chiều ngang của thanh: thực nhận màu {colors.accent-hot}, bảo hiểm màu {colors.accent-cold}, thuế màu {colors.warning}.
- **Hộp hụt bảo hiểm.** Hộp này dùng nền {colors.warning-surface}, chữ {colors.warning-ink}, nét đứt màu {colors.warning}, và bo {rounded.lg}. Hộp lương ẩn dùng cùng nét đứt. Hộp không dùng {colors.danger}.
- **Kết quả soi tin.** Thẻ liệt kê số lần làm mới, ngày thấy đầu, ngày thấy gần nhất. Tin trùng và lương bất thường dùng hộp {colors.warning-surface} khi có kết luận. Không có vòng điểm trên 100.
- **Toast.** Nền {colors.toast-surface}, chữ {colors.toast-ink}, bo {rounded.lg}. Có nút đóng cao ít nhất 44px. Câu ngắn, một việc vừa xảy ra. Hẹn giờ 2,4 giây không phải cách duy nhất để câu biến mất.
- **Khối trạng thái.** Đang tải là các thanh xương trên nền {colors.surface-card}. Lỗi và rỗng là một câu {typography.body}. Nút phụ đứng cạnh câu khi trạng thái đó có lối thử lại hoặc bỏ lọc.

## Do's and Don'ts

Làm:

- Giữ nền {colors.surface}, chữ {colors.ink}, nút chính {colors.accent-hot}, và nhấn bản đồ {colors.accent-cold}.
- Hiện một lương công khai bằng một số, chỉ khi ô mẫu đủ 30 tin.
- Vẽ dự báo thành một khoảng có chữ «Dự báo».
- Đặt Vì sao? trên từng nhận định của lộ trình, kể cả nhận định bị loại.
- Để ô email dưới lộ trình đã hiện.
- Giữ nút và chip cao ít nhất 44px.
- Tắt chuyển động khi người dùng bật giảm chuyển động.

Không làm:

- Không đưa thành màn các artboard Lộ trình thật, Hộ chiếu kỹ năng, Chỉ số phản hồi nhà tuyển dụng, Nhảy việc, và Remote & Nhật.
- Câu do agent viết được ghi tên một trong bốn agent: Bản đồ, Học gì tiếp, Lộ trình, Soi tin. Màn không hiện kế hoạch và không hiện lời gọi tool. Không đưa vào màn v1 nút «Chạy đa agent», phòng tập thương lượng, trục phân vị, vòng điểm trên 100, và chỉ số AI. Không có agent đọc hợp đồng, agent ghép việc, agent chấm nhà tuyển dụng, hay agent đọc CV. Khối kết quả lộ trình và ngăn Vì sao? của artboard cố vấn vẫn được dùng cho Lộ trình 90 ngày.
- Không điền sẵn hồ sơ tên Minh, mục tiêu Data/AI, hay kỹ năng mẫu Python, SQL, Git.
- Không hiện số mẫu của prototype, gồm các mức 3.960 tin hay lương 26 triệu, như thể đó là dữ liệu đang chạy.
- Không khóa một bảng lương sau form xin số điện thoại.
- Không dùng {colors.danger} để chấm một tin là đáng tin hay rủi ro cao.
- Không thay bản đồ 3D của prototype bằng một biểu đồ cột khác.
- Không dùng `.working/key-*.html` làm chuẩn mặt nhìn.
- Không có nút «Báo nguồn sai hoặc đã cũ».
