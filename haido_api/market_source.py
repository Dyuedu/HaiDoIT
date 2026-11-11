"""Interface nguồn số liệu thị trường mà route đọc qua.

Route không biết số đến từ đâu. #2 chỉ có bản giả (`fake_market.FakeMarket`). Story 1.21
cài bản thật cho `city_shares`, #27 cài bản thật cho `skill_rates`; mỗi phép chọn nguồn
riêng qua biến môi trường (xem `routes/market.py`), nên route và schema không đổi.
"""

from datetime import date
from typing import Protocol

from haido_api.schemas.market import CitySharesData, NewcomerRolesData, SkillRatesData
from haido_core.domain.envelope import Envelope


class UnknownCell(LookupError):
    """Không có ô thống kê nào cho tham số đã chọn. Route trả 404 `unknown_cell`."""

    def __init__(self, message: str, *, snapshot_date: date | None) -> None:
        super().__init__(message)
        self.message = message
        self.snapshot_date = snapshot_date


class MarketReadModel(Protocol):
    """Nguồn đọc số liệu thị trường của snapshot mới nhất còn đọc được."""

    def city_shares(self, *, role: str, level: str) -> Envelope[CitySharesData]:
        """Tỷ trọng từng thành phố trong số tin của `role` ở cấp bậc lọc `level` trên toàn quốc.

        `level` là `all`, một nhóm (`entry`) hoặc một cấp (#163); route đã kiểm nó thuộc cấu hình.

        Raises:
            UnknownCell: không có ô cho `role` ở `level`.
        """
        ...

    def skill_rates(self, *, role: str, level: str) -> Envelope[SkillRatesData]:
        """Tỷ lệ xuất hiện của từng kỹ năng trong ô của `role` × `level`, sau khi quay về.

        Raises:
            UnknownCell: không có ô nào, kể cả sau khi quay về.
        """
        ...

    def newcomer_roles(self) -> Envelope[NewcomerRolesData]:
        """Mỗi vai trò: số tin entry-level, tỷ lệ trong số tin của vai trò, và n (#144).

        Dòng theo thứ tự của `NewcomerRolesData.rows`.

        Raises:
            UnknownCell: chưa có snapshot nào đọc được.
        """
        ...
