"""Lộ trình cho demo trên máy (#217): hiện cả lộ trình chưa có giảng viên rà soát (#96).

Chỉ `haido_api.demo` dựng lớp này; nó không có trong `IMPLEMENTATIONS`, nên không biến môi trường nào bật được trên prod.
Lộ trình chưa rà soát luôn mang lưu ý `draft_path`.
"""

from haido_api.stat_market import StatMarket
from haido_api.stat_path import RolePath


class DraftPathMarket(StatMarket):
    """`StatMarket` không đòi dấu rà soát. Các phép khác không đổi."""

    def _path_for(self, role: str) -> RolePath | None:
        return self._paths.get(role)
