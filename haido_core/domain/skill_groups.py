"""Phép 4: nhóm kỹ năng theo θ (#101, AD-2, FR-9).

`rate >= theta_core` là CORE, `rate >= theta_common` là COMMON, còn lại RARE. θ nằm trong từng yêu cầu: hàm không đọc
config, nên đổi θ thì nhóm đổi ở lần gọi kế tiếp mà không cần tính lại tỷ lệ. Nhóm không lưu trong bảng; #102 quyết
định θ được ghi và đóng băng ra sao.

Kết quả giữ thứ tự đầu vào và gồm cả kỹ năng tỷ lệ 0 nếu người gọi đưa vào. Module chỉ import registry.
"""

import math

from haido_core.domain.registry import (
    OneOrMany,
    SkillBand,
    SkillGroup,
    SkillGroupRequest,
    as_batch,
)


class SkillGrouper:
    """Thân hàm duy nhất của phép 4."""

    def group_skills(self, requests: OneOrMany[SkillGroupRequest]) -> OneOrMany[tuple[SkillGroup, ...]]:
        batch = as_batch(requests)
        if batch is None:
            return self._one(requests)  # type: ignore[arg-type]
        return tuple(self._one(item) for item in batch)

    def _one(self, request: SkillGroupRequest) -> tuple[SkillGroup, ...]:
        core, common = request.theta_core, request.theta_common
        if common > core:
            raise ValueError(f"theta_common ({common}) không được lớn hơn theta_core ({core}).")
        groups = []
        for item in request.rates:
            rate = item.rate
            if math.isnan(rate) or not 0.0 <= rate <= 1.0:
                raise ValueError(f"Tỷ lệ của {item.skill_id!r} phải nằm trong [0, 1], nhận {rate}.")
            band = SkillBand.CORE if rate >= core else SkillBand.COMMON if rate >= common else SkillBand.RARE
            groups.append(SkillGroup(item.skill_id, band))
        return tuple(groups)

