"""TDD cho haido_core.extract.advisor: trích kỹ năng CV + tổng hợp lộ trình roadmap.sh từ JD và LLM."""

from haido_core.extract.advisor import (
    AdvisorInput,
    AdvisorLlmConfig,
    MarketSkillContext,
    generate_advisor_roadmap,
)
from haido_core.vocab.skills import load_seed_skills


def _sample_market_skills() -> tuple[MarketSkillContext, ...]:
    return (
        MarketSkillContext(code="java", name_en="Java", name_vi="Java", rate=0.68, group="core"),
        MarketSkillContext(code="sql", name_en="SQL", name_vi="SQL", rate=0.62, group="core"),
        MarketSkillContext(code="spring_boot", name_en="Spring Boot", name_vi="Spring Boot", rate=0.54, group="core"),
        MarketSkillContext(code="docker", name_en="Docker", name_vi="Docker", rate=0.35, group="core"),
        MarketSkillContext(code="redis", name_en="Redis", name_vi="Redis", rate=0.22, group="common"),
        MarketSkillContext(code="kubernetes", name_en="Kubernetes", name_vi="Kubernetes", rate=0.14, group="common"),
    )


def _sample_input(doc: str = "Kinh nghiệm Java, SQL, Git và PostgreSQL. Đã làm REST API.") -> AdvisorInput:
    return AdvisorInput(
        document_chars=doc,
        role="backend",
        role_label="Backend",
        level="mid",
        level_label="Mid",
        market_skills=_sample_market_skills(),
        vocab=load_seed_skills(),
        known_have=("git",),
    )


def test_advisor_offline_fallback_trich_ky_nang_va_dung_lo_trinh_cho_moi_vai_tro_cap_bac() -> None:
    inp = AdvisorInput(
        document_chars="Tôi biết Python, SQL và học máy cơ bản qua đồ án đại học.",
        role="ai_ml",
        role_label="AI/ML",
        level="junior",
        level_label="Junior",
        market_skills=(
            MarketSkillContext(code="python", name_en="Python", name_vi="Python", rate=0.82, group="core"),
            MarketSkillContext(code="machine_learning", name_en="Machine Learning", name_vi="Học máy", rate=0.61, group="core"),
            MarketSkillContext(code="pytorch", name_en="PyTorch", name_vi="PyTorch", rate=0.42, group="core"),
            MarketSkillContext(code="docker", name_en="Docker", name_vi="Docker", rate=0.24, group="common"),
        ),
        vocab=load_seed_skills(),
        known_have=(),
    )
    plan = generate_advisor_roadmap(inp, config=AdvisorLlmConfig(mode="offline"))
    assert plan.generation_mode == "market_fallback"
    assert "python" in plan.cv_skills
    assert "sql" in plan.cv_skills
    assert "machine_learning" in plan.cv_skills
    assert len(plan.stages) >= 1
    skills_in_stages = [n.skill for st in plan.stages for n in st.skills]
    assert "python" in skills_in_stages
    assert "pytorch" in skills_in_stages
    assert "AI/ML" in plan.advisor_summary
    assert "Junior" in plan.advisor_summary


def test_advisor_llm_mock_hau_kiem_ma_ky_nang_chu_trinh_url_va_tu_cam() -> None:
    def fake_caller(_system: str, _user: str) -> str:
        return """```json
{
  "cv_skills": ["java", "unknown_fake_skill", "sql"],
  "advisor_summary": "Bạn đã có nền tảng Java và SQL. Đừng học Docker vội.",
  "stages": [
    {
      "title": "Nền tảng cốt lõi",
      "choose_one": true,
      "skills": [
        {
          "skill": "java",
          "prerequisite_for": ["spring_boot", "java"],
          "blurb": "Ngôn ngữ chính để phát triển hệ thống backend.",
          "resource_title": "Dev.java",
          "resource_url": "http://insecure.example.com"
        }
      ]
    },
    {
      "title": "Framework & Triển khai",
      "choose_one": false,
      "skills": [
        {
          "skill": "spring_boot",
          "prerequisite_for": ["java", "docker"],
          "blurb": "Framework phổ biến cho dịch vụ Java. Nên học ngay.",
          "resource_title": "Spring Guides",
          "resource_url": "https://spring.io/guides"
        },
        {
          "skill": "docker",
          "prerequisite_for": [],
          "blurb": "Đừng học nếu không thích, hoặc bỏ qua một kỹ năng này.",
          "resource_title": "Docker Docs",
          "resource_url": "https://docs.docker.com/get-started/"
        },
        {
          "skill": "invalid_skill_xyz",
          "prerequisite_for": [],
          "blurb": "Không hợp lệ",
          "resource_title": "Bad",
          "resource_url": "https://example.com"
        }
      ]
    }
  ]
}
```"""

    plan = generate_advisor_roadmap(
        _sample_input(),
        config=AdvisorLlmConfig(mode="llm", provider="anthropic", api_key="test-key"),
        llm_caller=fake_caller,
    )
    assert plan.generation_mode == "llm"
    assert plan.cv_skills == ["java", "sql"]
    assert "đừng học" not in plan.advisor_summary.casefold()
    # Chặng 1 chỉ còn 1 kỹ năng hợp lệ -> choose_one tự tắt thành False
    assert plan.stages[0].choose_one is False
    # Mã lạ bị loại
    all_codes = [s.skill for st in plan.stages for s in st.skills]
    assert "invalid_skill_xyz" not in all_codes
    assert all_codes == ["java", "spring_boot", "docker"]
    # Kiểm tra cạnh tiên quyết chỉ đi sang chặng SAU (chặn tự trỏ và trỏ ngược chặng)
    assert plan.stages[0].skills[0].prerequisite_for == ["spring_boot"]
    assert plan.stages[1].skills[0].prerequisite_for == []  # docker cùng chặng 2 nên bị loại khỏi prerequisite_for
    # Link http không an toàn bị đổi sang https hợp lệ
    assert plan.stages[0].skills[0].resource_url.startswith("https://")
    # Câu cấm bị lọc
    assert "đừng học" not in plan.stages[1].skills[1].blurb.casefold()
    assert "bỏ qua một kỹ năng" not in plan.stages[1].skills[1].blurb.casefold()
