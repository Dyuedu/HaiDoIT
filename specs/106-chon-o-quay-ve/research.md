# Research: chọn ô và thứ tự quay về (#106, dùng chung cho #103 và #151)

Ngày 17/11/2026.

## kaptinlin/go-i18n

- Link: https://github.com/kaptinlin/go-i18n/blob/1612a824823f49c91f71d7c9e8d8eca6f7328e1b/localizer.go (dòng 92 đến 101: `lookupFallback`, `TranslationSourceFallback`)
- Cách làm: tra theo chuỗi locale từ hẹp đến rộng; kết quả ghi nguồn đã cấp bản dịch (`source`), nên người gọi biết có quay về hay không và quay về đâu.
- Lấy: kết quả của một lần chọn mang theo "tập đã dùng" (ô, cỡ mẫu, nhãn), không chỉ giá trị; chuỗi quay về là danh sách có thứ tự cố định, tra từ hẹp đến rộng và dừng ở phần tử đầu tiên đạt.
- Không lấy: tra theo chuỗi ký tự và gói catalog; cấu hình chuỗi quay về do người dùng đổi được (ở đây thứ tự cố định theo FR-19, AD-6, không có tham số đổi phạm vi); trả `name` làm giá trị cuối khi không có gì (ở đây ô cuối cùng đã thử, kèm nhãn "chưa đủ dữ liệu", để số thành `null_data`).

## Tìm không ra mã có ích khác

`gh search repos` với "hierarchical fallback sample size backoff", "salary benchmark minimum sample size fallback broader group", "k-anonymity suppression": không có repo nào có chuỗi quay về theo cỡ mẫu và nhãn đi kèm, chỉ có công cụ ẩn danh hóa dữ liệu (ví dụ `faridhafizh/Pryv`), vốn ẩn dòng chứ không quay về tập rộng hơn. Không lấy.

## Quyết định rút ra

- Thứ tự quay về đã chốt (issue #106): `(vai trò, cấp)`, nếu cấp thô thuộc một nhóm thì `(vai trò, nhóm)`, rồi `(vai trò, all)`. Khác chuỗi bốn bước của PRD §3 ở chỗ nhánh chưa có dữ liệu; khi yêu cầu có nhánh, mỗi bước thử nhánh trước rồi nhánh `all` (đúng thứ tự "giữ cấp bậc trước, giữ nhánh sau").
- Cỡ mẫu quyết định ô do người gọi đưa qua `CellStats.sample_n` (tỷ lệ kỹ năng dùng `n_scanned`, AD-17), để ô được chọn không bị ẩn ngay sau đó.
- Bảng ô đi vào qua `lookup` ở constructor: `haido_core/domain` không import DB hay API (hướng phụ thuộc).
