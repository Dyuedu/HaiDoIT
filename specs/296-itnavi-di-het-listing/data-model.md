# Data model: ITnavi đi hết listing

Không đổi bảng, cột, revision Alembic.

File seen `data/seen/<ngày>/itnavi.json` giữ nguyên các khóa. Chỉ khác giá trị: `listing_complete` có thể là `false` kèm `error` "met X of Y listed jobs" khi lượt quét gặp dưới 90% tổng số site in.
