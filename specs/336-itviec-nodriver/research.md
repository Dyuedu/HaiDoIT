# Research: #336 ITviec nodriver

## Nguồn tham khảo

Kiến trúc nodriver đã có sẵn trong repo cho TopCV (`crawlers/topcv.py`, commit
`1a8e3f6`). Bản viết lại ITviec theo cùng mô hình: Chrome profile cố định,
SQLite job queue, smart DOM wait.

## Lấy gì

- Cấu trúc `_nodriver_main()` lồng import lazy, giống cách `topcv.py` giữ
  `nodriver` ngoài import đầu file.
- Hàng đợi SQLite + export JSONL, tách ra cấp module để test không cần nodriver.
- Pipeline type `"nodriver"` → `xvfb-run` trên Linux không DISPLAY, giống topcv.

## Không lấy

- Không thay đổi `browser_polite.py` hay `polite.py` — đường Playwright giữ nguyên.
- Không viết test end-to-end cho nodriver (cần Chrome thật + nodriver, CI không có).
