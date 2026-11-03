# Claude Design (1).html — nội dung thiết kế 15 màn

Lấy từ thẻ `__bundler/template` của từng màn trong file xuất `(1).html`.
Phần CSS đã bỏ `@font-face`. Đây là trích để chưng cất, không phải spine.

## 01
- html: `.working/screens-inner/01.html` (40258 bytes)

### Chữ trên màn

- Bản đồ nhu cầu 3D
- HẢI ĐỒ
- ·
- IT
- Bản đồ
- Insights
- Cố vấn
- Soi tin
- Chưa có hồ sơ
- Bản đồ nhu cầu
- Tin tuyển dụng của một vai trò nằm ở đâu. Chiều cao cột là phần trăm số tin của vai trò đó trên toàn quốc được đăng ở mỗi nơi.
- Snapshot 02/11/2026 · 1.214 tin IT
- {{r.label}}
- {{v.label}}
- Tin {{roleName}} nằm ở đâu · mọi cấp bậc · n = {{tot}}
- QĐ. Hoàng Sa
- QĐ. Trường Sa
- {{c.name}} ›
- {{c.valText}}
- {{c.name}}
- {{c.valText}}
- {{c.smallLabel}}
- Kéo để xoay · kéo dọc để nghiêng · cột mờ = cỡ mẫu nhỏ, trỏ hoặc chạm nhãn để xem tỷ trọng
- {{b.name}}
- {{b.valText}}
- {{b.valText}}
- Trỏ hoặc chạm để xem %
- {{b.smallLabel}}
- Tin {{roleName}} nằm ở đâu · n = {{tot}} · snapshot 02/11/2026
- Nơi
- Tỷ trọng
- Tin {{roleName}}
- Ghi chú
- {{r.name}}
- {{r.p}}%
- {{r.p}}%
- Trỏ hoặc chạm để xem %
- {{r.kFmt}}
- {{r.note}}
- Tổng
- 100%
- {{tot}}
- Ba nơi trên bản đồ + Khác
- {{othText}}
- Khác {{othVal}} · cộng với các cột = 100%
- Tin {{roleName}} nằm ở đâu
- {{r.name}}
- {{r.p}}%
- {{r.p}}%
- Trỏ hoặc chạm để xem %
- {{r.kFmt}} / {{tot}} tin · 02/11/2026
- {{r.smallLabel}}
- {{othText}}
- {{othVal}}
- Xem chi tiết Hà Nội
- Đọc số này thế nào
- Chỉ gồm tin đăng công khai trên các nguồn đang bật. Tin tuyển nội bộ hay qua giới thiệu không có ở đây.
- Tin trùng giữa các nguồn đã được gộp. Một tin là một vị trí, không phải số người được tuyển.
- Nơi ít tin thì số liệu dao động mạnh. Dưới 30 tin được đánh dấu “cỡ mẫu nhỏ”, cột để mờ và phần trăm chỉ hiện khi bạn trỏ hoặc chạm.
- Nguồn đang bật: [Nguồn 1], [Nguồn 2] · Snapshot 02/11/2026 · n = 1.214 tin IT
- Hải Đồ IT không khuyên nộp hay không nộp. Số liệu là tổng hợp, không lưu CV hay tin bạn dán.
- Chính sách dữ liệu
- class Component extends DCLogic { constructor(props) { super(props); this.state = { role: 'be', view: '3d', rx: 0, rz: -16, grown: false, dragging: false, sel: '' }; this.t0 = null; this.drag = null; } componentDidMount() { var self = this; this.t0 = setTimeout(function () { self.setState({ rx: 56, grown: true }); }, 250); } componentWillUnmount() { if (this.t0) clearTimeout(this.t0); } renderVals() { var self = this, st = this.state; var ROLES = [['be', 'Backend'], ['fe', 'Frontend'], ['data', 'Data'], ['qa', 'QA/Tester'], ['ops', 'DevOps'], ['mob', 'Mobile']]; var PL = [ { id: 'hn', name: 'Hà Nội', px: 143, py: 88 }, { id: 'hcm', name: 'TP.HCM', px: 174, py: 467 }, { id: 'dn', name: 'Đà Nẵng', px: 230, py: 272 }, { id: 'oth', name: 'Khác' } ]; var K = { be: [143, 198, 23, 10], fe: [79, 93, 18, 9], data: [55, 76, 5, 3], qa: [46, 52, 11, 12], ops: [37, 52, 4, 8], mob: [42, 46, 9, 9] }; var role = st.role; var roleName = ROLES.filter(function (r) { return r[0] === role; })[0][1]; var fmt = function (n) { return n.toLocaleString('vi-VN'); }; var ks = K[role], tot = ks.reduce(function (a, b) { return a + b; }, 0); var raw = ks.map(function (k) { return 100 * k / tot; }); var pc = raw.map(function (r) { return Math.floor(r); }); var rest = 100 - pc.reduce(function (a, b) { return a + b; }, 0); raw.map(function (r, i) { return [r - pc[i], i]; }).sort(function (a, b) { return b[0] - a[0]; }).slice(0, rest).forEach(function (x) { pc[x[1]] += 1; }); var tap = st.sel === 'dn'; var D = PL.map(function (pl, i) { var k = ks[i], p = pc[i], sm = pl.id !== 'oth' && k

### CSS (không font-face)

```css
/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

body{margin:0;background:#070B10}
a{color:#C5F36A}a:hover{color:#E4FFB5}
.root{font-family:'Be Vietnam Pro',system-ui,sans-serif;color:#E6EDF3;background-color:#070B10;background-image:linear-gradient(rgba(98,217,238,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(98,217,238,.04) 1px,transparent 1px);background-size:40px 40px;min-height:100vh;display:flex;flex-direction:column}
.mono{font-family:'JetBrains Mono',ui-monospace,Menlo,monospace}
.k{font:600 11px/1.4 'JetBrains Mono',ui-monospace,monospace;color:#9FB0C2;letter-spacing:.08em;text-transform:uppercase}
.wrap{width:100%;max-width:1280px;margin:0 auto;padding:0 24px;box-sizing:border-box}
.hdr{border-bottom:1px solid #1C2A36;background:#0A1017}
.logo{display:inline-flex;align-items:center;gap:10px;text-decoration:none;color:#E6EDF3;font-weight:700;font-size:16px;letter-spacing:.04em;min-height:44px}
.logo:hover{color:#E6EDF3}
.nav{display:flex;gap:2px;flex:1 1 auto;min-width:0;overflow-x:auto}
.nav a{display:inline-flex;align-items:center;min-height:52px;padding:0 14px;color:#9FB0C2;text-decoration:none;font-weight:500;font-size:14px;border-bottom:2px solid transparent;white-space:nowrap}
.nav a:hover{color:#E6EDF3}
.nav a.on{color:#E6EDF3;border-bottom-color:#62D9EE}
.prof{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 14px;border-radius:999px;border:1px solid #243543;color:#C4D0DC;font-size:12px;text-decoration:none;white-space:nowrap;box-sizing:border-box}
.prof:hover{border-color:#62D9EE;color:#E6EDF3}
.panel{border:1px solid #1C2A36;background:#0D141C;border-radius:12px;padding:20px;box-sizing:border-box}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:44px;padding:0 18px;border-radius:8px;border:0;background:#C5F36A;color:#0A0F05;font:600 14px 'Be Vietnam Pro',sans-serif;text-decoration:none;cursor:pointer}
.btn:hover{color:#0A0F05;background:#D6FA94}
.chip{display:inline-flex;align-items:center;gap:6px;min-height:44px;padding:0 14px;border-radius:999px;border:1px solid #2E4456;background:#0A1118;color:#C4D0DC;font:500 13px 'Be Vietnam Pro',sans-serif;cursor:pointer;box-sizing:border-box}
.chip:hover{border-color:#62D9EE}
.chip.on{border-color:#62D9EE;background:rgba(98,217,238,.14);color:#E6EDF3}
.seg{display:inline-grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:3px;padding:3px;border:1px solid #243543;border-radius:10px;background:#0A1118}
.seg button{min-height:38px;padding:0 14px;border:0;border-radius:7px;background:transparent;color:#A9B8C7;font:600 12px 'JetBrains Mono',monospace;cursor:pointer}
.seg button.on{background:rgba(98,217,238,.16);color:#E6EDF3;box-shadow:inset 0 0 0 1px #62D9EE}
.ibtn{width:44px;height:44px;border-radius:10px;border:1px solid #243543;background:#0A1118;color:#C4D0DC;display:inline-flex;align-items:center;justify-content:center;cursor:pointer;padding:0}
.ibtn:hover{border-color:#62D9EE;color:#E6EDF3}
.foot{border-top:1px solid #1C2A36;margin-top:auto}
a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible{outline:2px solid #C5F36A;outline-offset:2px}
.viewport{position:relative;height:560px;perspective:1500px;perspective-origin:50% 18%;display:flex;align-items:center;justify-content:center;overflow:hidden;cursor:grab;touch-action:none;user-select:none;-webkit-user-select:none;background:radial-gradient(ellipse at 50% 60%,rgba(98,217,238,.08),transparent 60%)}
.viewport.dragging{cursor:grabbing}
.scaler{transform-style:preserve-3d}
@media (max-width:640px){.viewport{height:420px}.scaler{transform:scale(.62)}}
.stage{position:relative;flex:none;width:460px;height:560px;transform-style:preserve-3d;transition:transform 1.4s cubic-bezier(.2,.7,.2,1)}
.plate{position:absolute;left:-170px;top:-120px;width:800px;height:800px;transform:translateZ(-44px);background-image:linear-gradient(rgba(98,217,238,.13) 1px,transparent 1px),linear-gradient(90deg,rgba(98,217,238,.13) 1px,transparent 1px);background-size:40px 40px;-webkit-mask-image:radial-gradient(circle at 50% 50%,#000 25%,transparent 66%);mask-image:radial-gradient(circle at 50% 50%,#000 25%,transparent 66%);pointer-events:none}
.slab{position:absolute;left:0;top:0;width:460px;height:560px;overflow:visible;pointer-events:none}
.col{position:absolute;transform-style:preserve-3d;transform:translate(-50%,-50%)}
.f{position:absolute;display:block;box-sizing:border-box;transition:width 1.1s cubic-bezier(.2,.7,.2,1),height 1.1s cubic-bezier(.2,.7,.2,1),transform 1.1s cubic-bezier(.2,.7,.2,1),background .3s}
.f.top{left:0;top:0;width:100%;height:100%}
.f.fr,.f.bk{left:0;width:100%;transform-origin:top center;transform:rotateX(90deg)}
.f.fr{top:100%}.f.bk{top:0}
.f.lf,.f.rt{top:0;height:100%;transform-origin:left center;transform:rotateY(-90deg)}
.f.lf{left:0}.f.rt{left:100%}
.rev{display:none}
.bb:hover .rev,.bb:focus-visible .rev,.bb.tap .rev,.rv:hover .rev,.rv:focus-visible .rev,.rv.tap .rev{display:inline}
.rv:hover .hid,.rv:focus-visible .hid,.rv.tap .hid{display:none}
.rv{display:inline-flex;align-items:center;justify-content:flex-end;min-height:44px;padding:0 10px;border:1px dashed #5A4426;border-radius:8px;background:transparent;color:#E6EDF3;font:600 13px 'JetBrains Mono',monospace;cursor:pointer;white-space:nowrap}
.rv:hover{border-color:#F5A65B}
.bb.sm{border-color:#5A4426}
.glow3{position:absolute;left:50%;top:50%;width:96px;height:96px;border-radius:50%;background:radial-gradient(circle,rgba(98,217,238,.38),rgba(98,217,238,0) 70%);transform:translate(-50%,-50%);pointer-events:none}
.bb{position:absolute;left:50%;top:50%;transform-origin:0 0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1px;min-height:44px;padding:4px 10px;border-radius:8px;border:1px solid #2E4456;background:rgba(7,11,16,.94);color:#E6EDF3;cursor:pointer;white-space:nowrap;text-decoration:none;box-sizing:border-box;transition:transform 1.1s cubic-bezier(.2,.7,.2,1),border-color .2s;font-family:'Be Vietnam Pro',sans-serif}
.bb:hover{border-color:#62D9EE;color:#E6EDF3}
.bb.go{border-color:#62D9EE}
.viewport.dragging .stage,.viewport.dragging .f,.viewport.dragging .bb{transition:none}
.hatch{background-image:repeating-linear-gradient(135deg,rgba(98,217,238,.35) 0 4px,rgba(98,217,238,.08) 4px 8px)}
.tbl{width:100%;border-collapse:collapse;font-size:14px}
.tbl th{font:600 11px 'JetBrains Mono',monospace;color:#9FB0C2;letter-spacing:.06em;text-align:left;padding:10px 12px;border-bottom:1px solid #1C2A36}
.tbl td{padding:12px;border-bottom:1px solid #15212B}
.tbl td.num,.tbl th.num{text-align:right;font-family:'JetBrains Mono',monospace}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
```

### Script (rút)

```js

```

## 02
- html: `.working/screens-inner/02.html` (24268 bytes)

### Chữ trên màn

- Chi tiết Hà Nội
- HẢI ĐỒ
- ·
- IT
- Bản đồ
- Insights
- Cố vấn
- Soi tin
- Chưa có hồ sơ
- Bản đồ
- ›
- Hà Nội
- Hà Nội
- 462
- tin IT
- Snapshot 02/11/2026 · [Nguồn 1], [Nguồn 2]
- ← Quay lại bản đồ
- Tỷ trọng vai trò ở Hà Nội
- n = 462 tin · 02/11/2026
- {{r.label}}
- {{r.pct}}%
- · {{r.k}}/462
- Chạm một vai trò để xem kỹ năng hàng đầu bên dưới.
- Kỹ năng hàng đầu · {{roleName}} · Hà Nội
- n = {{roleN}} tin · 02/11/2026
- Tỷ lệ = số tin {{roleName}} ở Hà Nội có nhắc kỹ năng đó, chia cho {{roleN}} tin.
- KỸ NĂNG
- TỶ LỆ TIN
- SỐ TIN / n
- {{s.name}}
- {{s.p}}%
- {{s.k}}/{{roleN}}
- Xem lộ trình học và đối chiếu CV cho vai trò này
- Mở Cố vấn với vai trò {{roleName}} đã chọn sẵn.
- Chỉ gồm tin công khai trên các nguồn đang bật · tin trùng đã gộp · snapshot 02/11/2026
- Chính sách dữ liệu
- class Component extends DCLogic { constructor(props) { super(props); this.state = { role: 'be' }; } renderVals() { var self = this, st = this.state; var R = [ { id: 'be', label: 'Backend', pct: 31, k: 143, sk: [['SQL', 76], ['Java', 58], ['Git', 55], ['REST API', 52], ['Spring Boot', 44], ['Docker', 41], ['PostgreSQL', 33], ['MySQL', 31]] }, { id: 'fe', label: 'Frontend', pct: 17, k: 79, sk: [['JavaScript', 86], ['React', 71], ['TypeScript', 58], ['HTML/CSS', 54], ['Git', 49], ['Next.js', 27]] }, { id: 'data', label: 'Data', pct: 12, k: 55, sk: [['SQL', 89], ['Python', 82], ['Excel', 40], ['Power BI', 36], ['Spark', 33], ['Airflow', 25]] }, { id: 'qa', label: 'QA/Tester', pct: 10, k: 46, sk: [['Kiểm thử thủ công', 78], ['SQL', 50], ['Selenium', 41], ['Postman', 39], ['Jira', 35], ['Playwright', 22]] }, { id: 'mob', label: 'Mobile', pct: 9, k: 42, sk: [['Git', 52], ['Flutter', 48], ['Kotlin', 45], ['Swift', 38], ['React Native', 31], ['Firebase', 29]] }, { id: 'ops', label: 'DevOps', pct: 8, k: 37, sk: [['Linux', 84], ['Docker', 81], ['Kubernetes', 62], ['CI/CD', 59], ['AWS', 51], ['Terraform', 32]] }, { id: 'other', label: 'Vai trò khác', pct: 13, k: 60, sk: null } ]; var cur = R.filter(function (r) { return r.id === st.role; })[0]; return { roles: R.map(function (r) { var on = r.id === st.role, can = !!r.sk; return { label: r.label, pct: r.pct, k: r.k, w: Math.round(100 * r.pct / 31), on: on, color: on ? '#62D9EE' : '#2E5A6A', bg: on ? 'rgba(98,217,238,.10)' : 'transparent', ring: on ? 'inset 0 0 0 1px #62D9EE' : 'none', weight: on ? 600 : 400, pick: function () { if (can) self.setState({ role: r.id }); } }; }), roleName: cur.label, roleN: cur.k, skills: cur.sk.map(function (s) { return { name: s[0], p: s[1], k: Math.round(s[1] * cur.k / 100) }; }) }; } }

### CSS (không font-face)

```css
/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

body{margin:0;background:#070B10}
a{color:#C5F36A}a:hover{color:#E4FFB5}
.root{font-family:'Be Vietnam Pro',system-ui,sans-serif;color:#E6EDF3;background-color:#070B10;background-image:linear-gradient(rgba(98,217,238,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(98,217,238,.04) 1px,transparent 1px);background-size:40px 40px;min-height:100vh;display:flex;flex-direction:column}
.mono{font-family:'JetBrains Mono',ui-monospace,Menlo,monospace}
.k{font:600 11px/1.4 'JetBrains Mono',ui-monospace,monospace;color:#9FB0C2;letter-spacing:.08em;text-transform:uppercase}
.wrap{width:100%;max-width:1280px;margin:0 auto;padding:0 24px;box-sizing:border-box}
.hdr{border-bottom:1px solid #1C2A36;background:#0A1017}
.logo{display:inline-flex;align-items:center;gap:10px;text-decoration:none;color:#E6EDF3;font-weight:700;font-size:16px;letter-spacing:.04em;min-height:44px}
.logo:hover{color:#E6EDF3}
.nav{display:flex;gap:2px;flex:1 1 auto;min-width:0;overflow-x:auto}
.nav a{display:inline-flex;align-items:center;min-height:52px;padding:0 14px;color:#9FB0C2;text-decoration:none;font-weight:500;font-size:14px;border-bottom:2px solid transparent;white-space:nowrap}
.nav a:hover{color:#E6EDF3}
.nav a.on{color:#E6EDF3;border-bottom-color:#62D9EE}
.prof{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 14px;border-radius:999px;border:1px solid #243543;color:#C4D0DC;font-size:12px;text-decoration:none;white-space:nowrap;box-sizing:border-box}
.prof:hover{border-color:#62D9EE;color:#E6EDF3}
.panel{border:1px solid #1C2A36;background:#0D141C;border-radius:12px;padding:20px;box-sizing:border-box}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:48px;padding:0 20px;border-radius:8px;border:0;background:#C5F36A;color:#0A0F05;font:600 15px 'Be Vietnam Pro',sans-serif;text-decoration:none;cursor:pointer}
.btn:hover{color:#0A0F05;background:#D6FA94}
.ghost{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:44px;padding:0 16px;border-radius:8px;border:1px solid #2E4456;background:transparent;color:#C4D0DC;font:500 14px 'Be Vietnam Pro',sans-serif;text-decoration:none;cursor:pointer}
.ghost:hover{border-color:#62D9EE;color:#E6EDF3}
.chip{display:inline-flex;align-items:center;gap:6px;min-height:44px;padding:0 14px;border-radius:999px;border:1px solid #2E4456;background:#0A1118;color:#C4D0DC;font:500 13px 'Be Vietnam Pro',sans-serif;cursor:pointer;box-sizing:border-box}
.chip:hover{border-color:#62D9EE}
.chip.on{border-color:#62D9EE;background:rgba(98,217,238,.14);color:#E6EDF3}
.foot{border-top:1px solid #1C2A36;margin-top:auto}
a:focus-visible,button:focus-visible{outline:2px solid #C5F36A;outline-offset:2px}
@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.bar{transform-origin:left center;animation:grow .9s cubic-bezier(.2,.7,.2,1) both;transition:width .5s}
@keyframes slidein{from{opacity:0;transform:translateX(24px)}to{opacity:1;transform:none}}
.drawer{animation:slidein .5s cubic-bezier(.2,.7,.2,1) both}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
```

### Script (rút)

```js

```

## 03
- html: `.working/screens-inner/03.html` (26661 bytes)

### Chữ trên màn

- Cố vấn — lộ trình Backend
- HẢI ĐỒ
- ·
- IT
- Bản đồ
- Insights
- Cố vấn
- Soi tin
- Chưa có hồ sơ
- Lộ trình kỹ năng
- Mỗi nút là một kỹ năng, kèm tỷ lệ tin trong nhóm so sánh có nhắc tới nó.
- Snapshot 02/11/2026 · [Nguồn 1], [Nguồn 2]
- Vai trò
- Backend
- Frontend
- Data Engineer
- QA/Tester
- Nhánh
- {{b.label}}
- {{b.ct}}
- Cấp bậc
- Intern
- Fresher
- Junior
- Nhóm so sánh đã quay về
- Java Backend · Intern–Junior hiện có
- 26 tin
- , chưa đủ 30. Hải Đồ giữ nguyên cấp bậc bạn chọn và dùng
- Backend · Intern–Junior (n = 52)
- làm nhóm so sánh.
- Cơ cấu cấp bậc · n = 52 · 02/11/2026
- Intern 13
- Fresher 7
- Junior 32
- Nhóm so sánh: Backend · Intern–Junior · n = 52 · 02/11/2026
- Backend · Intern–Junior
- Cốt lõi ≥ 60%
- Thường gặp 30–59%
- Riêng của công ty &lt; 30%
- CHẶNG 1 · NỀN TẢNG
- CHẶNG 2 · FRAMEWORK &amp; DỮ LIỆU
- CHẶNG 3 · TRIỂN KHAI &amp; HIỆU NĂNG
- RIÊNG CỦA CÔNG TY
- {{n.name}}
- {{n.tier}}
- {{n.p}}%
- {{n.k}}/52 tin
- Đường nối = kỹ năng thường được học trước. Tỷ lệ = số tin có nhắc kỹ năng / 52 tin · snapshot 02/11/2026. Bấm một nút để xem vì sao thị trường cần.
- Bạn đã có những kỹ năng nào trong số này?
- Đối chiếu với CV để thấy khoảng trống, hoặc tự đánh dấu nếu chưa có CV.
- Chưa có CV — tự chọn kỹ năng
- Đối chiếu với CV của tôi
- Nhóm dưới 30 tin không được dùng làm nhóm so sánh · snapshot 02/11/2026
- Chính sách dữ liệu
- class Component extends DCLogic { constructor(props) { super(props); this.state = { branch: 'java' }; } renderVals() { var self = this, st = this.state; var B = [['all', 'Tất cả Backend', '52 tin', false], ['java', 'Java Backend', '26 tin ·
- = 60 ? 'CỐT LÕI' : p >= 30 ? 'THƯỜNG GẶP' : 'RIÊNG CÔNG TY'; return { name: n[0], k: n[1], p: p, x: n[2], y: n[3], tier: tier, d: (i * 0.05).toFixed(2), bc: p >= 60 ? '#62D9EE' : '#4A6478', bs: p >= 30 ? 'solid' : 'dashed', tc: p >= 60 ? '#62D9EE' : '#9FB0C2', op: p >= 30 ? 1 : 0.75, aria: n[0] + ': ' + p + '% (' + n[1] + ' trên 52 tin), ' + tier.toLowerCase() }; }) }; } }

### CSS (không font-face)

```css
/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

body{margin:0;background:#070B10}
a{color:#C5F36A}a:hover{color:#E4FFB5}
.root{font-family:'Be Vietnam Pro',system-ui,sans-serif;color:#E6EDF3;background-color:#070B10;background-image:linear-gradient(rgba(98,217,238,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(98,217,238,.04) 1px,transparent 1px);background-size:40px 40px;min-height:100vh;display:flex;flex-direction:column}
.mono{font-family:'JetBrains Mono',ui-monospace,Menlo,monospace}
.k{font:600 11px/1.4 'JetBrains Mono',ui-monospace,monospace;color:#9FB0C2;letter-spacing:.08em;text-transform:uppercase}
.wrap{width:100%;max-width:1280px;margin:0 auto;padding:0 24px;box-sizing:border-box}
.hdr{border-bottom:1px solid #1C2A36;background:#0A1017}
.logo{display:inline-flex;align-items:center;gap:10px;text-decoration:none;color:#E6EDF3;font-weight:700;font-size:16px;letter-spacing:.04em;min-height:44px}
.logo:hover{color:#E6EDF3}
.nav{display:flex;gap:2px;flex:1 1 auto;min-width:0;overflow-x:auto}
.nav a{display:inline-flex;align-items:center;min-height:52px;padding:0 14px;color:#9FB0C2;text-decoration:none;font-weight:500;font-size:14px;border-bottom:2px solid transparent;white-space:nowrap}
.nav a:hover{color:#E6EDF3}
.nav a.on{color:#E6EDF3;border-bottom-color:#62D9EE}
.prof{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 14px;border-radius:999px;border:1px solid #243543;color:#C4D0DC;font-size:12px;text-decoration:none;white-space:nowrap;box-sizing:border-box}
.prof:hover{border-color:#62D9EE;color:#E6EDF3}
.panel{border:1px solid #1C2A36;background:#0D141C;border-radius:12px;padding:20px;box-sizing:border-box}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:48px;padding:0 20px;border-radius:8px;border:0;background:#C5F36A;color:#0A0F05;font:600 15px 'Be Vietnam Pro',sans-serif;text-decoration:none;cursor:pointer}
.btn:hover{color:#0A0F05;background:#D6FA94}
.ghost{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:44px;padding:0 16px;border-radius:8px;border:1px solid #2E4456;background:transparent;color:#C4D0DC;font:500 14px 'Be Vietnam Pro',sans-serif;text-decoration:none;cursor:pointer}
.ghost:hover{border-color:#62D9EE;color:#E6EDF3}
.chip{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 14px;border-radius:999px;border:1px solid #2E4456;background:#0A1118;color:#C4D0DC;font:500 13px 'Be Vietnam Pro',sans-serif;cursor:pointer;box-sizing:border-box}
.chip:hover{border-color:#62D9EE}
.chip.on{border-color:#62D9EE;background:rgba(98,217,238,.14);color:#E6EDF3}
.chip .ct{font:600 11px 'JetBrains Mono',monospace;color:#9FB0C2}
.chip .ct.warn{color:#F5A65B}
.sel{appearance:none;min-height:44px;padding:0 36px 0 14px;border-radius:8px;border:1px solid #2E4456;background:#0A1118;color:#E6EDF3;font:600 14px 'Be Vietnam Pro',sans-serif;background-image:linear-gradient(45deg,transparent 50%,#62D9EE 50%),linear-gradient(135deg,#62D9EE 50%,transparent 50%);background-position:calc(100% - 18px) 19px,calc(100% - 13px) 19px;background-size:5px 5px;background-repeat:no-repeat}
.node{position:absolute;width:200px;height:88px;box-sizing:border-box;border-radius:10px;background:#0D141C;padding:10px 12px;display:flex;flex-direction:column;justify-content:space-between;text-decoration:none;color:#E6EDF3;transition:border-color .2s,transform .2s}
.node:hover{color:#E6EDF3;transform:translateY(-2px);border-color:#62D9EE!important}
.foot{border-top:1px solid #1C2A36;margin-top:auto}
a:focus-visible,button:focus-visible,select:focus-visible{outline:2px solid #C5F36A;outline-offset:2px}
@keyframes pop{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.pop{animation:pop .5s cubic-bezier(.2,.7,.2,1) both}
@keyframes draw{from{stroke-dashoffset:400}to{stroke-dashoffset:0}}
.edge{stroke-dasharray:400;animation:draw 1.2s .3s ease-out both}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
```

### Script (rút)

```js

```

## 04
- html: `.working/screens-inner/04.html` (22132 bytes)

### Chữ trên màn

- Đối chiếu CV — đồng ý và tải lên
- HẢI ĐỒ
- ·
- IT
- Bản đồ
- Insights
- Cố vấn
- Soi tin
- Chưa có hồ sơ
- Cố vấn · Backend · Intern–Junior
- ›
- Đối chiếu CV
- Đối chiếu CV với Backend · Intern–Junior
- Nhóm so sánh: n = 52 tin · snapshot 02/11/2026. Kết quả là danh sách kỹ năng đã có và khoảng trống, không phải lời khuyên nộp hồ sơ.
- PDF
- CV_Minh_JavaBackend.pdf
- 184 KB · PDF có lớp chữ · đọc ngay trên trình duyệt
- ✓ ĐÃ THẢ
- Kéo thả file vào đây, hoặc
- chọn file khác
- PDF có lớp chữ hoặc DOCX · tối đa 5 MB
- Tôi đồng ý gửi
- văn bản trích từ CV
- tới
- một dịch vụ AI bên ngoài
- để nhận diện tên kỹ năng. Văn bản này
- không được lưu lại
- .
- Gửi đi
- Chỉ phần chữ trong CV. File gốc ở lại máy bạn.
- Để làm gì
- Nhận diện tên kỹ năng, rồi so với nhóm 52 tin.
- Lưu lại
- Không. Chỉ danh sách kỹ năng nằm trong trình duyệt của bạn.
- Đọc CV và đối chiếu
- Đọc CV và đối chiếu
- Đánh dấu ô đồng ý ở trên để tiếp tục.
- Không muốn gửi CV? Tự chọn kỹ năng →
- Prototype: xem trường hợp CV là PDF ảnh scan
- CV không được lưu trên máy chủ Hải Đồ IT.
- Chính sách dữ liệu
- class Component extends DCLogic { constructor(props) { super(props); this.state = { consent: false }; } renderVals() { var self = this, on = this.state.consent; return { consent: on, noConsent: !on, consentBorder: on ? '#62D9EE' : '#1C2A36', toggle: function (e) { self.setState({ consent: !!e.target.checked }); } }; } }

### CSS (không font-face)

```css
/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

body{margin:0;background:#070B10}
a{color:#C5F36A}a:hover{color:#E4FFB5}
.root{font-family:'Be Vietnam Pro',system-ui,sans-serif;color:#E6EDF3;background-color:#070B10;background-image:linear-gradient(rgba(98,217,238,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(98,217,238,.04) 1px,transparent 1px);background-size:40px 40px;min-height:100vh;display:flex;flex-direction:column}
.mono{font-family:'JetBrains Mono',ui-monospace,Menlo,monospace}
.k{font:600 11px/1.4 'JetBrains Mono',ui-monospace,monospace;color:#9FB0C2;letter-spacing:.08em;text-transform:uppercase}
.wrap{width:100%;max-width:1280px;margin:0 auto;padding:0 24px;box-sizing:border-box}
.hdr{border-bottom:1px solid #1C2A36;background:#0A1017}
.logo{display:inline-flex;align-items:center;gap:10px;text-decoration:none;color:#E6EDF3;font-weight:700;font-size:16px;letter-spacing:.04em;min-height:44px}
.logo:hover{color:#E6EDF3}
.nav{display:flex;gap:2px;flex:1 1 auto;min-width:0;overflow-x:auto}
.nav a{display:inline-flex;align-items:center;min-height:52px;padding:0 14px;color:#9FB0C2;text-decoration:none;font-weight:500;font-size:14px;border-bottom:2px solid transparent;white-space:nowrap}
.nav a:hover{color:#E6EDF3}
.nav a.on{color:#E6EDF3;border-bottom-color:#62D9EE}
.prof{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 14px;border-radius:999px;border:1px solid #243543;color:#C4D0DC;font-size:12px;text-decoration:none;white-space:nowrap;box-sizing:border-box}
.prof:hover{border-color:#62D9EE;color:#E6EDF3}
.panel{border:1px solid #1C2A36;background:#0D141C;border-radius:12px;padding:20px;box-sizing:border-box}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:48px;padding:0 22px;border-radius:8px;border:0;background:#C5F36A;color:#0A0F05;font:600 15px 'Be Vietnam Pro',sans-serif;text-decoration:none;cursor:pointer}
.btn:hover{color:#0A0F05;background:#D6FA94}
.btn:disabled{background:#2A3A44;color:#8496A6;cursor:not-allowed}
.ghost{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:44px;padding:0 16px;border-radius:8px;border:1px solid #2E4456;background:transparent;color:#C4D0DC;font:500 14px 'Be Vietnam Pro',sans-serif;text-decoration:none;cursor:pointer}
.ghost:hover{border-color:#62D9EE;color:#E6EDF3}
.foot{border-top:1px solid #1C2A36;margin-top:auto}
a:focus-visible,button:focus-visible,input:focus-visible{outline:2px solid #C5F36A;outline-offset:2px}
@keyframes dashmove{to{background-position:24px 0,-24px 100%,0 -24px,100% 24px}}
.drop{border-radius:14px;padding:28px;background:linear-gradient(90deg,#62D9EE 50%,transparent 0) repeat-x,linear-gradient(90deg,#62D9EE 50%,transparent 0) repeat-x,linear-gradient(0deg,#62D9EE 50%,transparent 0) repeat-y,linear-gradient(0deg,#62D9EE 50%,transparent 0) repeat-y;background-size:12px 1.5px,12px 1.5px,1.5px 12px,1.5px 12px;background-position:0 0,0 100%,0 0,100% 0;background-color:rgba(98,217,238,.05);animation:dashmove 1s linear 3}
@keyframes land{0%{opacity:0;transform:translateY(-26px) rotate(-6deg)}70%{opacity:1;transform:translateY(3px) rotate(1deg)}100%{opacity:1;transform:none}}
.land{animation:land .7s cubic-bezier(.2,.7,.2,1) both}
.check{appearance:none;width:24px;height:24px;margin:0;border-radius:6px;border:1.5px solid #4A6478;background:#0A1118;display:inline-grid;place-content:center;cursor:pointer;flex:none}
.check:checked{background:#62D9EE;border-color:#62D9EE}
.check:checked::after{content:'';width:10px;height:6px;border-left:2.5px solid #0A0F05;border-bottom:2.5px solid #0A0F05;transform:rotate(-45deg) translate(1px,-1px)}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
```

### Script (rút)

```js

```

## 05
- html: `.working/screens-inner/05.html` (21630 bytes)

### Chữ trên màn

- Đang đọc CV
- HẢI ĐỒ
- ·
- IT
- Bản đồ
- Insights
- Cố vấn
- Soi tin
- Chưa có hồ sơ
- CV_Minh_JavaBackend.pdf → Backend · Intern–Junior (n = 52)
- {{title}}
- {{elapsed}}
- / ~9 giây
- {{s.label}}
- {{s.note}}
- {{f.name}}
- {{s.time}}
- Xem khoảng trống kỹ năng
- Chạy lại mô phỏng
- Huỷ
- Văn bản CV không được lưu lại sau khi đọc xong.
- Nhóm so sánh: Backend · Intern–Junior · n = 52 · snapshot 02/11/2026
- Chính sách dữ liệu
- class Component extends DCLogic { constructor(props) { super(props); this.state = { t: 0 }; this.timer = null; } componentDidMount() { this.start(); } componentWillUnmount() { if (this.timer) clearInterval(this.timer); } start() { var self = this; if (this.timer) clearInterval(this.timer); this.setState({ t: 0 }); this.timer = setInterval(function () { var t = self.state.t + 100; if (t >= 8800) { clearInterval(self.timer); self.timer = null; t = 8800; } self.setState({ t: t }); }, 100); } renderVals() { var self = this, t = this.state.t; var S = [ ['Đọc chữ trong CV_Minh_JavaBackend.pdf', '2.143 ký tự · đọc ngay trên trình duyệt', 1000], ['Gửi văn bản tới dịch vụ AI để nhận diện kỹ năng', 'chỉ gửi phần chữ · không lưu lại', 3200], ['Chuẩn hoá tên kỹ năng theo danh mục', 'ví dụ: “Spring” → Spring Boot, “REST” → REST API', 1500], ['Đối chiếu với 52 tin Backend · Intern–Junior', 'snapshot 02/11/2026 · [Nguồn 1], [Nguồn 2]', 1800], ['Xếp khoảng trống: cốt lõi, thường gặp, riêng công ty', 'ngưỡng 60% và 30% số tin', 1300] ]; var acc = 0, total = 8800; var steps = S.map(function (s, i) { var st0 = acc, st1 = acc + s[2]; acc = st1; var done = t >= st1, run = !done && t >= st0; return { label: s[0], note: s[1], done: done, run: run, wait: !done && !run, color: done || run ? '#E6EDF3' : '#8496A6', time: done ? ((st1 - st0) / 1000).toFixed(1).replace('.', ',') + ' giây' : '', showChips: i === 2 && done, st0: st0, dur: s[2] }; }); var fin = t >= total; return { title: fin ? 'Đã đọc xong CV' : 'Đang đọc CV của bạn', elapsed: (t / 1000).toFixed(1).replace('.', ',') + ' giây', pct: Math.round(100 * t / total), segs: steps.map(function (s) { return { flex: s.dur, fill: Math.max(0, Math.min(100, 100 * (t - s.st0) / s.dur)) }; }), steps: steps, found: ['Java', 'MySQL', 'Git', 'REST API', 'Spring Boot'].map(function (n, i) { return { name: '✓ ' + n, d: (i * 0.08).toFixed(2) }; }), finished: fin, running: !fin, replay: function () { self.start(); } }; } }

### CSS (không font-face)

```css
/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

body{margin:0;background:#070B10}
a{color:#C5F36A}a:hover{color:#E4FFB5}
.root{font-family:'Be Vietnam Pro',system-ui,sans-serif;color:#E6EDF3;background-color:#070B10;background-image:linear-gradient(rgba(98,217,238,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(98,217,238,.04) 1px,transparent 1px);background-size:40px 40px;min-height:100vh;display:flex;flex-direction:column}
.mono{font-family:'JetBrains Mono',ui-monospace,Menlo,monospace}
.k{font:600 11px/1.4 'JetBrains Mono',ui-monospace,monospace;color:#9FB0C2;letter-spacing:.08em;text-transform:uppercase}
.wrap{width:100%;max-width:1280px;margin:0 auto;padding:0 24px;box-sizing:border-box}
.hdr{border-bottom:1px solid #1C2A36;background:#0A1017}
.logo{display:inline-flex;align-items:center;gap:10px;text-decoration:none;color:#E6EDF3;font-weight:700;font-size:16px;letter-spacing:.04em;min-height:44px}
.logo:hover{color:#E6EDF3}
.nav{display:flex;gap:2px;flex:1 1 auto;min-width:0;overflow-x:auto}
.nav a{display:inline-flex;align-items:center;min-height:52px;padding:0 14px;color:#9FB0C2;text-decoration:none;font-weight:500;font-size:14px;border-bottom:2px solid transparent;white-space:nowrap}
.nav a:hover{color:#E6EDF3}
.nav a.on{color:#E6EDF3;border-bottom-color:#62D9EE}
.prof{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 14px;border-radius:999px;border:1px solid #243543;color:#C4D0DC;font-size:12px;text-decoration:none;white-space:nowrap;box-sizing:border-box}
.panel{border:1px solid #1C2A36;background:#0D141C;border-radius:12px;padding:20px;box-sizing:border-box}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:48px;padding:0 22px;border-radius:8px;border:0;background:#C5F36A;color:#0A0F05;font:600 15px 'Be Vietnam Pro',sans-serif;text-decoration:none;cursor:pointer}
.btn:hover{color:#0A0F05;background:#D6FA94}
.ghost{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:44px;padding:0 16px;border-radius:8px;border:1px solid #2E4456;background:transparent;color:#C4D0DC;font:500 14px 'Be Vietnam Pro',sans-serif;text-decoration:none;cursor:pointer}
.ghost:hover{border-color:#62D9EE;color:#E6EDF3}
.foot{border-top:1px solid #1C2A36;margin-top:auto}
a:focus-visible,button:focus-visible{outline:2px solid #C5F36A;outline-offset:2px}
@keyframes spin{to{transform:rotate(360deg)}}
.spin{animation:spin .9s linear infinite}
@keyframes chipin{from{opacity:0;transform:scale(.85)}to{opacity:1;transform:none}}
.chipin{animation:chipin .35s cubic-bezier(.2,.7,.2,1) both}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
```

### Script (rút)

```js

```

## 06
- html: `.working/screens-inner/06.html` (26913 bytes)

### Chữ trên màn

- Khoảng trống kỹ năng
- HẢI ĐỒ
- ·
- IT
- Bản đồ
- Insights
- Cố vấn
- Soi tin
- Hồ sơ tạm · chưa lưu
- CV_Minh_JavaBackend.pdf · so với Backend · Intern–Junior · n = 52 · 02/11/2026
- Khoảng trống kỹ năng
- Máy có thể đọc sót. Xác nhận từng khoảng trống — lộ trình sẽ xếp lại theo câu trả lời của bạn.
- {{done}}
- /{{total}}
- đã xác nhận
- Đã có trong CV · 5
- {{h.name}}
- {{h.tier}}
- {{h.p}}%
- · {{h.k}}/52
- Tô xanh vì hệ thống tìm thấy trong CV của bạn.
- {{g.name}}
- {{g.badge}}
- {{g.hint}}
- {{g.p}}%
- {{g.k}}/52 tin · 02/11/2026
- Tôi chưa biết
- Tôi đã biết, chỉ là CV chưa ghi
- CV của tôi có ghi rồi (hệ thống đọc sót)
- {{g.result}}
- Lộ trình đã xếp lại theo chặng
- Backend · Intern–Junior · n = 52 · 02/11/2026
- {{s.title}}
- {{i.name}}
- {{i.p}}% · {{i.k}}/52
- Không còn khoảng trống cốt lõi hay thường gặp trong nhóm so sánh này.
- Đã biết, cần ghi vào CV
- {{cvList}}
- Hệ thống đọc sót · đã ghi nhận
- {{missList}}
- Lưu hồ sơ và tải bản tóm tắt
- Lưu hồ sơ và tải bản tóm tắt
- Còn {{left}} khoảng trống chưa xác nhận.
- ← Về lộ trình chung
- Cốt lõi ≥ 60% · Thường gặp 30–59% · Riêng của công ty &lt; 30% số tin trong nhóm so sánh
- Chính sách dữ liệu
- class Component extends DCLogic { constructor(props) { super(props); this.state = { ans: {}, touched: false }; } renderVals() { var self = this, st = this.state; var PRESET = { SQL: 'cv', PostgreSQL: 'cv', Docker: 'cv', Microservices: 'cv', 'CI/CD': 'chua', Redis: 'chua' }; var ans = st.touched ? st.ans : ((this.props.preset ?? 'chưa xác nhận') === 'đã xác nhận' ? PRESET : st.ans); var G = [ { name: 'SQL', k: 42, core: true, hint: 'CV có ghi MySQL nhưng không thấy chữ “SQL”. Hãy kiểm tra lại.' }, { name: 'PostgreSQL', k: 20, core: false, hint: 'Hay đi cùng SQL trong các tin cần cơ sở dữ liệu quan hệ.' }, { name: 'Docker', k: 18, core: false, hint: 'Hay xuất hiện ở phần triển khai và môi trường chạy dịch vụ.' }, { name: 'Microservices', k: 16, core: false, hint: 'Hay đi cùng Spring Boot và Docker.' }, { name: 'CI/CD', k: 17, core: false, hint: 'Hay đi cùng Docker ở phần quy trình đưa code lên môi trường thật.' }, { name: 'Redis', k: 16, core: false, hint: 'Hay xuất hiện ở phần bộ nhớ đệm (cache) và tối ưu hiệu năng.' } ]; var HAVE = [['Java', 36], ['Git', 33], ['REST API', 31], ['Spring Boot', 27], ['MySQL', 23]]; var pct = function (k) { return Math.round(100 * k / 52); }; var set = function (name, v) { return function () { var a = Object.assign({}, ans); a[name] = v; self.setState({ ans: a, touched: true }); }; }; var RES = { chua: '→ Đưa vào lộ trình', cv: '→ Thêm vào danh sách “cần ghi vào CV”', sot: '→ Tính là đã có · đã ghi nhận để sửa bộ đọc' }; var done = G.filter(function (g) { return !!ans[g.name]; }).length; var known = function (n) { return ans[n] === 'cv' || ans[n] === 'sot'; }; var stageOf = { SQL: 1, PostgreSQL: known('SQL') ? 1 : 2, Docker: 2, Microservices: ans.Docker === 'chua' ? 3 : 2, 'CI/CD': ans.Docker === 'chua' ? 3 : 2, Redis: 4 }; var N = G.length; var learn = G.filter(function (g) { return ans[g.name] === 'chua'; }); var nums = []; learn.forEach(function (g) { if (nums.indexOf(stageOf[g.name])
- = 60 ? 'CỐT LÕI' : 'THƯỜNG GẶP' }; }), gaps: G.map(function (g) { var a = ans[g.name] || ''; return { name: g.name, k: g.k, p: pct(g.k), hint: g.hint, badge: g.core ? 'KHOẢNG TRỐNG CỐT LÕI' : 'KHOẢNG TRỐNG THƯỜNG GẶP', badgeColor: g.core ? '#F5A65B' : '#9FB0C2', border: a ? '#2E5A6A' : (g.core ? '#5A4426' : '#1C2A36'), aria: 'Xác nhận kỹ năng ' + g.name, on1: a === 'chua', on2: a === 'cv', on3: a === 'sot', c1: a === 'chua' ? 'ans on' : 'ans', c2: a === 'cv' ? 'ans on' : 'ans', c3: a === 'sot' ? 'miss on' : 'miss', a1: set(g.name, 'chua'), a2: set(g.name, 'cv'), a3: set(g.name, 'sot'), answered: !!a, result: RES[a] || '' }; }), stages: stages, noStages: stages.length === 0, cvList: list('cv'), missList: list('sot') }; } }

### CSS (không font-face)

```css
/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

body{margin:0;background:#070B10}
a{color:#C5F36A}a:hover{color:#E4FFB5}
.root{font-family:'Be Vietnam Pro',system-ui,sans-serif;color:#E6EDF3;background-color:#070B10;background-image:linear-gradient(rgba(98,217,238,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(98,217,238,.04) 1px,transparent 1px);background-size:40px 40px;min-height:100vh;display:flex;flex-direction:column}
.mono{font-family:'JetBrains Mono',ui-monospace,Menlo,monospace}
.k{font:600 11px/1.4 'JetBrains Mono',ui-monospace,monospace;color:#9FB0C2;letter-spacing:.08em;text-transform:uppercase}
.wrap{width:100%;max-width:1280px;margin:0 auto;padding:0 24px;box-sizing:border-box}
.hdr{border-bottom:1px solid #1C2A36;background:#0A1017}
.logo{display:inline-flex;align-items:center;gap:10px;text-decoration:none;color:#E6EDF3;font-weight:700;font-size:16px;letter-spacing:.04em;min-height:44px}
.logo:hover{color:#E6EDF3}
.nav{display:flex;gap:2px;flex:1 1 auto;min-width:0;overflow-x:auto}
.nav a{display:inline-flex;align-items:center;min-height:52px;padding:0 14px;color:#9FB0C2;text-decoration:none;font-weight:500;font-size:14px;border-bottom:2px solid transparent;white-space:nowrap}
.nav a:hover{color:#E6EDF3}
.nav a.on{color:#E6EDF3;border-bottom-color:#62D9EE}
.prof{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 14px;border-radius:999px;border:1px solid #243543;color:#C4D0DC;font-size:12px;text-decoration:none;white-space:nowrap;box-sizing:border-box}
.prof:hover{border-color:#62D9EE;color:#E6EDF3}
.panel{border:1px solid #1C2A36;background:#0D141C;border-radius:12px;padding:20px;box-sizing:border-box}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:48px;padding:0 22px;border-radius:8px;border:0;background:#C5F36A;color:#0A0F05;font:600 15px 'Be Vietnam Pro',sans-serif;text-decoration:none;cursor:pointer}
.btn:hover{color:#0A0F05;background:#D6FA94}
.btn:disabled{background:#2A3A44;color:#8496A6;cursor:not-allowed}
.ans{min-height:44px;padding:0 14px;border-radius:8px;border:1px solid #2E4456;background:#0A1118;color:#C4D0DC;font:500 14px 'Be Vietnam Pro',sans-serif;cursor:pointer;text-align:left}
.ans:hover{border-color:#62D9EE;color:#E6EDF3}
.ans.on{border-color:#62D9EE;background:rgba(98,217,238,.14);color:#E6EDF3;box-shadow:inset 0 0 0 1px #62D9EE}
.miss{min-height:44px;padding:0 4px;border:0;background:transparent;color:#9FB0C2;font:500 13px 'Be Vietnam Pro',sans-serif;text-decoration:underline;text-underline-offset:3px;cursor:pointer}
.miss:hover{color:#E6EDF3}
.miss.on{color:#62D9EE;font-weight:600}
.foot{border-top:1px solid #1C2A36;margin-top:auto}
a:focus-visible,button:focus-visible{outline:2px solid #C5F36A;outline-offset:2px}
@keyframes pop{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
.pop{animation:pop .55s cubic-bezier(.2,.7,.2,1) both}
@keyframes flash{0%{box-shadow:0 0 0 0 rgba(98,217,238,.5)}100%{box-shadow:0 0 0 12px rgba(98,217,238,0)}}
.flash{animation:flash 1s ease-out 1}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
```

### Script (rút)

```js

```

## 07
- html: `.working/screens-inner/07.html` (21071 bytes)

### Chữ trên màn

- Kỹ năng Docker — vì sao thị trường cần
- HẢI ĐỒ
- ·
- IT
- Bản đồ
- Insights
- Cố vấn
- Soi tin
- Hồ sơ tạm · chưa lưu
- Cố vấn
- ›
- Khoảng trống kỹ năng
- ›
- Docker
- Docker
- KHOẢNG TRỐNG THƯỜNG GẶP
- Vì sao thị trường cần
- Docker đóng gói một ứng dụng cùng môi trường chạy của nó. Nhờ vậy đội backend chạy cùng một dịch vụ giống hệt nhau trên máy lập trình, máy kiểm thử và máy chủ. Trong tin tuyển dụng backend, Docker thường được nhắc ở phần triển khai, cùng với microservices và quy trình đưa code lên môi trường thật.
- Với người mới, Docker là cách nhanh để chạy được cơ sở dữ liệu và dịch vụ phụ trợ trên máy mình mà không cần cài từng thứ.
- Số liệu · tách khỏi lời dẫn
- 35%
- 18/52 tin
- tin Backend · Intern–Junior có nhắc Docker
- Snapshot 02/11/2026 · [Nguồn 1], [Nguồn 2]
- Hay đi cùng Docker
- Chưa đủ dữ liệu (n = 18 tin có Docker, cần 30)
- Khi đủ 30 tin, Hải Đồ sẽ hiện tỷ lệ đi cùng.
- Tài liệu miễn phí đã kiểm duyệt
- Hải Đồ không nhận tiền giới thiệu từ nguồn nào
- TÀI LIỆU CHÍNH THỨC · TIẾNG ANH
- ↗
- Docker Docs — Get started
- Đi từ chạy container đầu tiên tới viết Dockerfile và Compose cho một ứng dụng nhỏ.
- Kiểm duyệt: [người kiểm duyệt] · [ngày]
- THỰC HÀNH TRÊN TRÌNH DUYỆT · TIẾNG ANH
- ↗
- Play with Docker
- Gõ lệnh Docker ngay trên trình duyệt, không cần cài gì lên máy.
- Kiểm duyệt: [người kiểm duyệt] · [ngày]
- TIẾNG VIỆT
- [Tài liệu tiếng Việt đã kiểm duyệt]
- Chỗ dành cho một nguồn tiếng Việt sau khi qua kiểm duyệt.
- ← Quay lại khoảng trống kỹ năng
- Lời dẫn do người viết, không chứa số liệu. Số liệu nằm ở khung bên phải.
- Chính sách dữ liệu
- class Component extends DCLogic { renderVals() { return {}; } }

### CSS (không font-face)

```css
/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

body{margin:0;background:#070B10}
a{color:#C5F36A}a:hover{color:#E4FFB5}
.root{font-family:'Be Vietnam Pro',system-ui,sans-serif;color:#E6EDF3;background-color:#070B10;background-image:linear-gradient(rgba(98,217,238,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(98,217,238,.04) 1px,transparent 1px);background-size:40px 40px;min-height:100vh;display:flex;flex-direction:column}
.mono{font-family:'JetBrains Mono',ui-monospace,Menlo,monospace}
.k{font:600 11px/1.4 'JetBrains Mono',ui-monospace,monospace;color:#9FB0C2;letter-spacing:.08em;text-transform:uppercase}
.wrap{width:100%;max-width:1280px;margin:0 auto;padding:0 24px;box-sizing:border-box}
.hdr{border-bottom:1px solid #1C2A36;background:#0A1017}
.logo{display:inline-flex;align-items:center;gap:10px;text-decoration:none;color:#E6EDF3;font-weight:700;font-size:16px;letter-spacing:.04em;min-height:44px}
.logo:hover{color:#E6EDF3}
.nav{display:flex;gap:2px;flex:1 1 auto;min-width:0;overflow-x:auto}
.nav a{display:inline-flex;align-items:center;min-height:52px;padding:0 14px;color:#9FB0C2;text-decoration:none;font-weight:500;font-size:14px;border-bottom:2px solid transparent;white-space:nowrap}
.nav a:hover{color:#E6EDF3}
.nav a.on{color:#E6EDF3;border-bottom-color:#62D9EE}
.prof{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 14px;border-radius:999px;border:1px solid #243543;color:#C4D0DC;font-size:12px;text-decoration:none;white-space:nowrap;box-sizing:border-box}
.prof:hover{border-color:#62D9EE;color:#E6EDF3}
.panel{border:1px solid #1C2A36;background:#0D141C;border-radius:12px;padding:20px;box-sizing:border-box}
.ghost{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:44px;padding:0 16px;border-radius:8px;border:1px solid #2E4456;background:transparent;color:#C4D0DC;font:500 14px 'Be Vietnam Pro',sans-serif;text-decoration:none;cursor:pointer}
.ghost:hover{border-color:#62D9EE;color:#E6EDF3}
.res{display:flex;flex-direction:column;gap:10px;padding:18px;border-radius:12px;border:1px solid #2E4456;background:#0A1118;text-decoration:none;color:#E6EDF3;transition:border-color .2s,transform .2s}
.res:hover{border-color:#62D9EE;color:#E6EDF3;transform:translateY(-2px)}
.foot{border-top:1px solid #1C2A36;margin-top:auto}
a:focus-visible,button:focus-visible{outline:2px solid #C5F36A;outline-offset:2px}
@keyframes rise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
.rise{animation:rise .6s cubic-bezier(.2,.7,.2,1) both}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
```

### Script (rút)

```js

```

## 08
- html: `.working/screens-inner/08.html` (23964 bytes)

### Chữ trên màn

- Lưu hồ sơ và tải bản tóm tắt
- HẢI ĐỒ
- ·
- IT
- Bản đồ
- Insights
- Cố vấn
- Soi tin
- Hồ sơ: Java Backend · trong trình duyệt
- Hồ sơ đã lưu trong trình duyệt này
- Không có tài khoản. Hồ sơ không được gửi về máy chủ — xoá dữ liệu trình duyệt hoặc bấm “Xoá hồ sơ” là mất.
- Những gì được lưu
- Vai trò
- Java Backend
- Nhóm so sánh
- Backend · Intern–Junior
- (n = 52)
- CV đã ghi
- Java, Git, REST API, Spring Boot, MySQL
- Cần ghi vào CV
- SQL, PostgreSQL, Docker, Microservices
- Cần học
- CI/CD, Redis
- Lưu lúc
- Chủ nhật 02/11/2026 · 22:41
- Không lưu
- File CV và văn bản trích từ CV. Chúng đã bị bỏ sau khi đọc.
- Xoá hồ sơ khỏi trình duyệt
- Bản tóm tắt · xem trước
- Java Backend · Intern–Junior
- Snapshot 02/11/2026 · n = 52
- 1 ·
- Kỹ năng đã có nhưng cần ghi vào CV
- SQL
- 81% · 42/52 tin
- Bạn xác nhận đã biết. CV hiện chỉ ghi MySQL, chưa ghi rõ “SQL”.
- PostgreSQL
- 38% · 20/52 tin
- Bạn xác nhận đã biết. CV chưa ghi.
- Docker
- 35% · 18/52 tin
- Bạn xác nhận đã biết. CV chưa ghi.
- Microservices
- 31% · 16/52 tin
- Bạn xác nhận đã biết. CV chưa ghi.
- 2 ·
- Lộ trình theo chặng
- Chặng 1
- CI/CD
- 33% · 17/52 tin
- GitHub Actions — tài liệu chính thức ↗
- Chặng 2
- Redis
- 31% · 16/52 tin
- Redis Docs — Get started ↗
- Nguồn đang bật: [Nguồn 1], [Nguồn 2] · Tỷ lệ = số tin có nhắc kỹ năng / 52 tin Backend · Intern–Junior. Bản tóm tắt không phải lời khuyên nộp hồ sơ.
- Tải bản tóm tắt (PDF)
- Tải dạng văn bản (.md)
- Sáng mai: soi một tin tuyển dụng với hồ sơ này →
- Hồ sơ chỉ nằm trong trình duyệt này.
- Chính sách dữ liệu
- {{toast}}
- class Component extends DCLogic { constructor(props) { super(props); this.state = { toast: '' }; this.tt = null; } componentWillUnmount() { if (this.tt) clearTimeout(this.tt); } say(t) { var self = this; if (this.tt) clearTimeout(this.tt); this.setState({ toast: t }); this.tt = setTimeout(function () { self.setState({ toast: '' }); }, 2400); } renderVals() { var self = this; return { toast: this.state.toast, toastOn: !!this.state.toast, dlPdf: function () { self.say('Đã tạo HaiDo_TomTat_JavaBackend_02-11-2026.pdf'); }, dlMd: function () { self.say('Đã tạo HaiDo_TomTat_JavaBackend_02-11-2026.md'); }, clear: function () { self.say('Prototype: hồ sơ sẽ bị xoá khỏi trình duyệt sau khi bạn xác nhận.'); } }; } }

### CSS (không font-face)

```css
/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

body{margin:0;background:#070B10}
a{color:#C5F36A}a:hover{color:#E4FFB5}
.root{font-family:'Be Vietnam Pro',system-ui,sans-serif;color:#E6EDF3;background-color:#070B10;background-image:linear-gradient(rgba(98,217,238,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(98,217,238,.04) 1px,transparent 1px);background-size:40px 40px;min-height:100vh;display:flex;flex-direction:column}
.mono{font-family:'JetBrains Mono',ui-monospace,Menlo,monospace}
.k{font:600 11px/1.4 'JetBrains Mono',ui-monospace,monospace;color:#9FB0C2;letter-spacing:.08em;text-transform:uppercase}
.wrap{width:100%;max-width:1280px;margin:0 auto;padding:0 24px;box-sizing:border-box}
.hdr{border-bottom:1px solid #1C2A36;background:#0A1017}
.logo{display:inline-flex;align-items:center;gap:10px;text-decoration:none;color:#E6EDF3;font-weight:700;font-size:16px;letter-spacing:.04em;min-height:44px}
.logo:hover{color:#E6EDF3}
.nav{display:flex;gap:2px;flex:1 1 auto;min-width:0;overflow-x:auto}
.nav a{display:inline-flex;align-items:center;min-height:52px;padding:0 14px;color:#9FB0C2;text-decoration:none;font-weight:500;font-size:14px;border-bottom:2px solid transparent;white-space:nowrap}
.nav a:hover{color:#E6EDF3}
.nav a.on{color:#E6EDF3;border-bottom-color:#62D9EE}
.prof{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 14px;border-radius:999px;border:1px solid #243543;color:#C4D0DC;font-size:12px;text-decoration:none;white-space:nowrap;box-sizing:border-box}
.prof:hover{border-color:#62D9EE;color:#E6EDF3}
.panel{border:1px solid #1C2A36;background:#0D141C;border-radius:12px;padding:20px;box-sizing:border-box}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:48px;padding:0 20px;border-radius:8px;border:0;background:#C5F36A;color:#0A0F05;font:600 15px 'Be Vietnam Pro',sans-serif;text-decoration:none;cursor:pointer}
.btn:hover{color:#0A0F05;background:#D6FA94}
.ghost{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:44px;padding:0 16px;border-radius:8px;border:1px solid #2E4456;background:transparent;color:#C4D0DC;font:500 14px 'Be Vietnam Pro',sans-serif;text-decoration:none;cursor:pointer}
.ghost:hover{border-color:#62D9EE;color:#E6EDF3}
.danger{border-color:#5A3E22;color:#FFD3A6}
.danger:hover{border-color:#F5A65B;color:#FFE6CC}
.foot{border-top:1px solid #1C2A36;margin-top:auto}
.toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);z-index:50;padding:12px 18px;border-radius:10px;background:#E6EDF3;color:#0A0F05;font:600 14px 'Be Vietnam Pro',sans-serif;box-shadow:0 12px 40px rgba(0,0,0,.5)}
a:focus-visible,button:focus-visible{outline:2px solid #C5F36A;outline-offset:2px}
@keyframes rise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
.rise{animation:rise .6s cubic-bezier(.2,.7,.2,1) both}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
```

### Script (rút)

```js

```

## 09
- html: `.working/screens-inner/09.html` (19651 bytes)

### Chữ trên màn

- CV là ảnh scan — không đọc được chữ
- HẢI ĐỒ
- ·
- IT
- Bản đồ
- Insights
- Cố vấn
- Soi tin
- Chưa có hồ sơ
- CV_Minh_scan.pdf
- 2,1 MB · PDF
- Không đọc được chữ trong file này
- Chỉ đọc được
- 12 ký tự
- , cần ít nhất 30. File có vẻ là ảnh chụp hoặc bản scan nên không có lớp chữ.
- Phát hiện sau 0,4 giây · chưa có gì được gửi ra ngoài
- Chọn một trong ba cách để tiếp tục
- CÁCH 1
- Xuất lại PDF từ Word, Canva hoặc Overleaf
- Dùng “Lưu thành PDF” hoặc “Tải xuống PDF” ngay trong công cụ bạn đã soạn CV. File xuất trực tiếp sẽ có lớp chữ.
- Tải lên file khác
- CÁCH 2
- Dùng file DOCX
- Nếu CV soạn bằng Word hoặc Google Docs, tải bản .docx lên là đủ.
- Tải lên file DOCX
- CÁCH 3
- Tự chọn kỹ năng trên màn
- Bấm vào những kỹ năng bạn đã có. Không cần file, không gửi gì ra ngoài.
- Tự chọn kỹ năng
- Hải Đồ không đoán chữ từ ảnh, để tránh đọc nhầm kỹ năng của bạn.
- Ngưỡng tối thiểu: 30 ký tự đọc được từ CV.
- Chính sách dữ liệu
- class Component extends DCLogic { renderVals() { return {}; } }

### CSS (không font-face)

```css
/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

body{margin:0;background:#070B10}
a{color:#C5F36A}a:hover{color:#E4FFB5}
.root{font-family:'Be Vietnam Pro',system-ui,sans-serif;color:#E6EDF3;background-color:#070B10;background-image:linear-gradient(rgba(98,217,238,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(98,217,238,.04) 1px,transparent 1px);background-size:40px 40px;min-height:100vh;display:flex;flex-direction:column}
.mono{font-family:'JetBrains Mono',ui-monospace,Menlo,monospace}
.k{font:600 11px/1.4 'JetBrains Mono',ui-monospace,monospace;color:#9FB0C2;letter-spacing:.08em;text-transform:uppercase}
.wrap{width:100%;max-width:1280px;margin:0 auto;padding:0 24px;box-sizing:border-box}
.hdr{border-bottom:1px solid #1C2A36;background:#0A1017}
.logo{display:inline-flex;align-items:center;gap:10px;text-decoration:none;color:#E6EDF3;font-weight:700;font-size:16px;letter-spacing:.04em;min-height:44px}
.logo:hover{color:#E6EDF3}
.nav{display:flex;gap:2px;flex:1 1 auto;min-width:0;overflow-x:auto}
.nav a{display:inline-flex;align-items:center;min-height:52px;padding:0 14px;color:#9FB0C2;text-decoration:none;font-weight:500;font-size:14px;border-bottom:2px solid transparent;white-space:nowrap}
.nav a:hover{color:#E6EDF3}
.nav a.on{color:#E6EDF3;border-bottom-color:#62D9EE}
.prof{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 14px;border-radius:999px;border:1px solid #243543;color:#C4D0DC;font-size:12px;text-decoration:none;white-space:nowrap;box-sizing:border-box}
.prof:hover{border-color:#62D9EE;color:#E6EDF3}
.panel{border:1px solid #1C2A36;background:#0D141C;border-radius:12px;padding:20px;box-sizing:border-box}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:44px;padding:0 18px;border-radius:8px;border:0;background:#C5F36A;color:#0A0F05;font:600 14px 'Be Vietnam Pro',sans-serif;text-decoration:none;cursor:pointer}
.btn:hover{color:#0A0F05;background:#D6FA94}
.ghost{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:44px;padding:0 16px;border-radius:8px;border:1px solid #2E4456;background:transparent;color:#C4D0DC;font:500 14px 'Be Vietnam Pro',sans-serif;text-decoration:none;cursor:pointer}
.ghost:hover{border-color:#62D9EE;color:#E6EDF3}
.opt{display:flex;flex-direction:column;gap:12px;padding:20px;border-radius:12px;border:1px solid #2E4456;background:#0D141C}
.foot{border-top:1px solid #1C2A36;margin-top:auto}
a:focus-visible,button:focus-visible{outline:2px solid #C5F36A;outline-offset:2px}
@keyframes shake{0%,100%{transform:none}25%{transform:translateX(-4px)}75%{transform:translateX(4px)}}
.shake{animation:shake .3s ease-in-out 2}
@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.rise{animation:rise .5s cubic-bezier(.2,.7,.2,1) both}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
```

### Script (rút)

```js

```

## 10
- html: `.working/screens-inner/10.html` (20213 bytes)

### Chữ trên màn

- Soi tin — dán nội dung tin
- HẢI ĐỒ
- ·
- IT
- Bản đồ
- Insights
- Cố vấn
- Soi tin
- Hồ sơ: Java Backend · trong trình duyệt
- Hồ sơ từ tối qua vẫn ở đây:
- Java Backend
- · 9 kỹ năng đã có · 2 kỹ năng đang học · lưu Chủ nhật 02/11 22:41.
- Xem hồ sơ
- Soi tin tuyển dụng
- Dán nội dung một tin. Hải Đồ tách kỹ năng và đối chiếu với nhóm tin cùng vai trò, cùng cấp bậc.
- Nội dung tin tuyển dụng
- {{count}} ký tự
- Soi tin
- Soi tin
- Xoá nội dung
- Nội dung tin không được lưu lại.
- Hải Đồ sẽ
- Tách danh sách kỹ năng trong tin.
- So với nhóm tin cùng vai trò và cấp bậc, kèm n và ngày snapshot.
- Nêu vài điểm nên tự kiểm tra trước khi nộp.
- Hải Đồ không
- Khuyên bạn nộp hay không nộp.
- Kết luận một tin là thật hay giả.
- Lưu nội dung tin bạn dán.
- Snapshot 02/11/2026 · [Nguồn 1], [Nguồn 2]
- Chính sách dữ liệu
- class Component extends DCLogic { constructor(props) { super(props); this.state = { text: '[Công ty A] tuyển Java Backend Developer (Fresher/Junior)\n\nYêu cầu:\n- Thành thạo Java, Spring Boot\n- Nắm vững SQL, đã làm việc với MySQL\n- Thiết kế và xây dựng REST API\n- Sử dụng Git trong làm việc nhóm\n- Ưu tiên ứng viên biết Kafka, Redis\n\nĐịa điểm: Hà Nội\nLiên hệ: tuyendung.congtya@gmail.com' }; } renderVals() { var self = this, t = this.state.text || ''; return { text: t, count: t.length.toLocaleString('vi-VN'), hasText: t.trim().length > 0, noText: t.trim().length === 0, onText: function (e) { self.setState({ text: e.target.value }); }, clear: function () { self.setState({ text: '' }); } }; } }

### CSS (không font-face)

```css
/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

body{margin:0;background:#070B10}
a{color:#C5F36A}a:hover{color:#E4FFB5}
.root{font-family:'Be Vietnam Pro',system-ui,sans-serif;color:#E6EDF3;background-color:#070B10;background-image:linear-gradient(rgba(98,217,238,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(98,217,238,.04) 1px,transparent 1px);background-size:40px 40px;min-height:100vh;display:flex;flex-direction:column}
.mono{font-family:'JetBrains Mono',ui-monospace,Menlo,monospace}
.k{font:600 11px/1.4 'JetBrains Mono',ui-monospace,monospace;color:#9FB0C2;letter-spacing:.08em;text-transform:uppercase}
.wrap{width:100%;max-width:1280px;margin:0 auto;padding:0 24px;box-sizing:border-box}
.hdr{border-bottom:1px solid #1C2A36;background:#0A1017}
.logo{display:inline-flex;align-items:center;gap:10px;text-decoration:none;color:#E6EDF3;font-weight:700;font-size:16px;letter-spacing:.04em;min-height:44px}
.logo:hover{color:#E6EDF3}
.nav{display:flex;gap:2px;flex:1 1 auto;min-width:0;overflow-x:auto}
.nav a{display:inline-flex;align-items:center;min-height:52px;padding:0 14px;color:#9FB0C2;text-decoration:none;font-weight:500;font-size:14px;border-bottom:2px solid transparent;white-space:nowrap}
.nav a:hover{color:#E6EDF3}
.nav a.on{color:#E6EDF3;border-bottom-color:#62D9EE}
.prof{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 14px;border-radius:999px;border:1px solid #243543;color:#C4D0DC;font-size:12px;text-decoration:none;white-space:nowrap;box-sizing:border-box}
.prof:hover{border-color:#62D9EE;color:#E6EDF3}
.panel{border:1px solid #1C2A36;background:#0D141C;border-radius:12px;padding:20px;box-sizing:border-box}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:48px;padding:0 24px;border-radius:8px;border:0;background:#C5F36A;color:#0A0F05;font:600 15px 'Be Vietnam Pro',sans-serif;text-decoration:none;cursor:pointer}
.btn:hover{color:#0A0F05;background:#D6FA94}
.btn:disabled{background:#2A3A44;color:#8496A6;cursor:not-allowed}
.ghost{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:44px;padding:0 16px;border-radius:8px;border:1px solid #2E4456;background:transparent;color:#C4D0DC;font:500 14px 'Be Vietnam Pro',sans-serif;text-decoration:none;cursor:pointer}
.ghost:hover{border-color:#62D9EE;color:#E6EDF3}
.ta{width:100%;min-height:340px;box-sizing:border-box;padding:16px;border-radius:10px;border:1px solid #2E4456;background:#05080C;color:#E6EDF3;font:400 14px/1.7 'JetBrains Mono',monospace;resize:vertical}
.ta::placeholder{color:#7D8FA1}
.foot{border-top:1px solid #1C2A36;margin-top:auto}
a:focus-visible,button:focus-visible,textarea:focus-visible{outline:2px solid #C5F36A;outline-offset:2px}
@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.rise{animation:rise .5s cubic-bezier(.2,.7,.2,1) both}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
```

### Script (rút)

```js

```

## 11
- html: `.working/screens-inner/11.html` (26111 bytes)

### Chữ trên màn

- Soi tin — kết quả
- HẢI ĐỒ
- ·
- IT
- Bản đồ
- Insights
- Cố vấn
- Soi tin
- Hồ sơ: Java Backend · trong trình duyệt
- Đang đối chiếu với:
- Java Backend · Fresher/Junior
- Backend · Intern–Junior
- Data Engineer · Fresher/Junior
- {{d.note}}
- Đổi nhóm không cần dán lại tin.
- Tin đã dán · [Công ty A] · Java Backend Developer (Fresher/Junior) · Hà Nội
- So sánh với snapshot 02/11/2026 · [Nguồn 1], [Nguồn 2] · nội dung tin không được lưu
- {{d.match}}%
- Mức khớp với hồ sơ của bạn
- {{d.sub}}
- Trọng số: cốt lõi 3 · thường gặp 2 · riêng của công ty 1. Bậc kỹ năng tính trên nhóm n = {{d.n}}.
- Số kỹ năng yêu cầu
- 8 kỹ năng
- — nhiều hơn
- {{d.pctl}}%
- tin trong nhóm
- (n = {{d.n}})
- Lương của nhóm
- Chưa đủ dữ liệu
- ({{d.sal}}/30 tin có lương)
- Thông tin
- Tin không công bố khoảng lương.
- 8 kỹ năng trong tin, xếp theo nhóm so sánh
- ✓ có trong hồ sơ · ○ chưa có
- {{t.title}}
- {{t.score}}
- {{i.mark}}
- {{i.name}}
- {{i.note}}
- {{i.p}}% · {{i.k}}/{{d.n}}
- Việc nên tự kiểm tra
- Đây là việc cần kiểm tra, không phải kết luận tin giả.
- D1
- Email liên hệ là địa chỉ cá nhân
- Địa chỉ dùng gmail.com, không theo tên miền của công ty. Nên đối chiếu với trang tuyển dụng chính thức của [Công ty A].
- D2
- Tin xuất hiện lại nhiều lần
- Nội dung gần giống được đăng 3 lần trong 45 ngày trên các nguồn đang bật. Nên hỏi nhà tuyển dụng vị trí còn tuyển hay không.
- ← Soi tin khác
- Xem lộ trình của tôi
- Hải Đồ IT không khuyên nộp hay không nộp.
- Cốt lõi ≥ 60% · Thường gặp 30–59% · Riêng của công ty &lt; 30% số tin trong nhóm so sánh
- Chính sách dữ liệu
- class Component extends DCLogic { constructor(props) { super(props); this.state = { g: 'jb' }; } renderVals() { var self = this; var HAVE = { 'Java': 1, 'Git': 1, 'REST API': 1, 'Spring Boot': 1, 'MySQL': 1, 'SQL': 2, 'PostgreSQL': 2, 'Docker': 2, 'Microservices': 2 }; var D = { jb: { n: 39, sal: 10, pctl: 76, note: 'Cấp bậc lấy từ tin. Nhánh Java Backend · Fresher/Junior có 24 tin (

### CSS (không font-face)

```css
/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

body{margin:0;background:#070B10}
a{color:#C5F36A}a:hover{color:#E4FFB5}
.root{font-family:'Be Vietnam Pro',system-ui,sans-serif;color:#E6EDF3;background-color:#070B10;background-image:linear-gradient(rgba(98,217,238,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(98,217,238,.04) 1px,transparent 1px);background-size:40px 40px;min-height:100vh;display:flex;flex-direction:column}
.mono{font-family:'JetBrains Mono',ui-monospace,Menlo,monospace}
.k{font:600 11px/1.4 'JetBrains Mono',ui-monospace,monospace;color:#9FB0C2;letter-spacing:.08em;text-transform:uppercase}
.wrap{width:100%;max-width:1280px;margin:0 auto;padding:0 24px;box-sizing:border-box}
.hdr{border-bottom:1px solid #1C2A36;background:#0A1017}
.logo{display:inline-flex;align-items:center;gap:10px;text-decoration:none;color:#E6EDF3;font-weight:700;font-size:16px;letter-spacing:.04em;min-height:44px}
.logo:hover{color:#E6EDF3}
.nav{display:flex;gap:2px;flex:1 1 auto;min-width:0;overflow-x:auto}
.nav a{display:inline-flex;align-items:center;min-height:52px;padding:0 14px;color:#9FB0C2;text-decoration:none;font-weight:500;font-size:14px;border-bottom:2px solid transparent;white-space:nowrap}
.nav a:hover{color:#E6EDF3}
.nav a.on{color:#E6EDF3;border-bottom-color:#62D9EE}
.prof{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 14px;border-radius:999px;border:1px solid #243543;color:#C4D0DC;font-size:12px;text-decoration:none;white-space:nowrap;box-sizing:border-box}
.prof:hover{border-color:#62D9EE;color:#E6EDF3}
.panel{border:1px solid #1C2A36;background:#0D141C;border-radius:12px;padding:20px;box-sizing:border-box}
.ghost{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:44px;padding:0 16px;border-radius:8px;border:1px solid #2E4456;background:transparent;color:#C4D0DC;font:500 14px 'Be Vietnam Pro',sans-serif;text-decoration:none;cursor:pointer}
.ghost:hover{border-color:#62D9EE;color:#E6EDF3}
.sel{appearance:none;min-height:44px;padding:0 40px 0 14px;border-radius:8px;border:1px solid #62D9EE;background:#0A1620;color:#E6EDF3;font:600 15px 'Be Vietnam Pro',sans-serif;background-image:linear-gradient(45deg,transparent 50%,#62D9EE 50%),linear-gradient(135deg,#62D9EE 50%,transparent 50%);background-position:calc(100% - 20px) 19px,calc(100% - 15px) 19px;background-size:5px 5px;background-repeat:no-repeat}
.foot{border-top:1px solid #1C2A36;margin-top:auto}
a:focus-visible,button:focus-visible,select:focus-visible{outline:2px solid #C5F36A;outline-offset:2px}
.ring{transition:stroke-dasharray .9s cubic-bezier(.2,.7,.2,1)}
@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.rise{animation:rise .5s cubic-bezier(.2,.7,.2,1) both}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
```

### Script (rút)

```js

```

## 12
- html: `.working/screens-inner/12.html` (21556 bytes)

### Chữ trên màn

- Insights
- HẢI ĐỒ
- ·
- IT
- Bản đồ
- Insights
- Cố vấn
- Soi tin
- Chưa có hồ sơ
- Insights
- Mỗi thẻ là một câu mẫu, số điền thẳng từ bảng dữ liệu. Nhóm dưới 30 tin không hiện tỷ lệ.
- Toàn quốc · snapshot 02/11/2026 · [Nguồn 1], [Nguồn 2]
- Cửa vào cho người mới
- Mẫu câu E1: “{vai trò}: {x}% tin nhận Intern hoặc Fresher (n = {n})”
- {{c.role}}
- :
- {{c.p}}%
- tin nhận Intern hoặc Fresher
- {{c.k}}/{{c.n}} tin · n = {{c.n}} · 02/11/2026
- {{c.role}}
- :
- chưa đủ dữ liệu (n = {{c.n}})
- Cần ít nhất 30 tin để hiện tỷ lệ. Thẻ sẽ cập nhật ở snapshot sau.
- Xem lộ trình {{c.role}} →
- Bộ kỹ năng hay đi cùng nhau
- Mẫu câu C1: “Trong {n} tin có {A}, {x}% cũng nhắc {B}”
- {{c.a}}
- +
- {{c.b}}
- Trong
- {{c.n}}
- tin có {{c.a}},
- {{c.p}}%
- cũng nhắc {{c.b}}.
- {{c.k}}/{{c.n}} tin · 02/11/2026
- {{c.a}} và {{c.b}}:
- chưa đủ dữ liệu (n = {{c.n}} tin có {{c.a}})
- Cần ít nhất 30 tin có {{c.a}}.
- Chưa có CV?
- Tự đánh dấu những kỹ năng bạn đã học để xem lộ trình của một vai trò. Không cần file, không cần tài khoản.
- Đánh dấu kỹ năng đã có
- Câu trên thẻ là mẫu câu cố định, số lấy từ bảng tổng hợp · snapshot 02/11/2026
- Chính sách dữ liệu
- class Component extends DCLogic { renderVals() { var E = [['QA/Tester', 53, 121], ['Frontend', 72, 199], ['Backend', 108, 374], ['Data', 33, 136], ['DevOps', 13, 101], ['AI/ML Engineer', 0, 19]]; var P = [['Java', 'Spring Boot', 119, 168], ['Python', 'SQL', 97, 143], ['React', 'TypeScript', 91, 142], ['Docker', 'Kubernetes', 62, 131], ['Flutter', 'Firebase', 0, 24]]; var card = function (ok) { return { bs: ok ? 'solid' : 'dashed', bc: ok ? '#1C2A36' : '#5A4426' }; }; return { entry: E.map(function (e) { var ok = e[2] >= 30, c = card(ok); return { role: e[0], k: e[1], n: e[2], p: ok ? Math.round(100 * e[1] / e[2]) : 0, ok: ok, low: !ok, bs: c.bs, bc: c.bc }; }), pairs: P.map(function (e) { var ok = e[3] >= 30, c = card(ok); return { a: e[0], b: e[1], k: e[2], n: e[3], p: ok ? Math.round(100 * e[2] / e[3]) : 0, ok: ok, low: !ok, bs: c.bs, bc: c.bc }; }) }; } }

### CSS (không font-face)

```css
/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

body{margin:0;background:#070B10}
a{color:#C5F36A}a:hover{color:#E4FFB5}
.root{font-family:'Be Vietnam Pro',system-ui,sans-serif;color:#E6EDF3;background-color:#070B10;background-image:linear-gradient(rgba(98,217,238,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(98,217,238,.04) 1px,transparent 1px);background-size:40px 40px;min-height:100vh;display:flex;flex-direction:column}
.mono{font-family:'JetBrains Mono',ui-monospace,Menlo,monospace}
.k{font:600 11px/1.4 'JetBrains Mono',ui-monospace,monospace;color:#9FB0C2;letter-spacing:.08em;text-transform:uppercase}
.wrap{width:100%;max-width:1280px;margin:0 auto;padding:0 24px;box-sizing:border-box}
.hdr{border-bottom:1px solid #1C2A36;background:#0A1017}
.logo{display:inline-flex;align-items:center;gap:10px;text-decoration:none;color:#E6EDF3;font-weight:700;font-size:16px;letter-spacing:.04em;min-height:44px}
.logo:hover{color:#E6EDF3}
.nav{display:flex;gap:2px;flex:1 1 auto;min-width:0;overflow-x:auto}
.nav a{display:inline-flex;align-items:center;min-height:52px;padding:0 14px;color:#9FB0C2;text-decoration:none;font-weight:500;font-size:14px;border-bottom:2px solid transparent;white-space:nowrap}
.nav a:hover{color:#E6EDF3}
.nav a.on{color:#E6EDF3;border-bottom-color:#62D9EE}
.prof{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 14px;border-radius:999px;border:1px solid #243543;color:#C4D0DC;font-size:12px;text-decoration:none;white-space:nowrap;box-sizing:border-box}
.prof:hover{border-color:#62D9EE;color:#E6EDF3}
.panel{border:1px solid #1C2A36;background:#0D141C;border-radius:12px;padding:20px;box-sizing:border-box}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:48px;padding:0 20px;border-radius:8px;border:0;background:#C5F36A;color:#0A0F05;font:600 15px 'Be Vietnam Pro',sans-serif;text-decoration:none;cursor:pointer}
.btn:hover{color:#0A0F05;background:#D6FA94}
.card{display:flex;flex-direction:column;gap:12px;padding:18px;border-radius:12px;background:#0D141C;box-sizing:border-box}
.foot{border-top:1px solid #1C2A36;margin-top:auto}
a:focus-visible,button:focus-visible{outline:2px solid #C5F36A;outline-offset:2px}
@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.rise{animation:rise .5s cubic-bezier(.2,.7,.2,1) both}
@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.bar{transform-origin:left center;animation:grow .9s cubic-bezier(.2,.7,.2,1) both}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
```

### Script (rút)

```js

```

## 13
- html: `.working/screens-inner/13.html` (23765 bytes)

### Chữ trên màn

- Cố vấn — tự chọn kỹ năng, không cần CV
- HẢI ĐỒ
- ·
- IT
- Bản đồ
- Insights
- Cố vấn
- Soi tin
- Hồ sơ: {{count}} kỹ năng tự chọn · trong trình duyệt
- Tự chọn kỹ năng bạn đã có
- Không cần CV. Bấm vào những kỹ năng bạn đã học — hồ sơ chỉ nằm trong trình duyệt này.
- Snapshot 02/11/2026 · [Nguồn 1], [Nguồn 2]
- Kỹ năng đã có · chạm để bật/tắt
- {{s.mark}} {{s.name}}
- {{r.label}}
- {{roleMeta}}
- Có
- {{overlap}}
- kỹ năng trong lộ trình này trùng với hồ sơ của bạn.
- {{t.title}}
- {{t.rule}}
- {{i.name}}
- ✓ ĐÃ CÓ
- {{i.p}}% · {{i.k}}/{{n}}
- Lưu hồ sơ trong trình duyệt
- ← Quay lại Insights
- Có CV rồi? Đối chiếu bằng CV →
- Tỷ lệ = số tin có nhắc kỹ năng / n tin của vai trò · Intern–Junior · toàn quốc
- Chính sách dữ liệu
- {{toast}}
- class Component extends DCLogic { constructor(props) { super(props); this.state = { role: 'de', mine: ['Java', 'SQL', 'Git'], toast: '' }; this.tt = null; } componentWillUnmount() { if (this.tt) clearTimeout(this.tt); } renderVals() { var self = this, st = this.state; var R = { be: { label: 'Backend', n: 52, sk: [['SQL', 42], ['Java', 36], ['Git', 33], ['REST API', 31], ['Spring Boot', 27], ['MySQL', 23], ['PostgreSQL', 20], ['Docker', 18], ['CI/CD', 17], ['Microservices', 16], ['Redis', 16], ['Kafka', 6]] }, de: { label: 'Data Engineer', n: 38, sk: [['SQL', 33], ['Python', 31], ['ETL', 23], ['Git', 18], ['Cloud (AWS/GCP)', 15], ['Spark', 14], ['Docker', 13], ['Airflow', 12], ['Java', 7]] } }; var POOL = ['Java', 'SQL', 'Git', 'Python', 'JavaScript', 'REST API', 'Spring Boot', 'MySQL', 'PostgreSQL', 'Docker', 'Linux', 'Excel', 'ETL', 'Spark']; var cur = R[st.role], n = cur.n; var has = function (s) { return st.mine.indexOf(s) >= 0; }; var TIER = [['core', 'Cốt lõi', '≥ 60%', '#62D9EE', 'solid'], ['common', 'Thường gặp', '30–59%', '#9FB0C2', 'solid'], ['spec', 'Riêng của công ty', '
- = 60 ? 'core' : p >= 30 ? 'common' : 'spec'; }; var overlap = cur.sk.filter(function (s) { return has(s[0]); }).length; return { count: st.mine.length, n: n, pool: POOL.map(function (s) { var on = has(s); return { name: s, on: on, mark: on ? '✓' : '+', cls: on ? 'chip on' : 'chip', toggle: function () { self.setState({ mine: on ? st.mine.filter(function (x) { return x !== s; }) : st.mine.concat([s]) }); } }; }), roles: ['be', 'de'].map(function (id) { var on = id === st.role; return { label: R[id].label, on: on, cls: on ? 'on' : '', pick: function () { self.setState({ role: id }); } }; }), roleMeta: cur.label + ' · Intern–Junior · n = ' + n + ' tin · 02/11/2026', overlap: overlap, tiers: TIER.map(function (t) { return { title: t[1], rule: t[2], tc: t[3], bs: t[4], items: cur.sk.filter(function (s) { return tierOf(Math.round(100 * s[1] / n)) === t[0]; }).map(function (s) { var h = has(s[0]), p = Math.round(100 * s[1] / n); return { name: s[0], k: s[1], p: p, have: h, bc: h ? '#62D9EE' : '#1C2A36', bar: h ? '#62D9EE' : '#3E6A80', cls: h ? 'node hit' : 'node' }; }) }; }), toast: st.toast, toastOn: !!st.toast, save: function () { if (self.tt) clearTimeout(self.tt); self.setState({ toast: 'Đã lưu ' + st.mine.length + ' kỹ năng trong trình duyệt này.' }); self.tt = setTimeout(function () { self.setState({ toast: '' }); }, 2400); } }; } }

### CSS (không font-face)

```css
/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

body{margin:0;background:#070B10}
a{color:#C5F36A}a:hover{color:#E4FFB5}
.root{font-family:'Be Vietnam Pro',system-ui,sans-serif;color:#E6EDF3;background-color:#070B10;background-image:linear-gradient(rgba(98,217,238,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(98,217,238,.04) 1px,transparent 1px);background-size:40px 40px;min-height:100vh;display:flex;flex-direction:column}
.mono{font-family:'JetBrains Mono',ui-monospace,Menlo,monospace}
.k{font:600 11px/1.4 'JetBrains Mono',ui-monospace,monospace;color:#9FB0C2;letter-spacing:.08em;text-transform:uppercase}
.wrap{width:100%;max-width:1280px;margin:0 auto;padding:0 24px;box-sizing:border-box}
.hdr{border-bottom:1px solid #1C2A36;background:#0A1017}
.logo{display:inline-flex;align-items:center;gap:10px;text-decoration:none;color:#E6EDF3;font-weight:700;font-size:16px;letter-spacing:.04em;min-height:44px}
.logo:hover{color:#E6EDF3}
.nav{display:flex;gap:2px;flex:1 1 auto;min-width:0;overflow-x:auto}
.nav a{display:inline-flex;align-items:center;min-height:52px;padding:0 14px;color:#9FB0C2;text-decoration:none;font-weight:500;font-size:14px;border-bottom:2px solid transparent;white-space:nowrap}
.nav a:hover{color:#E6EDF3}
.nav a.on{color:#E6EDF3;border-bottom-color:#62D9EE}
.prof{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 14px;border-radius:999px;border:1px solid #243543;color:#C4D0DC;font-size:12px;text-decoration:none;white-space:nowrap;box-sizing:border-box}
.panel{border:1px solid #1C2A36;background:#0D141C;border-radius:12px;padding:20px;box-sizing:border-box}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:48px;padding:0 20px;border-radius:8px;border:0;background:#C5F36A;color:#0A0F05;font:600 15px 'Be Vietnam Pro',sans-serif;text-decoration:none;cursor:pointer}
.btn:hover{color:#0A0F05;background:#D6FA94}
.ghost{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:44px;padding:0 16px;border-radius:8px;border:1px solid #2E4456;background:transparent;color:#C4D0DC;font:500 14px 'Be Vietnam Pro',sans-serif;text-decoration:none;cursor:pointer}
.ghost:hover{border-color:#62D9EE;color:#E6EDF3}
.chip{display:inline-flex;align-items:center;gap:6px;min-height:44px;padding:0 14px;border-radius:999px;border:1px dashed #3A5163;background:transparent;color:#C4D0DC;font:500 14px 'Be Vietnam Pro',sans-serif;cursor:pointer;box-sizing:border-box}
.chip:hover{border-color:#62D9EE;color:#E6EDF3}
.chip.on{border-style:solid;border-color:#62D9EE;background:rgba(98,217,238,.14);color:#E6EDF3}
.seg{display:inline-grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:3px;padding:3px;border:1px solid #243543;border-radius:10px;background:#0A1118}
.seg button{min-height:44px;padding:0 16px;border:0;border-radius:7px;background:transparent;color:#A9B8C7;font:600 14px 'Be Vietnam Pro',sans-serif;cursor:pointer}
.seg button.on{background:rgba(98,217,238,.16);color:#E6EDF3;box-shadow:inset 0 0 0 1px #62D9EE}
.node{display:flex;flex-direction:column;gap:6px;padding:12px 14px;border-radius:10px;background:#0A1118;transition:border-color .3s,background .3s}
.foot{border-top:1px solid #1C2A36;margin-top:auto}
.toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);z-index:50;padding:12px 18px;border-radius:10px;background:#E6EDF3;color:#0A0F05;font:600 14px 'Be Vietnam Pro',sans-serif;box-shadow:0 12px 40px rgba(0,0,0,.5)}
a:focus-visible,button:focus-visible{outline:2px solid #C5F36A;outline-offset:2px}
@keyframes glow{0%{box-shadow:0 0 0 0 rgba(98,217,238,.55)}100%{box-shadow:0 0 0 10px rgba(98,217,238,0)}}
.hit{animation:glow 1s ease-out 1}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
```

### Script (rút)

```js

```

## 14
- html: `.working/screens-inner/14.html` (17419 bytes)

### Chữ trên màn

- Chính sách dữ liệu — Hải Đồ IT
- HẢI ĐỒ
- ·
- IT
- Mở Hải Đồ IT →
- Trang công khai
- Chính sách dữ liệu
- Trang này nói rõ Hải Đồ IT lấy dữ liệu gì, dùng vào việc gì, công bố ở mức nào, và cách yêu cầu gỡ.
- Cập nhật lần cuối: [ngày cập nhật]
- 01
- Mục đích
- Hải Đồ IT là dự án nghiên cứu học thuật của [tên nhóm / đơn vị nghiên cứu], tìm hiểu kỹ năng nào xuất hiện trong tin tuyển dụng IT ở Việt Nam. Dự án không bán dữ liệu và không chạy quảng cáo.
- 02
- Nguồn đang dùng
- [Nguồn 1]
- — [loại trang], dùng từ [ngày].
- [Nguồn 2]
- — [loại trang], dùng từ [ngày].
- Từ mỗi tin đăng công khai, chúng tôi lấy: chức danh, phần yêu cầu, thành phố, cấp bậc, khoảng lương nếu tin có công bố, và ngày đăng.
- Chúng tôi không lấy tên, email hay số điện thoại của người đăng tin.
- 03
- Dữ liệu được công bố ở mức tổng hợp
- Chỉ công bố tỷ lệ và số tin của một nhóm, luôn kèm cỡ mẫu n và ngày snapshot.
- Nhóm dưới 30 tin hiện “chưa đủ dữ liệu”, không hiện tỷ lệ.
- Trang công khai không liệt kê từng tin, không ghi tên công ty, không dẫn link tới tin gốc.
- 04
- CV và tin bạn dán không được lưu
- CV:
- đọc ngay trên trình duyệt. Chỉ khi bạn đồng ý, phần chữ trong CV mới được gửi tới một dịch vụ AI bên ngoài để nhận diện tên kỹ năng, và không được lưu lại.
- Tin bạn dán vào Soi tin:
- chỉ dùng để đối chiếu rồi bỏ, không lưu.
- Hồ sơ:
- danh sách kỹ năng nằm trong trình duyệt của bạn. Không có tài khoản; bạn có thể xoá bất cứ lúc nào.
- 05
- Yêu cầu gỡ dữ liệu
- Nếu bạn là chủ một nguồn dữ liệu, nhà tuyển dụng, hay bất kỳ ai muốn gỡ dữ liệu liên quan tới mình, hãy gửi email tới
- [email liên hệ]
- . Chúng tôi xử lý yêu cầu gỡ trong vòng
- 48 giờ
- .
- Ví dụ trang công khai: vai trò Backend →
- Mở bản đồ nhu cầu →
- Hải Đồ IT · dự án nghiên cứu học thuật
- Liên hệ gỡ dữ liệu: [email liên hệ]
- class Component extends DCLogic { renderVals() { return {}; } }

### CSS (không font-face)

```css
/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

body{margin:0;background:#070B10}
a{color:#C5F36A}a:hover{color:#E4FFB5}
.root{font-family:'Be Vietnam Pro',system-ui,sans-serif;color:#E6EDF3;background:#070B10;min-height:100vh;display:flex;flex-direction:column}
.mono{font-family:'JetBrains Mono',ui-monospace,Menlo,monospace}
.k{font:600 11px/1.4 'JetBrains Mono',ui-monospace,monospace;color:#9FB0C2;letter-spacing:.08em;text-transform:uppercase}
.wrap{width:100%;max-width:1280px;margin:0 auto;padding:0 24px;box-sizing:border-box}
.hdr{border-bottom:1px solid #1C2A36;background:#0A1017}
.logo{display:inline-flex;align-items:center;gap:10px;text-decoration:none;color:#E6EDF3;font-weight:700;font-size:16px;letter-spacing:.04em;min-height:52px}
.logo:hover{color:#E6EDF3}
.doc{max-width:760px;margin:0 auto;padding:40px 24px 64px;box-sizing:border-box;width:100%;display:flex;flex-direction:column;gap:32px}
.doc h2{margin:0 0 10px;font-size:20px;font-weight:700}
.doc p,.doc li{font-size:16px;line-height:1.7;color:#D5DEE7}
.doc p{margin:0}
.doc ul{margin:8px 0 0;padding-left:20px;display:flex;flex-direction:column;gap:6px}
.sec{display:grid;grid-template-columns:48px minmax(0,1fr);gap:16px;border-top:1px solid #1C2A36;padding-top:24px}
.num{font:600 13px 'JetBrains Mono',monospace;color:#62D9EE;padding-top:4px}
.foot{border-top:1px solid #1C2A36;margin-top:auto}
a:focus-visible{outline:2px solid #C5F36A;outline-offset:2px}
@media (max-width:560px){.sec{grid-template-columns:1fr;gap:6px}}
```

### Script (rút)

```js

```

## 15
- html: `.working/screens-inner/15.html` (19970 bytes)

### Chữ trên màn

- Vai trò Backend — trang công khai
- HẢI ĐỒ
- ·
- IT
- [tên miền]/vai-tro/{{slug}}
- Vai trò · mọi cấp bậc · toàn quốc
- {{role}}
- Trong
- 374
- tin {{role}} đăng công khai trên toàn quốc, mọi cấp bậc,
- SQL
- xuất hiện ở
- 74%
- tin,
- Git
- ở
- 58%
- và
- Java
- ở
- 52%
- . Nguồn đang bật: [Nguồn 1], [Nguồn 2]. Snapshot 02/11/2026.
- Chưa đủ dữ liệu (n = 21).
- Trang sẽ hiện tỷ lệ kỹ năng khi có từ 30 tin trở lên. Nguồn đang bật: [Nguồn 1], [Nguồn 2]. Snapshot 02/11/2026.
- Kỹ năng hay gặp
- n = 374 tin · 02/11/2026
- KỸ NĂNG
- TỶ LỆ TIN
- SỐ TIN
- {{s.name}}
- {{s.p}}%
- {{s.k}}/374
- Cơ cấu cấp bậc
- n = 374 tin · 02/11/2026
- Intern 13
- Fresher 7
- Junior 32
- Middle 168
- Senior trở lên 154
- Trang này chỉ công bố số liệu tổng hợp. Không liệt kê tin, không ghi tên công ty, không dẫn link tới tin gốc. Chỉ gồm tin đăng công khai trên các nguồn đang bật; tin trùng giữa các nguồn đã được gộp.
- Xem theo thành phố và cấp bậc trong Hải Đồ IT
- Chính sách dữ liệu →
- Hải Đồ IT · dự án nghiên cứu học thuật · đọc không cần tài khoản
- Chính sách dữ liệu
- class Component extends DCLogic { renderVals() { var ok = (this.props.mau ?? 'Backend · n ≥ 30') === 'Backend · n ≥ 30'; var S = [['SQL', 277], ['Git', 217], ['Java', 194], ['Docker', 172], ['REST API', 165], ['Spring Boot', 146]]; return { ok: ok, low: !ok, role: ok ? 'Backend' : 'Embedded', slug: ok ? 'backend' : 'embedded', skills: S.map(function (s) { return { name: s[0], k: s[1], p: Math.round(100 * s[1] / 374) }; }) }; } }

### CSS (không font-face)

```css
/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

/* cyrillic-ext */

/* cyrillic */

/* greek */

/* vietnamese */

/* latin-ext */

/* latin */

body{margin:0;background:#070B10}
a{color:#C5F36A}a:hover{color:#E4FFB5}
.root{font-family:'Be Vietnam Pro',system-ui,sans-serif;color:#E6EDF3;background:#070B10;min-height:100vh;display:flex;flex-direction:column}
.mono{font-family:'JetBrains Mono',ui-monospace,Menlo,monospace}
.k{font:600 11px/1.4 'JetBrains Mono',ui-monospace,monospace;color:#9FB0C2;letter-spacing:.08em;text-transform:uppercase}
.wrap{width:100%;max-width:1280px;margin:0 auto;padding:0 24px;box-sizing:border-box}
.hdr{border-bottom:1px solid #1C2A36;background:#0A1017}
.logo{display:inline-flex;align-items:center;gap:10px;text-decoration:none;color:#E6EDF3;font-weight:700;font-size:16px;letter-spacing:.04em;min-height:52px}
.logo:hover{color:#E6EDF3}
.doc{max-width:860px;margin:0 auto;padding:40px 24px 64px;box-sizing:border-box;width:100%;display:flex;flex-direction:column;gap:28px}
.panel{border:1px solid #1C2A36;background:#0D141C;border-radius:12px;padding:20px;box-sizing:border-box}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:48px;padding:0 20px;border-radius:8px;border:0;background:#C5F36A;color:#0A0F05;font:600 15px 'Be Vietnam Pro',sans-serif;text-decoration:none}
.btn:hover{color:#0A0F05;background:#D6FA94}
.foot{border-top:1px solid #1C2A36;margin-top:auto}
a:focus-visible{outline:2px solid #C5F36A;outline-offset:2px}
@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.bar{transform-origin:left center;animation:grow .9s cubic-bezier(.2,.7,.2,1) both}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
```

### Script (rút)

```js

```
