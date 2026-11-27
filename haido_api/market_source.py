"""Interface nguồn số liệu thị trường mà route đọc qua.

Route không biết số đến từ đâu. #2 chỉ có bản giả (`fake_market.FakeMarket`). Story 1.21
cài bản thật cho `city_shares`, #27 cài bản thật cho `skill_rates`; mỗi phép chọn nguồn
riêng qua biến môi trường (xem `routes/market.py`), nên route và schema không đổi.
"""

from collections.abc import Collection
from datetime import date
from typing import Protocol

from haido_api.schemas.learning_path import LearningPathData
from haido_api.schemas.market import (
    CitySharesData,
    MarketOverviewData,
    NewcomerRolesData,
    SkillRatesData,
    SkillRolesData,
)
from haido_api.schemas.posting import PostingCheckData, PostingFacts
from haido_core.domain.envelope import Envelope


class UnknownCell(LookupError):
    """Không có ô thống kê nào cho tham số đã chọn. Route trả 404 `unknown_cell`."""

    def __init__(self, message: str, *, snapshot_date: date | None) -> None:
        super().__init__(message)
        self.message = message
        self.snapshot_date = snapshot_date


class CheckUnavailable(RuntimeError):
    """Nguồn chưa có số thật để soi tin dán (#230, tới #234): "chưa sẵn sàng, thử lại sau", không phải "không có số cho vai trò này".

    Route trả 503 `check_unavailable`, khác 404 `unknown_cell` (vai trò và cấp không có ô), nên màn không nhầm một chỗ chưa nối số với
    một kết quả cuối. Thông điệp không có chữ của tin: nguồn không bao giờ nhận chữ.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class UnknownSkill(LookupError):
    """Mã kỹ năng đúng định dạng nhưng không có trong bộ từ vựng. Route trả 404 `unknown_skill` (#166)."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class MarketReadModel(Protocol):
    """Nguồn đọc số liệu thị trường của snapshot mới nhất còn đọc được."""

    def version(self) -> str:
        """Dấu của tập snapshot đã chốt. Mọi phép khác trả cùng kết quả khi dấu không đổi (#343).

        Cache response hỏi dấu này ở mỗi request và bỏ cache khi nó đổi. Phải rẻ: không đọc bảng `stat_*`.
        """
        ...

    def city_shares(self, *, role: str, level: str, years: str) -> Envelope[CitySharesData]:
        """Tỷ trọng từng thành phố trong số tin của `role` ở cấp bậc lọc `level` và mốc số năm `years` trên toàn quốc.

        `level` là `all`, một nhóm (`entry`) hoặc một cấp (#163); `years` là `any` hoặc một mốc của `years_options`
        (#280). Route đã kiểm cả hai thuộc cấu hình.

        Raises:
            UnknownCell: không có ô cho `role` ở `level` và `years`.
        """
        ...

    def skill_rates(
        self, *, role: str, level: str, have: Collection[str] = ()
    ) -> Envelope[SkillRatesData]:
        """Tỷ lệ xuất hiện của từng kỹ năng trong ô của `role` × `level`, sau khi quay về.

        `have` là mã kỹ năng của hồ sơ (AD-22): đặt cờ `have` từng dòng và đếm `have_core`. Không đổi thứ tự dòng.

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

    def market_overview(self) -> Envelope[MarketOverviewData]:
        """Toàn cảnh thị trường của snapshot mới nhất (#327): cấp bậc, vai trò, nơi làm việc, số năm kinh nghiệm.

        Mọi tỷ trọng tính ở máy chủ bằng `haido_api.market_overview.build_market_overview`. Route đọc nguồn của
        `newcomer_roles`, vì hai phép cùng đọc ô toàn quốc của `stat_cells`.

        Raises:
            UnknownCell: chưa có snapshot nào đọc được.
        """
        ...

    def learning_path(self, *, role: str, level: str, have: Collection[str]) -> Envelope[LearningPathData]:
        """Lộ trình học đã xếp của `role` ở `level`, kèm tỷ lệ của từng kỹ năng (#212).

        `have` là các mã kỹ năng người dùng đã có (đúng định dạng, không trùng, tối đa 200); nguồn tự đánh cờ và
        đếm (AD-22) bằng `haido_api.learning_path.apply_have`. Vai trò chưa có lộ trình đã rà soát trả
        `status = not_ready`, không phải lỗi.

        Raises:
            UnknownCell: vai trò không có, hoặc không có ô cho `level`.
        """
        ...

    def skill_roles(self, *, skill: str) -> Envelope[SkillRolesData]:
        """Tỷ lệ tin entry-level của từng vai trò có nhắc `skill` (#166).

        Cấp bậc cố định là nhóm `entry`. Mỗi vai trò của `config/rules.toml` một dòng, theo thứ tự hiển thị; dưới ngưỡng
        mẫu là `null_data`. `data.mentioned` do nguồn tính. `skill` là mã đã có trong bộ từ vựng (route đã kiểm).

        Raises:
            UnknownCell: nguồn chưa có số cho `skill`, hoặc chưa có snapshot nào đọc được.
        """
        ...

    def posting_check(
        self,
        *,
        role: str,
        level: str,
        have: Collection[str],
        skills: Collection[str],
        facts: PostingFacts,
    ) -> Envelope[PostingCheckData]:
        """Mục `match` của một tin dán trên ô `role` × `level` (FR-28, #230); `market` và `warnings` còn `not_ready` (#125, #126).

        `skills` là mã kỹ năng của tin (đã nằm trong bộ từ vựng, route đã kiểm); `have` là hồ sơ (AD-22, rỗng là không có hồ
        sơ). Nguồn lấy tỷ lệ kỹ năng của ô như `skill_rates` (kể cả quay về ô rộng hơn) rồi đưa qua
        `haido_api.posting_match.build_match`. `facts` là sự kiện đóng của bước một (nhánh, số năm, lương, tên công ty, kênh liên hệ, phí, mô tả công việc, cấp của chức danh, vòng đời tin khớp),
        #240–#246 mới đọc; #230 chỉ lặp lại `branch`.

        Raises:
            UnknownCell: không có ô nào cho `role` × `level`, kể cả sau khi quay về.
            CheckUnavailable: nguồn chưa có số thật (đến #234); 503, không phải 404.
        """
        ...
