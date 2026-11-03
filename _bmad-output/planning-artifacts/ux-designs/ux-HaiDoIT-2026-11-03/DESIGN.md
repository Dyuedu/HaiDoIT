---
name: Hải Đồ IT
description: Bảng điều khiển tối, mật độ cao, cho số liệu kỹ năng trên tin tuyển dụng IT. Không có hệ thống UI shadcn.
status: final
created: 2026-11-03
updated: 2026-11-04
sources:
  - '{planning_artifacts}/prds/prd-HaiDoIT-2026-11-02/prd.md'
  - '{planning_artifacts}/prds/prd-HaiDoIT-2026-11-02/addendum.md'
  - '{planning_artifacts}/architecture/architecture-HaiDoIT-2026-11-03/ARCHITECTURE-SPINE.md'
colors:
  canvas: '#070B10'
  header: '#0A1017'
  panel: '#0D141C'
  inset: '#0A1118'
  field: '#05080C'
  notice: '#141009'
  text: '#E6EDF3'
  text-muted: '#9FB0C2'
  text-secondary: '#C4D0DC'
  text-quiet: '#A9B8C7'
  text-dim: '#8496A6'
  text-placeholder: '#7D8FA1'
  text-doc: '#D5DEE7'
  border: '#1C2A36'
  border-strong: '#243543'
  border-chip: '#2E4456'
  border-row: '#15212B'
  border-dashed: '#3A5163'
  track: '#13202B'
  track-alt: '#16222D'
  primary: '#C5F36A'
  primary-hover: '#D6FA94'
  primary-ink: '#0A0F05'
  link-hover: '#E4FFB5'
  selected: '#62D9EE'
  amber: '#F5A65B'
  amber-deep: '#5A4426'
  amber-soft: '#FFD3A6'
  amber-softer: '#FFE6CC'
  amber-edge: '#5A3E22'
  disabled: '#2A3A44'
  slate: '#4A6478'
  column-face: '#1F6A7C'
  column-side: '#154B5B'
  map-land: '#0D2836'
  map-line: '#2E5A6A'
  meter-idle: '#3E6A80'
  band-deep: '#1F4A58'
  band-mid: '#3E8296'
  band-pale: '#A8EAF5'
  icon-scan: '#1A140C'
  mask: '#000'
typography:
  logo:
    fontFamily: Be Vietnam Pro
    fontSize: 16px
    fontWeight: '700'
    letterSpacing: 0.04em
  display:
    fontFamily: Be Vietnam Pro
    fontSize: 34px
    fontWeight: '700'
    lineHeight: '1.2'
  skill-name:
    fontFamily: Be Vietnam Pro
    fontSize: 32px
    fontWeight: '700'
  title:
    fontFamily: Be Vietnam Pro
    fontSize: 26px
    fontWeight: '700'
    lineHeight: '1.2'
  title-sm:
    fontFamily: Be Vietnam Pro
    fontSize: 22px
    fontWeight: '700'
  section:
    fontFamily: Be Vietnam Pro
    fontSize: 20px
    fontWeight: '700'
  heading-sm:
    fontFamily: Be Vietnam Pro
    fontSize: 18px
    fontWeight: '700'
  lead:
    fontFamily: Be Vietnam Pro
    fontSize: 17px
    fontWeight: '600'
  body:
    fontFamily: Be Vietnam Pro
    fontSize: 16px
    lineHeight: '1.7'
  body-md:
    fontFamily: Be Vietnam Pro
    fontSize: 15px
    lineHeight: '1.55'
  ui:
    fontFamily: Be Vietnam Pro
    fontSize: 14px
    fontWeight: '500'
  button:
    fontFamily: Be Vietnam Pro
    fontSize: 15px
    fontWeight: '600'
  button-compact:
    fontFamily: Be Vietnam Pro
    fontSize: 14px
    fontWeight: '600'
  chip:
    fontFamily: Be Vietnam Pro
    fontSize: 13px
    fontWeight: '500'
  caption:
    fontFamily: Be Vietnam Pro
    fontSize: 13px
    lineHeight: '1.5'
  footer:
    fontFamily: JetBrains Mono
    fontSize: 12px
  kicker:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '600'
    lineHeight: '1.4'
    letterSpacing: 0.08em
  micro:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '600'
    letterSpacing: 0.06em
  metric:
    fontFamily: Be Vietnam Pro
    fontSize: 28px
    fontWeight: '700'
  match:
    fontFamily: JetBrains Mono
    fontSize: 34px
    fontWeight: '600'
  mono-lg:
    fontFamily: JetBrains Mono
    fontSize: 22px
    fontWeight: '600'
  mono:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '600'
  mono-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
  field:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.7'
rounded:
  hair: 2px
  bar: 4px
  sm: 6px
  segment: 7px
  md: 8px
  lg: 10px
  xl: 12px
  drop: 14px
  full: 999px
spacing:
  target: 44px
  nav: 52px
  button: 48px
  page: 24px
  panel: 20px
  grid: 40px
  content: 1280px
  doc: 760px
  role-doc: 860px
components:
  app-header:
    background: '{colors.header}'
    border: '{colors.border}'
    foreground: '{colors.text}'
    logo: '{typography.logo.fontSize}'
    nav: '{spacing.nav}'
    accent: '{colors.primary}'
    selected: '{colors.selected}'
  profile-chip:
    foreground: '{colors.text-secondary}'
    border: '{colors.border-strong}'
    radius: '{rounded.full}'
    minHeight: '{spacing.target}'
    fontSize: '{typography.footer.fontSize}'
    emptyDot: '{colors.slate}'
    unsavedDot: '{colors.amber}'
    savedDot: '{colors.primary}'
  button-primary:
    background: '{colors.primary}'
    foreground: '{colors.primary-ink}'
    backgroundHover: '{colors.primary-hover}'
    radius: '{rounded.md}'
    minHeight: '{spacing.button}'
    minHeightCompact: '{spacing.target}'
    fontSize: '{typography.button.fontSize}'
    disabledBackground: '{colors.disabled}'
    disabledForeground: '{colors.text-dim}'
  button-ghost:
    background: transparent
    foreground: '{colors.text-secondary}'
    border: '{colors.border-chip}'
    borderHover: '{colors.selected}'
    radius: '{rounded.md}'
    minHeight: '{spacing.target}'
    fontSize: '{typography.ui.fontSize}'
  button-danger:
    background: transparent
    foreground: '{colors.amber-soft}'
    border: '{colors.amber-edge}'
    foregroundHover: '{colors.amber-softer}'
    borderHover: '{colors.amber}'
    radius: '{rounded.md}'
    minHeight: '{spacing.target}'
  chip:
    background: '{colors.inset}'
    foreground: '{colors.text-secondary}'
    border: '{colors.border-chip}'
    selectedBorder: '{colors.selected}'
    radius: '{rounded.full}'
    minHeight: '{spacing.target}'
    fontSize: '{typography.chip.fontSize}'
  segmented-control:
    background: '{colors.inset}'
    border: '{colors.border-strong}'
    radius: '{rounded.lg}'
    itemRadius: '{rounded.segment}'
    selected: '{colors.selected}'
    foreground: '{colors.text-quiet}'
  icon-button:
    size: '{spacing.target}'
    radius: '{rounded.lg}'
    background: '{colors.inset}'
    foreground: '{colors.text-secondary}'
    border: '{colors.border-strong}'
    borderHover: '{colors.selected}'
  panel:
    background: '{colors.panel}'
    border: '{colors.border}'
    radius: '{rounded.xl}'
    padding: '{spacing.panel}'
  kicker:
    fontFamily: '{typography.kicker.fontFamily}'
    fontSize: '{typography.kicker.fontSize}'
    letterSpacing: '{typography.kicker.letterSpacing}'
    foreground: '{colors.text-muted}'
  data-table:
    fontSize: '{typography.ui.fontSize}'
    header: '{typography.kicker.fontSize}'
    headerForeground: '{colors.text-muted}'
    rowBorder: '{colors.border-row}'
    numberFont: '{typography.mono.fontFamily}'
  site-footer:
    border: '{colors.border}'
    foreground: '{colors.text-muted}'
    fontSize: '{typography.footer.fontSize}'
    link: '{colors.primary}'
  map-column:
    top: '{colors.selected}'
    topSelected: '{colors.text}'
    face: '{colors.column-face}'
    side: '{colors.column-side}'
    labelBackground: '{colors.canvas}'
    labelBorder: '{colors.border-chip}'
    smallBorder: '{colors.amber-deep}'
    radius: '{rounded.md}'
  meter:
    track: '{colors.track}'
    trackAlt: '{colors.track-alt}'
    fill: '{colors.selected}'
    idle: '{colors.meter-idle}'
    radius: '{rounded.bar}'
  level-bar:
    radius: '{rounded.sm}'
    deep: '{colors.band-deep}'
    line: '{colors.map-line}'
    mid: '{colors.band-mid}'
    selected: '{colors.selected}'
    pale: '{colors.band-pale}'
  skill-node:
    background: '{colors.panel}'
    inset: '{colors.inset}'
    radius: '{rounded.lg}'
    selected: '{colors.selected}'
    idleBorder: '{colors.border}'
    percent: '{typography.mono-lg.fontSize}'
  select:
    background: '{colors.inset}'
    foreground: '{colors.text}'
    border: '{colors.border-chip}'
    radius: '{rounded.md}'
    minHeight: '{spacing.target}'
    caret: '{colors.selected}'
  checkbox:
    box: 24px
    border: '{colors.slate}'
    checked: '{colors.selected}'
    mark: '{colors.primary-ink}'
    radius: '{rounded.sm}'
  drop-zone:
    radius: '{rounded.drop}'
    line: '{colors.selected}'
    fill: '{colors.selected}'
  step-list:
    done: '{colors.text}'
    waiting: '{colors.text-dim}'
    track: '{colors.track-alt}'
    fill: '{colors.selected}'
    time: '{typography.mono-lg.fontSize}'
  gap-actions:
    background: '{colors.inset}'
    foreground: '{colors.text-secondary}'
    border: '{colors.border-chip}'
    selected: '{colors.selected}'
    radius: '{rounded.md}'
    minHeight: '{spacing.target}'
    miss: '{colors.text-muted}'
    coreBadge: '{colors.amber}'
  stat-block:
    background: '{colors.inset}'
    border: '{colors.border-chip}'
    radius: '{rounded.xl}'
    number: '{typography.mono.fontFamily}'
  toast:
    background: '{colors.text}'
    foreground: '{colors.primary-ink}'
    radius: '{rounded.lg}'
    fontSize: '{typography.button-compact.fontSize}'
  paste-field:
    background: '{colors.field}'
    foreground: '{colors.text}'
    placeholder: '{colors.text-placeholder}'
    border: '{colors.border-chip}'
    radius: '{rounded.lg}'
    fontSize: '{typography.field.fontSize}'
    lineHeight: '{typography.field.lineHeight}'
  match-ring:
    track: '{colors.track-alt}'
    fill: '{colors.selected}'
    number: '{typography.match.fontSize}'
  sign-card:
    background: '{colors.inset}'
    border: '{colors.border-chip}'
    radius: '{rounded.lg}'
    mark: '{colors.amber}'
    markBorder: '{colors.amber-deep}'
  insight-card:
    background: '{colors.panel}'
    radius: '{rounded.xl}'
    number: '{colors.selected}'
    lowBorder: '{colors.amber-deep}'
    lowText: '{colors.amber}'
  notice:
    background: '{colors.notice}'
    border: '{colors.amber-deep}'
    radius: '{rounded.xl}'
    kicker: '{colors.amber}'
  doc-section:
    maxWidth: '{spacing.doc}'
    heading: '{typography.section.fontSize}'
    body: '{typography.body.fontSize}'
    bodyColor: '{colors.text-doc}'
    rule: '{colors.border}'
---

## Brand & Style

Hải Đồ IT là bảng điều khiển tối, mật độ cao. Người dùng mở trên web để đọc tỷ lệ kỹ năng trong tin tuyển dụng, không phải để xem một trang giới thiệu. Nền `{colors.canvas}`, chữ `{colors.text}`, nút chính `{colors.primary}` với chữ `{colors.primary-ink}`, mục đang chọn `{colors.selected}`.

Chữ giao diện là Be Vietnam Pro. Số, cỡ mẫu n, ngày snapshot và phần trăm là JetBrains Mono. Vàng chanh chỉ dành cho việc chính và liên kết. Xanh lam là thứ đang được chọn hoặc con số đang được đọc. Hổ phách là cỡ mẫu nhỏ, nhóm so sánh đã quay về, chưa đủ dữ liệu, hoặc hồ sơ tạm. Hổ phách không có nghĩa tin giả.

Các màn ứng dụng có lưới nền mờ: hai `linear-gradient` của `{colors.selected}` ở độ phủ 0,04, ô `{spacing.grid}`. Trang chính sách và trang vai trò bỏ lớp lưới này; nền vẫn là `{colors.canvas}`.

Khi artboard lệch spine này, làm theo spine.

## Colors

Màu dưới đây đều có trong CSS hoặc thuộc tính `style` của 15 màn. Không thêm màu cho chế độ sáng.

- **Nền.** `{colors.canvas}` là nền trang. `{colors.header}` là thanh đầu. `{colors.panel}` là thẻ và khung. `{colors.inset}` là ô lồng bên trong (nút kỹ năng, ô chọn, hồ sơ tạm). `{colors.field}` chỉ là nền ô dán tin. `{colors.notice}` là nền khung cảnh báo (nhóm so sánh quay về, CV scan).
- **Chữ.** `{colors.text}` là chữ chính. `{colors.text-secondary}` là chữ phụ trên nút ma và mô tả. `{colors.text-quiet}` là đoạn dẫn. `{colors.text-muted}` là nhãn phụ, chân trang, số trên n. `{colors.text-dim}` là bước chưa chạy và chữ nút tắt. `{colors.text-placeholder}` là gợi ý trong ô dán. `{colors.text-doc}` là thân trang chính sách.
- **Viền.** `{colors.border}` ngăn header, panel, hàng chân trang. `{colors.border-strong}` viền hồ sơ và cụm chuyển. `{colors.border-chip}` viền nút ma, ô chọn, thẻ dấu hiệu. `{colors.border-row}` ngăn hàng bảng. `{colors.border-dashed}` là viền nét đứt của nút kỹ năng chưa chọn trên màn tự chọn.
- **Việc chính và đang chọn.** `{colors.primary}` là nút chính và liên kết (`a`). `{colors.primary-hover}` khi trỏ nút chính. `{colors.link-hover}` khi trỏ liên kết. `{colors.primary-ink}` là chữ trên nút chính và trên toast. `{colors.selected}` là gạch mục nav, viền đang chọn, cột bản đồ, vòng mức khớp.
- **Hổ phách.** `{colors.amber}` là nhãn cỡ mẫu nhỏ, kicker cảnh báo, huy hiệu khoảng trống cốt lõi, chữ “chưa đủ dữ liệu”, chấm hồ sơ tạm. `{colors.amber-deep}` là viền khung cảnh báo và viền nhãn cột mờ. `{colors.amber-soft}` / `{colors.amber-softer}` / `{colors.amber-edge}` chỉ xuất hiện trên nút xoá hồ sơ.
- **Tắt.** Nút chính tắt dùng nền `{colors.disabled}` và chữ `{colors.text-dim}`.
- **Bản đồ.** Mặt trên cột `{colors.selected}`; khi cột đang được chọn, mặt trên đổi thành `{colors.text}`. Mặt trước và sau `{colors.column-face}`, hai bên `{colors.column-side}`. Cột n < 30 vẽ cùng tỷ trọng nhưng opacity 0,4. Lãnh thổ trên hình `{colors.map-land}`, nét `{colors.map-line}`. Lưới đĩa bản đồ dùng `{colors.selected}` ở độ phủ 0,13, che bởi mặt nạ radial tới `{colors.mask}` (stylesheet ghi `#000`).
- **Thanh tỷ lệ.** Rãnh `{colors.track}` hoặc `{colors.track-alt}`. Phần đã có đủ mẫu tô `{colors.selected}`. Phần kỹ năng chưa có trên màn tự chọn tô `{colors.meter-idle}`. Cột mờ ở biểu đồ 2D để nền trong suốt và phủ lớp sọc `{colors.selected}`.
- **Cơ cấu cấp bậc.** `{colors.band-deep}`, `{colors.map-line}`, `{colors.band-mid}`, `{colors.selected}`, `{colors.band-pale}` là các đoạn trên thanh xếp. Cùng một hex không gắn với một cấp bậc trên mọi artboard: trên màn cố vấn, `{colors.map-line}` là đoạn Intern; trên trang vai trò, hex đó là đoạn Fresher. [NOTE FOR UX] Chưa có thang màu cấp bậc ổn định. Đừng gán tên cấp cho các hex này khi dựng lại.
- **Khác.** `{colors.slate}` là chấm “chưa có hồ sơ”, viền ô kiểm chưa chọn, và nút kỹ năng dưới ngưỡng trên artboard lộ trình chung. `{colors.icon-scan}` chỉ là nền biểu tượng file scan.

Độ tương phản đo từ các hex này, chữ thường trên nền:

| Cặp | Tỷ lệ |
|---|---|
| `{colors.text}` trên `{colors.canvas}` | 16,7:1 |
| `{colors.text-muted}` trên `{colors.canvas}` | 8,9:1 |
| `{colors.text-quiet}` trên `{colors.canvas}` | 9,7:1 |
| `{colors.primary-ink}` trên `{colors.primary}` | 15,1:1 |
| `{colors.selected}` trên `{colors.canvas}` | 11,9:1 |
| `{colors.amber}` trên `{colors.canvas}` | 9,9:1 |
| `{colors.text-dim}` trên `{colors.disabled}` | 3,9:1 |

[NOTE FOR UX] Cặp chữ nút tắt chưa đạt mức 4,5:1. Chưa có quyết định đổi hex.

## Typography

Be Vietnam Pro cho câu, nhãn, nút, tiêu đề. JetBrains Mono cho số, n, ngày, phần trăm, mã, tên file, chân trang.

| Vai | Mặt chữ | Cỡ | Nặng | Thấy ở |
|---|---|---|---|---|
| `{typography.display}` | Be Vietnam Pro | 34px | 700 | Tiêu đề trang chính sách, `line-height: 1.2` |
| `{typography.match}` | JetBrains Mono | 34px | 600 | Số mức khớp |
| `{typography.skill-name}` | Be Vietnam Pro | 32px | 700 | Tên kỹ năng trên màn chi tiết |
| `{typography.metric}` | Be Vietnam Pro | 28px | 700 | Số tin của một thành phố |
| `{typography.title}` | Be Vietnam Pro | 26px | 700 | Tiêu đề màn ứng dụng, `line-height: 1.2` trên Bản đồ |
| `{typography.mono-lg}` | JetBrains Mono | 22px | 600 | Phần trăm trên nút kỹ năng; đồng hồ đang đọc CV |
| `{typography.title-sm}` | Be Vietnam Pro | 22px | 700 | Tiêu đề bảng thành phố; tiêu đề lỗi CV scan |
| `{typography.section}` | Be Vietnam Pro | 20px | 700 | Tiêu đề mục chính sách và Insights |
| `{typography.heading-sm}` | Be Vietnam Pro | 18px | 700 | Mục trên kết quả Soi tin; số đếm kỹ năng trùng |
| `{typography.lead}` | Be Vietnam Pro | 17px | 600 | Câu mời đối chiếu CV; câu trên thẻ Insights |
| `{typography.logo}` | Be Vietnam Pro | 16px | 700 | Wordmark, giãn cách 0,04em |
| `{typography.body}` | Be Vietnam Pro | 16px | — | Thân trang chính sách, `line-height: 1.7` |
| `{typography.body-md}` | Be Vietnam Pro | 15px | — | Đoạn dẫn màn, `line-height: 1.55` |
| `{typography.button}` | Be Vietnam Pro | 15px | 600 | Nút chính trên hầu hết màn ứng dụng |
| `{typography.ui}` | Be Vietnam Pro | 14px | 500 | Mục nav, nút ma, bảng |
| `{typography.button-compact}` | Be Vietnam Pro | 14px | 600 | Nút chính trên Bản đồ và màn CV scan |
| `{typography.field}` | JetBrains Mono | 14px | 400 | Ô dán tin, `line-height: 1.7` |
| `{typography.chip}` | Be Vietnam Pro | 13px | 500 | Chip vai trò trên Bản đồ |
| `{typography.mono}` | JetBrains Mono | 13px | 600 | Phần trăm trong bảng, nhãn cột mờ |
| `{typography.caption}` | Be Vietnam Pro | 13px | — | Dòng trợ giúp |
| `{typography.footer}` | JetBrains Mono | 12px | — | Chân trang, meta snapshot, chip hồ sơ |
| `{typography.mono-sm}` | JetBrains Mono | 12px | 600 | Cụm chuyển 3D / 2D / bảng trên Bản đồ |
| `{typography.kicker}` | JetBrains Mono | 11px | 600 | Nhãn in hoa, `line-height: 1.4`, giãn cách 0,08em |
| `{typography.micro}` | JetBrains Mono | 10px | 600 | Huy hiệu nhóm trên nút kỹ năng |

Tiêu đề bảng dùng 11px JetBrains Mono, giãn cách 0,06em. Không có bậc chữ lớn hơn 34px.

## Layout & Spacing

Một bề mặt web. Artboard được xem ở rộng 1440px. Cột nội dung ứng dụng tối đa `{spacing.content}`, đệm ngang `{spacing.page}`. Trang chính sách tối đa `{spacing.doc}`. Trang vai trò tối đa `{spacing.role-doc}`.

Header là một hàng `flex-wrap`: wordmark, nav, chip hồ sơ. Nav cao `{spacing.nav}`, mục cách nhau 2px, tràn thì cuộn ngang. Vùng bấm được giữ tối thiểu `{spacing.target}`, trừ ô kiểm (khung 24px, nhãn là vùng bấm). Nút “chọn file khác” đang cao 36px trên artboard; cụm 3D / 2D / bảng đang cao 38px. Khi dựng, đưa cả hai về `{spacing.target}`. Spine lấy `{spacing.target}` làm sàn. Chiều cao nút chính nằm ở `button-primary`: `{components.button-primary.minHeightCompact}` trên Bản đồ và màn CV scan, `{components.button-primary.minHeight}` trên các màn ứng dụng còn lại.

Panel đệm `{spacing.panel}`. Khoảng cách dọc trong một màn thường 18–20px; khoảng giữa cụm điều khiển thường 8px hoặc 12px. Các giá trị này lặp trong `gap` của artboard, không phải một thang 4px kín.

Bản đồ 3D nằm trong khung cao 560px, `perspective: 1500px`. Dưới 640px, khung còn 420px và tỷ lệ 0,62. Trang chính sách dưới 560px xếp mục một cột.

Lối xem Bản đồ có ba chế độ trên cùng số liệu: 3D, biểu đồ 2D, bảng. “Khác” nằm ở chú thích, không chiếm cột.

## Elevation & Depth

Độ sâu của giao diện là viền 1px và lớp nền, không phải bóng đổ.

Thứ tự nền, từ sau ra trước: `{colors.canvas}`, rồi `{colors.header}` hoặc `{colors.inset}`, rồi `{colors.panel}`. Khung cảnh báo đổi nền thành `{colors.notice}` và viền `{colors.amber-deep}`.

Bóng đổ duy nhất khi đứng yên là toast: `0 12px 40px rgba(0,0,0,.5)`. Vòng chọn dùng `box-shadow: inset 0 0 0 1px {colors.selected}`. Lớp `.flash` trên màn khoảng trống là một vòng chạy một lần (`0 0 0 0` tới `0 0 0 12px`, màu selected rồi tan), không phải độ cao của thẻ.

Bản đồ tạo chiều sâu bằng `translateZ` và các mặt cột, cộng quầng `{colors.selected}` ở tâm. Không thêm bóng cho panel, nav, hay nút.

`prefers-reduced-motion: reduce` tắt animation và transition.

## Shapes

Góc chủ yếu `{rounded.md}` cho nút và `{rounded.xl}` cho panel. Chip vai trò và chip hồ sơ là `{rounded.full}` (stylesheet ghi `999px`, không phải hình tròn đầy 9999px). Ô dán và toast dùng `{rounded.lg}`. Ô thả CV dùng `{rounded.drop}`. Ô kiểm dùng `{rounded.sm}`. Thanh tỷ lệ mỏng dùng `{rounded.hair}` hoặc `{rounded.bar}`.

Nét đứt xuất hiện ở nhãn cột cỡ mẫu nhỏ, viền nút kỹ năng chưa chọn, và viền thẻ Insights khi n < 30. Nút kỹ năng trên lộ trình chung của artboard cũng nét đứt khi artboard xếp kỹ năng dưới 30% theo ngưỡng 60/30. Ngưỡng đó không phải quy tắc hình của spine; xem EXPERIENCE.md.

Logo là ô bo `{rounded.md}`, nét `{colors.primary}`, hai điểm `{colors.selected}` và một điểm `{colors.primary}`, nối bằng nét đứt `{colors.text}`.

## Components

- **`app-header`.** Nền `{colors.header}`, gạch dưới `{colors.border}`. Wordmark “HẢI ĐỒ” + dấu `{colors.primary}` + “IT”. Bốn mục nav chữ `{colors.text-muted}`, mục đang mở chữ `{colors.text}` và gạch dưới 2px `{colors.selected}`. Trang chính sách và trang vai trò không dùng nav này.
- **`profile-chip`.** Viền `{colors.border-strong}`, chữ `{colors.text-secondary}`, cao tối thiểu `{spacing.target}`. Chấm 8px: chưa có hồ sơ `{colors.slate}`; hồ sơ tạm `{colors.amber}`; đã lưu `{colors.primary}`.
- **`button-primary`.** Nền `{colors.primary}`, chữ `{colors.primary-ink}`, góc `{rounded.md}`. Trỏ chuột: nền `{colors.primary-hover}`. Tắt: nền `{colors.disabled}`, chữ `{colors.text-dim}`, `cursor: not-allowed`. Trên Bản đồ và màn CV scan, nút chính cao `{spacing.target}` và chữ `{typography.button-compact.fontSize}`. Các màn ứng dụng còn lại cao `{spacing.button}`, chữ `{typography.button.fontSize}`.
- **`button-ghost`.** Nền trong, viền `{colors.border-chip}`, chữ `{colors.text-secondary}`. Trỏ: viền `{colors.selected}`, không đổi nền, chữ `{colors.text}`.
- **`button-danger`.** Biến thể ghost của “Xoá hồ sơ khỏi trình duyệt”: viền `{colors.amber-edge}`, chữ `{colors.amber-soft}`. Trỏ: viền `{colors.amber}`, chữ `{colors.amber-softer}`.
- **`chip`.** Pill. Đang chọn: viền `{colors.selected}`, nền selected ở độ phủ 0,14, chữ `{colors.text}`. Trên màn tự chọn, trạng thái chưa chọn là nét đứt `{colors.border-dashed}` và nền trong; đã chọn thì nét liền như chip thường.
- **`icon-button`.** Vuông `{spacing.target}`, góc `{rounded.lg}`, nền `{colors.inset}`, viền `{colors.border-strong}`. Trỏ: viền `{colors.selected}`. Dùng cho xoay trái, xoay phải, đặt lại góc nhìn trên Bản đồ.
- **`segmented-control`.** Nền `{colors.inset}`, viền `{colors.border-strong}`, góc `{rounded.lg}`. Nút con góc `{rounded.segment}`. Đang chọn: nền selected 0,16 và viền trong `{colors.selected}`. Bản đồ dùng `{typography.mono-sm}`. Artboard vẽ nút cụm này cao 38px; khi dựng, đưa về `{spacing.target}`. Màn tự chọn dùng Be Vietnam Pro 14px, nút cao `{spacing.target}`.
- **`panel`.** Nền `{colors.panel}`, viền `{colors.border}`, góc `{rounded.xl}`, đệm `{spacing.panel}`.
- **`kicker`.** `{typography.kicker}`, chữ `{colors.text-muted}`, in hoa. Trên khung cảnh báo, kicker chuyển `{colors.amber}`.
- **`data-table`.** Chữ 14px. Đầu cột 11px mono, màu `{colors.text-muted}`. Hàng ngăn bằng `{colors.border-row}`. Cột số canh phải, JetBrains Mono.
- **`site-footer`.** Gạch trên `{colors.border}`, chữ mono 12px `{colors.text-muted}`, liên kết `{colors.primary}`. Một bên là câu meta, một bên là “Chính sách dữ liệu”.
- **`map-column`.** Ba cột: Hà Nội, TP.HCM, Đà Nẵng. Mặt trên `{colors.selected}`, mặt trước/sau `{colors.column-face}`, hai bên `{colors.column-side}`. Cột đang chọn đổi mặt trên thành `{colors.text}`. Cột n < 30 opacity 0,4, nhãn viền `{colors.amber-deep}`. Phần trăm của cột đó nằm trong `.rev` (`display: none`) và chỉ hiện khi trỏ, `:focus-visible`, hoặc `.tap`. Nhãn đứng là câu cỡ mẫu nhỏ, không phải phần trăm.
- **`meter`.** Rãnh `{colors.track}` hoặc `{colors.track-alt}`, phần tô `{colors.selected}`. Kỹ năng chưa có trên màn tự chọn dùng `{colors.meter-idle}`.
- **`level-bar`.** Thanh cao khoảng 26–28px, góc `{rounded.sm}`, các đoạn màu `{colors.band-deep}`, `{colors.map-line}`, `{colors.band-mid}`, `{colors.selected}`, `{colors.band-pale}`. Số đếm ghi bằng chữ cạnh thanh. Xem lưu ý ở Colors: hex không khoá theo cấp bậc.
- **`skill-node`.** Trên lộ trình chung: thẻ tuyệt đối 200×88px, nền `{colors.panel}`, góc `{rounded.lg}`, viền 1,5px. Phần trăm `{typography.mono-lg}`. Trỏ: viền `{colors.selected}`, dịch lên 2px. Trên màn tự chọn: thẻ tĩnh nền `{colors.inset}`, cùng góc; đã có thì viền và thanh `{colors.selected}`, chưa có thì viền `{colors.border}` và thanh `{colors.meter-idle}`.
- **`select`.** Nền `{colors.inset}`, chữ `{colors.text}`, viền `{colors.border-chip}`, cao `{spacing.target}`, góc `{rounded.md}`. Mũi tên là hai tam giác `{colors.selected}`.
- **`checkbox`.** Khung 24×24, viền `{colors.slate}`, góc `{rounded.sm}`. Đã chọn: nền `{colors.selected}`, dấu tích `{colors.primary-ink}`.
- **`drop-zone`.** Góc `{rounded.drop}`, đệm 28px. Viền là nét đứt vẽ bằng gradient `{colors.selected}`. Nền selected ở độ phủ 0,05.
- **`step-list`.** Bước đã xong hoặc đang chạy: chữ `{colors.text}`. Bước chờ: `{colors.text-dim}`. Thanh tiến độ rãnh `{colors.track-alt}`, tô `{colors.selected}`. Đồng hồ `{typography.mono-lg}` màu `{colors.selected}`.
- **`gap-actions`.** Hai nút chính cao `{spacing.target}`, nền `{colors.inset}`, viền `{colors.border-chip}`, chữ 14px. Đang chọn: nền selected 0,14 và viền trong `{colors.selected}`. Lựa chọn phụ là chữ gạch chân 13px `{colors.text-muted}`; khi chọn, chữ `{colors.selected}` và nặng 600. Huy hiệu “khoảng trống cốt lõi” dùng `{colors.amber}`; huy hiệu thường gặp dùng `{colors.text-muted}`.
- **`stat-block`.** Ô số tách khỏi lời dẫn: nền `{colors.inset}`, viền `{colors.border-chip}`, góc `{rounded.xl}`. Số dùng JetBrains Mono.
- **`toast`.** Cố định, giữa, cách đáy 24px. Nền `{colors.text}`, chữ `{colors.primary-ink}`, góc `{rounded.lg}`, bóng như mục Elevation. Chữ 14px nặng 600.
- **`paste-field`.** Nền `{colors.field}`, chữ `{colors.text}`, placeholder `{colors.text-placeholder}`, viền `{colors.border-chip}`, góc `{rounded.lg}`, mono 14px / 1,7. Cao tối thiểu 340px, kéo dọc được.
- **`match-ring`.** Vòng 132px, nét rãnh `{colors.track-alt}`, nét giá trị `{colors.selected}` dày 10px. Số ở tâm `{typography.match}`.
- **`sign-card`.** Nền `{colors.inset}`, viền `{colors.border-chip}`, góc `{rounded.lg}`. Ô mã D: chữ `{colors.amber}`, viền `{colors.amber-deep}`, góc `{rounded.sm}`.
- **`insight-card`.** Nền `{colors.panel}`, góc `{rounded.xl}`, đệm 18px. Số trong câu mẫu màu `{colors.selected}`. Khi n < 30: viền nét đứt `{colors.amber-deep}`, câu “chưa đủ dữ liệu” màu `{colors.amber}`, không vẽ phần trăm.
- **`notice`.** Nền `{colors.notice}`, viền `{colors.amber-deep}`, góc `{rounded.xl}`. Dùng cho nhóm so sánh đã quay về và cho CV không đọc được chữ. Kicker `{colors.amber}`.
- **`doc-section`.** Trang chính sách: tiêu đề mục `{typography.section.fontSize}`, thân `{typography.body.fontSize}` màu `{colors.text-doc}`, `line-height: 1.7`. Số mục mono. Gạch mục `{colors.border}`.

## Do's and Don'ts

| Làm | Tránh |
|---|---|
| Giữ nền `{colors.canvas}`, chữ `{colors.text}`, nút `{colors.primary}` / chữ `{colors.primary-ink}`, mục chọn `{colors.selected}` | Thêm bảng màu sáng, hoặc đổi các hex này cho “đẹp hơn” |
| Đặt số, n, ngày, phần trăm bằng JetBrains Mono | Viết phần trăm bằng Be Vietnam Pro cho khỏi “lệch font” |
| Tạo lớp bằng viền và nền | Thêm bóng đổ cho panel, nav, nút. Bóng đứng yên chỉ có ở toast |
| Giữ lưới 40px, selected ở độ phủ 0,04, trên màn ứng dụng đang có lưới | Kéo lưới sang trang chính sách và trang vai trò; hai trang đó không có lưới |
| Vẽ cột n < 30, mờ, nhãn cỡ mẫu nhỏ luôn hiện, phần trăm chỉ khi trỏ, chạm hoặc focus | Ẩn cột Đà Nẵng, hoặc in sẵn phần trăm lên nhãn cột mờ |
| Để “Khác” trong chú thích, kèm tỷ trọng, sao cho cột + Khác = 100% | Vẽ “Khác” thành một cột |
| Dùng hổ phách cho mẫu nhỏ, chưa đủ dữ liệu, hồ sơ tạm | Dùng hổ phách để kết luận tin giả |
| Lấy `{spacing.target}` làm sàn vùng bấm | Giữ nút 36px của artboard “chọn file khác” |
| Khi mock lệch spine, làm theo spine | Chép ngưỡng 60% / 30% in trên artboard vào sản phẩm |
