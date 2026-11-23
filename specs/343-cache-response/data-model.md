# Data Model: Cache response

Không đổi schema, không có Alembic revision mới.

API đọc thêm bảng `haido.snapshots` qua `StatMarket.version()` (khi cache bật, mỗi request một lần):

```sql
SELECT count(*)::text || ':' || coalesce(md5(string_agg(
  snapshot_id::text || '|' || status || '|' || coalesce(closed_at::text, ''), ',' ORDER BY snapshot_id)), '')
FROM haido.snapshots WHERE status <> 'open'
```

Bảng có một dòng mỗi ngày; không thêm index.
