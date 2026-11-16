"""AD-17, AD-22 — danh sách trường được dấu `Ordinal` (số thứ tự và số đếm của response, #212).

Thêm một trường `Ordinal` mới là mở thêm một lỗ trong luật "mọi số là Stat". Test này khóa tập đó: thêm trường thì phải
sửa danh sách ở đây và giải thích trong `docs/api/envelope-meta.md`.
"""

import types
from typing import Annotated, Union, get_args, get_origin

from pydantic import BaseModel

from haido_api.routes import market, skills
from haido_core.domain.envelope import OrdinalRef

ALLOWED = {
    "PathStage.stage",
    "LearningPathData.current_stage",
    "LearningPathData.have_on_path",
    "LearningPathData.path_size",
}


def _carries_ordinal(annotation: object) -> bool:
    if isinstance(annotation, OrdinalRef):
        return True
    return any(_carries_ordinal(arg) for arg in get_args(annotation))


def _models_in(annotation: object) -> list[type[BaseModel]]:
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return [annotation]
    origin = get_origin(annotation)
    if origin is Annotated or origin in (Union, types.UnionType) or origin is not None:
        return [m for arg in get_args(annotation) for m in _models_in(arg)]
    return []


def _collect(
    model: type[BaseModel], seen: set[type[BaseModel]], found: set[str]
) -> None:
    if model in seen:
        return
    seen.add(model)
    for name, info in model.model_fields.items():
        if any(isinstance(m, OrdinalRef) for m in info.metadata) or _carries_ordinal(
            info.annotation
        ):
            found.add(f"{model.__name__}.{name}")
        for inner in _models_in(info.annotation):
            _collect(inner, seen, found)


def test_ad17_chi_nhung_truong_trong_danh_sach_mang_dau_ordinal() -> None:
    found: set[str] = set()
    seen: set[type[BaseModel]] = set()
    checked = 0
    for route in [*market.router.routes, *skills.router.routes]:
        model = getattr(route, "response_model", None)
        if not (isinstance(model, type) and issubclass(model, BaseModel)):
            continue
        checked += 1
        _collect(model, seen, found)
    assert checked >= 4, "không tìm thấy route nào có response_model"
    assert found == ALLOWED, sorted(found ^ ALLOWED)
