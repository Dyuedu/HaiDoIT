"""Route bộ từ vựng kỹ năng. Đọc danh sách mồi đã kiểm, không tính gì."""

from fastapi import APIRouter

from haido_api.schemas.error import ErrorEnvelope
from haido_api.schemas.skills import SkillRow, SkillsData, SkillsResponse
from haido_core.vocab.skills import load_seed_skills, seed_version

router = APIRouter(
    prefix="/api/v1",
    tags=["vocabulary"],
    responses={500: {"model": ErrorEnvelope, "description": "Lỗi máy chủ (`internal_error`)."}},
)


@router.get(
    "/skills",
    response_model=SkillsResponse,
    summary="Danh sách kỹ năng để tìm và tick",
)
def get_skills() -> SkillsResponse:
    """Mọi kỹ năng của bộ từ vựng đang dùng, tên song ngữ và bí danh. Web tìm trên danh sách này."""
    rows = [
        SkillRow(code=s.code, name_en=s.name_en, name_vi=s.name_vi, aliases=list(s.aliases))
        for s in load_seed_skills()
    ]
    return SkillsResponse(data=SkillsData(vocab_version=seed_version(), skills=rows))
