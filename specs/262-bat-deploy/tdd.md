# TDD: Bật deploy

Một hành vi một test. Assert trên nội dung workflow và file compose, không gọi VPS.

Lệnh:

```text
uv run pytest tests/deploy/test_gh262_bat_deploy.py -q
```

RED: 5 failed, 1 passed. Test project name đã xanh vì `compose.prod.yml` vốn có `name: haido-prod`. Bốn test kia đỏ vì workflow chưa có đường dẫn, `scp`, Alembic và cổng localhost.

GREEN: `uv run pytest tests/deploy/test_gh262_bat_deploy.py tests/deploy/test_compose_ad1_ad15.py tests/deploy/test_gh162_ban_do_doc_snapshot_that.py -q` → 16 passed.
