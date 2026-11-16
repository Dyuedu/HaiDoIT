"""Route chức danh → vai trò (#150). Chỉ gọi phép 6, không có luật so khớp riêng (AD-2, AD-5).

Nhãn của phép 6 đổi sang mã vai trò bằng `report_as` của `config/classify.toml` rồi `[labels.role]` của
`config/rules.toml`, đúng cách `haido_core/steps/aggregate.py` làm, nên vai trò của màn trùng vai trò của số liệu.
Chức danh chỉ đi qua bộ nhớ: không ghi log, không lặp lại trong response.
"""

from functools import cache
from typing import Annotated

from fastapi import APIRouter, Query
from fastapi.exceptions import RequestValidationError

from haido_api.schemas.error import ErrorEnvelope
from haido_api.schemas.roles import RoleForTitleData, RoleForTitleResponse, TitleMatch
from haido_core.config import load_rules
from haido_core.domain.classify import (
    OTHER_ROLE,
    RuleClassifier,
    default_classify_config,
)
from haido_core.domain.registry import PostingFacts

MAX_TITLE_LEN = 120
"""Chức danh dài nhất nhận, sau khi bỏ khoảng trắng hai đầu."""

router = APIRouter(
    prefix="/api/v1",
    tags=["roles"],
    responses={
        422: {"model": ErrorEnvelope, "description": "Chức danh rỗng hoặc quá dài (`invalid_query`)."},
        500: {"model": ErrorEnvelope, "description": "Lỗi máy chủ (`internal_error`)."},
    },
)


@cache
def _classifier() -> tuple[RuleClassifier, dict[str, str], dict[str, str]]:
    config = default_classify_config()
    return RuleClassifier(config), dict(config.report_as), dict(load_rules().role_codes)


def _invalid() -> RequestValidationError:
    return RequestValidationError(
        [{"type": "value_error", "loc": ("query", "title"), "msg": "title không hợp lệ", "input": None}]
    )


def match_title(title: str) -> RoleForTitleData:
    """Phân loại một chức danh bằng phép 6. Nhãn không có trong `[labels.role]` (ngoài IT) là `not_it`."""
    classifier, report_as, role_codes = _classifier()
    result = classifier.classify(PostingFacts(title, "", None, None, None))
    label = report_as.get(result.role, result.role)  # type: ignore[union-attr]
    code = role_codes.get(label)
    if code is None:
        return RoleForTitleData(status=TitleMatch.NOT_IT, role=None)
    if label == OTHER_ROLE:
        return RoleForTitleData(status=TitleMatch.GENERIC, role=None)
    return RoleForTitleData(status=TitleMatch.MATCHED, role=code)


@router.get(
    "/role-for-title",
    response_model=RoleForTitleResponse,
    summary="Vai trò cho một chức danh",
)
def get_role_for_title(
    title: Annotated[
        str,
        Query(
            max_length=MAX_TITLE_LEN + 64,
            description=(
                f"Chức danh người dùng gõ, ví dụ `Lập trình viên Java`. Tối đa {MAX_TITLE_LEN} ký tự sau khi bỏ "
                "khoảng trắng hai đầu. Không được lưu hay ghi log."
            ),
        ),
    ],
) -> RoleForTitleResponse:
    """Đưa chức danh vào phép 6 và trả vai trò Hải Đồ dùng (FR-18, #150).

    `matched` kèm mã vai trò; `generic` khi chức danh thuộc IT nhưng không chỉ một vai trò (ví dụ `Developer`);
    `not_it` khi chức danh không thuộc IT. Hai trường hợp sau có `role = null`: màn hiện danh sách vai trò để chọn.
    """
    cleaned = title.strip()
    if not cleaned or len(cleaned) > MAX_TITLE_LEN:
        raise _invalid()
    return RoleForTitleResponse(data=match_title(cleaned))
