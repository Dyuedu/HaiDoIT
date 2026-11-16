"""Phép 4: nhóm kỹ năng theo θ (#101, AD-2, FR-9).

`rate >= theta_core` là CORE, `rate >= theta_common` là COMMON, còn lại RARE. θ nằm trong từng yêu cầu: hàm không đọc
config, nên đổi θ thì nhóm đổi ở lần gọi kế tiếp mà không cần tính lại tỷ lệ. Nhóm không lưu trong bảng; #102 quyết
định θ được ghi và đóng băng ra sao.

Đầu vào sai là `ValueError`, không đoán: θ không hữu hạn hoặc ngoài [0, 1], `theta_common > theta_core`, tỷ lệ
không hữu hạn hoặc ngoài [0, 1], `skill_id` trùng trong một yêu cầu.

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
        for name, theta in (("theta_core", core), ("theta_common", common)):
            if not math.isfinite(theta) or not 0.0 <= theta <= 1.0:
                raise ValueError(f"{name} phải là số hữu hạn trong [0, 1], nhận {theta}.")
        if common > core:
            raise ValueError(f"theta_common ({common}) không được lớn hơn theta_core ({core}).")
        ids = [item.skill_id for item in request.rates]
        duplicated = sorted({i for i in ids if ids.count(i) > 1})
        if duplicated:
            raise ValueError(f"skill_id trùng trong một yêu cầu: {', '.join(map(repr, duplicated))}.")
        groups = []
        for item in request.rates:
            rate = item.rate
            if not math.isfinite(rate) or not 0.0 <= rate <= 1.0:
                raise ValueError(f"Tỷ lệ của {item.skill_id!r} phải nằm trong [0, 1], nhận {rate}.")
            band = SkillBand.CORE if rate >= core else SkillBand.COMMON if rate >= common else SkillBand.RARE
            groups.append(SkillGroup(item.skill_id, band))
        return tuple(groups)

