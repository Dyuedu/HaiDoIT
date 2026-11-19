# θ: ngưỡng chia kỹ năng thành core, common, rare

Tài liệu này là nơi cả nhóm đọc giá trị θ đã đóng băng (#102). Nguồn của giá trị là `config/theta.toml`; file này giải thích và giữ bằng chứng hiệu chỉnh.

## θ là gì

Mỗi vai trò, ở mỗi cấp bậc, có một tỷ lệ cho từng kỹ năng: số tin nhắc kỹ năng chia cho số tin đã quét kỹ năng của ô (`stat_skill_rates.rate`). Hai ngưỡng θ chia các kỹ năng thành ba nhóm (phép 4, `haido_core/domain/skill_groups.py`):

| Nhóm | Điều kiện | Ý nghĩa với người xem |
|---|---|---|
| core | `rate >= θ_core` | Kỹ năng cốt lõi của vai trò |
| common | `θ_common <= rate < θ_core` | Kỹ năng thường gặp |
| rare | `rate < θ_common` | Hiếm; API không trả dòng nào cho nhóm này |

Hồ sơ kỹ năng (#111) chỉ hiện nhóm core và common, và câu "bạn có X/Y kỹ năng cốt lõi" đếm theo nhóm core; lộ trình học (#121) xếp core trước common. Nhóm của mỗi dòng nằm ở `data.rows[].group` của `skill-rates`; θ đã dùng nằm ở `meta.thresholds` (kèm `theta_version`).

## Phiên bản hiện hành

Cột "Hiện hành" đánh dấu phiên bản mà `rules.theta_version` (`config/rules.toml`) đang chọn; `aggregate` ghi phiên bản này vào snapshot mới.

| Phiên bản | θ_core | θ_common | Hiệu chỉnh ngày | Hiện hành |
|---|---|---|---|---|
| `theta-1` | 0,3 | 0,1 | 2026-11-19 | có |

`theta-1` giữ nguyên giá trị đang chạy trước khi đóng băng, nên không màn hình nào đổi số khi đóng băng.

## Quy tắc đóng băng

1. Không bao giờ sửa hay xóa một phiên bản đã có trong `config/theta.toml`. Muốn đổi θ thì thêm một mục `[[versions]]` mới với `id` mới (`theta-2`, ...).
2. Thêm phiên bản mới thì làm cùng một commit: thêm vào `PINNED` trong `tests/core/test_gh102_theta_dong_bang.py`, đổi `theta_version` trong `config/rules.toml`, tăng `config_version`, ghi dòng mới vào bảng trên (đánh dấu cột "Hiện hành") và bằng chứng hiệu chỉnh vào file này. Test chỉ bắt được một phần:
   - Test ghim (`test_gh102_ac1_moi_phien_ban_da_dong_bang_co_trong_so_dang_ky_dung_gia_tri` và `test_gh102_ac1_so_dang_ky_khong_co_phien_ban_nao_ngoai_ban_ghi_cung`) đỏ khi một phiên bản đã ghim bị sửa, bị xóa, hoặc khi có phiên bản trong `config/theta.toml` chưa được thêm vào `PINNED`.
   - Test tài liệu (`test_gh102_ac2_moi_phien_ban_da_ghim_co_mat_trong_docs_data_theta_md` và `test_gh102_ac2_bang_phien_ban_hien_hanh_co_dong_cho_moi_phien_ban_va_danh_dau_rules_theta_version`) đỏ khi file này thiếu một phiên bản đã ghim hoặc đánh dấu sai phiên bản hiện hành.
   - Không test nào bắt được việc quên đổi `theta_version` trong `config/rules.toml` (hệ thống vẫn chạy bằng phiên bản cũ) hay quên tăng `config_version`. Hai bước này chỉ dựa vào người review.
3. Mỗi snapshot lưu phiên bản θ nó đã tính bằng (`haido.snapshots.theta_version`, ghi bởi `aggregate`). API nhóm kỹ năng của snapshot bằng θ của chính phiên bản đó và ghi nó vào `meta.thresholds.theta_version`. Vì vậy đổi phiên bản hiện hành chỉ ảnh hưởng snapshot tính sau đó; snapshot cũ không đổi nhóm.
4. Snapshot tính trước đóng băng có `theta_version` rỗng (NULL). Nó được đọc là `theta-1` (hằng `PRE_FREEZE_THETA_VERSION` trong `haido_core/config.py`), đúng giá trị khi đó. Không dựa vào vị trí: bộ đọc từ chối sổ đăng ký mà mục `[[versions]]` ĐẦU TIÊN không phải `theta-1`.
5. Snapshot ghi một phiên bản không có trong sổ đăng ký là dữ liệu hỏng: API trả lỗi 500 thay vì nhóm bằng θ khác.
6. Bộ đọc nghiêm ngặt: `id` không có khoảng trắng ở hai đầu, `calibrated_on` là ngày `YYYY-MM-DD`, không có khóa lạ trong một mục hay ở cấp cao nhất của `config/theta.toml`; `config/rules.toml` không được còn khóa `theta_core` hay `theta_common` (θ nay nằm ở `config/theta.toml`, `rules.toml` chỉ chọn bằng `theta_version`). Vi phạm là `ConfigError` lúc nạp.

## Giới hạn của việc đóng băng

- Ghi tay `UPDATE haido.snapshots SET theta_version = ...` sang một id khác đã có trong sổ đăng ký sẽ đổi nhóm của snapshot đó mà không ai hay: không có khóa ngoại hay ràng buộc check, và không test nào bắt được. Không làm việc này; muốn tính lại bằng θ khác thì chạy lại `aggregate` trên snapshot còn `open`.
- Sửa một phiên bản cũ trong `config/theta.toml` rồi sửa `PINNED` trong cùng commit thì mọi test vẫn xanh. Test ghim chỉ làm cho thay đổi hiện trong diff; người review phải từ chối commit nào sửa hay xóa một phiên bản đã đóng băng.
- Quên đổi `theta_version` hay quên tăng `config_version` khi thêm phiên bản không có test nào bắt (xem quy tắc 2).

## Bằng chứng hiệu chỉnh của `theta-1`

Nguồn: snapshot 2026-11-19, tỷ lệ cấp entry-level từ API công khai (`skill-roles`), mười vai trò có ít nhất 30 tin đã quét kỹ năng. Mỗi ô là `core,common`: số kỹ năng core và số kỹ năng common của vai trò đó.

| vai trò (n) | 0,3/0,1 (chọn) | 0,25/0,1 | 0,35/0,12 | 0,4/0,15 |
|---|---|---|---|---|
| it_infra (172) | 4,13 | 9,8 | 3,12 | 3,10 |
| ba_po_pm (155) | 4,20 | 5,19 | 3,14 | 1,13 |
| qa (90) | 7,19 | 10,16 | 5,16 | 5,9 |
| backend (75) | 12,31 | 18,25 | 7,31 | 2,25 |
| game (49) | 5,11 | 6,10 | 4,11 | 3,9 |
| ai_ml (40) | 14,28 | 19,23 | 9,25 | 7,22 |
| security (40) | 7,18 | 13,12 | 6,15 | 6,10 |
| other (39) | 3,19 | 3,19 | 1,14 | 1,12 |
| fullstack (38) | 17,43 | 24,36 | 10,41 | 5,36 |
| devops (30) | 15,35 | 17,33 | 12,27 | 11,22 |

Vì sao chọn 0,3/0,1:

- Đó là giá trị đang chạy, nên đóng băng không đổi màn hình nào.
- "Được nhắc trong khoảng 1 trên 3 tin entry-level" dễ giải thích cho người dùng.
- 0,4 chỉ còn 1 kỹ năng core cho BA/PO/PM và 2 cho Backend, quá ít để gọi là "cốt lõi". 0,25 cho Fullstack tới 24 kỹ năng core, quá nhiều.

Giới hạn đã biết: ở n từ 30 đến 40, sai số chuẩn của một tỷ lệ gần 0,3 vào khoảng ±0,07, nên kỹ năng nằm sát ngưỡng có thể đổi nhóm giữa hai snapshot dù θ không đổi. Đóng băng θ chỉ loại nguồn đổi nhóm do ngưỡng, không loại nhiễu lấy mẫu.

## Tính lại bảng

Script chỉ đọc (`snapshots`, `stat_skill_rates` và `stat_sources`, không đọc bảng tin) và in cùng dạng bảng cho snapshot đọc được mới nhất:

```text
HAIDO_DATABASE_URL=postgresql+psycopg://... PYTHONPATH=. uv run python tools/theta/calibrate_theta.py
```

Ô `core,common` đếm theo nhóm: common không gồm kỹ năng core. Mặc định so bốn cặp của bảng trên ở cấp `entry`. Đổi cặp hay cấp bằng `--pairs 0.3/0.1,0.4/0.15` và `--level mid`. Số trong bảng trên là của snapshot 2026-11-19; chạy lại ở snapshot khác sẽ cho số khác, đó là chuyện bình thường và không đổi phiên bản đã đóng băng.
