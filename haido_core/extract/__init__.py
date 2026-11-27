"""Tầng trích xuất dữ kiện qua LLM có dán nhãn và cố vấn lộ trình của Hải Đồ IT."""

from haido_core.extract.advisor import (
    AdvisorGenerationError,
    AdvisorInput,
    AdvisorLlmConfig,
    MarketSkillContext,
    RawAdvisorPlan,
    RawStage,
    RawStageNode,
    build_fallback_plan,
    generate_advisor_roadmap,
    load_advisor_config,
)
from haido_core.extract.cv_parser import UnreadableCvError, extract_document_chars

__all__ = [
    "AdvisorGenerationError",
    "AdvisorInput",
    "AdvisorLlmConfig",
    "MarketSkillContext",
    "RawAdvisorPlan",
    "RawStage",
    "RawStageNode",
    "UnreadableCvError",
    "build_fallback_plan",
    "extract_document_chars",
    "generate_advisor_roadmap",
    "load_advisor_config",
]
