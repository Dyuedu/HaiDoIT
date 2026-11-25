"""App demo trên máy: mọi phép đọc snapshot thật, lộ trình là bản nháp (`draft_path.py`).

Chỉ `deploy/compose.demo.yml` chạy module này. Prod và local chạy `haido_api.main:app`.
"""

from haido_api.draft_path import DraftPathMarket
from haido_api.main import create_app
from haido_api.routes.market import load_sources

app = create_app(load_sources() | {"learning_path": DraftPathMarket()})
