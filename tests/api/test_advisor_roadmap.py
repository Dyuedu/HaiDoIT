"""TDD cho POST /api/v1/advisor/roadmap: upload CV trong bộ nhớ + role + level + JD + LLM -> roadmap.sh Envelope."""

from __future__ import annotations

import io
import json
import zipfile
from typing import Any

import httpx
import pytest

from haido_api.fake_market import FakeMarket
from haido_api.main import create_app


def _docx_bytes(paragraphs: list[str]) -> bytes:
    body = "".join(f"<w:p><w:r><w:t>{p}</w:t></w:r></w:p>" for p in paragraphs)
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{body}</w:body></w:document>"
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("word/document.xml", xml.encode("utf-8"))
    return buf.getvalue()


def _minimal_pdf(text: str) -> bytes:
    safe = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = f"BT\n/F1 12 Tf\n72 720 Td\n({safe}) Tj\nET\n".encode("latin-1")
    objs = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n",
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
        f"5 0 obj\n<< /Length {len(stream)} >>\nstream\n".encode("ascii") + stream + b"endstream\nendobj\n",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offs = [0]
    for obj in objs:
        offs.append(len(out))
        out.extend(obj)
    xref = len(out)
    out.extend(f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode("ascii"))
    for off in offs[1:]:
        out.extend(f"{off:010d} 00000 n \n".encode("ascii"))
    out.extend(f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii"))
    return bytes(out)


async def _post_roadmap(
    app: Any,
    *,
    filename: str = "cv.docx",
    content: bytes | None = None,
    content_type: str = "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    data: dict[str, str] | None = None,
) -> httpx.Response:
    raw = content if content is not None else _docx_bytes(
        ["Ứng viên Backend với kinh nghiệm Python, SQL, Git, Docker và REST API."]
    )
    fields = data if data is not None else {"role": "backend", "level": "entry", "consent": "true"}
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.post(
            "/api/v1/advisor/roadmap",
            files={"cv": (filename, raw, content_type)},
            data=fields,
        )


@pytest.mark.anyio
async def test_advisor_roadmap_tao_lo_trinh_tu_cv_va_jd_offline_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HAIDO_ADVISOR_MODE", "offline")
    fake = FakeMarket()
    app = create_app(
        {
            "city_shares": fake,
            "skill_rates": fake,
            "newcomer_roles": fake,
            "learning_path": fake,
            "skill_roles": fake,
            "posting_check": fake,
        }
    )
    resp = await _post_roadmap(app)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert set(body) == {"data", "meta"}
    data = body["data"]
    assert data["generation_mode"] == "market_fallback"
    assert "sql" in data["cv_skills"]
    assert "git" in data["cv_skills"]
    path = data["path"]
    assert path["role"] == "backend"
    assert path["level"] == "entry"
    assert path["status"] == "ready"
    assert len(path["stages"]) >= 2
    assert path["have_on_path"] >= 1
    assert path["cell_id"] in body["meta"]["cells"]
    assert path["entry_cell_id"] in body["meta"]["cells"]


@pytest.mark.anyio
async def test_advisor_roadmap_dung_llm_va_gan_ty_le_jd_that_theo_role_level(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, str] = {}

    def fake_llm(system_prompt: str, user_prompt: str) -> str:
        captured["system"] = system_prompt
        captured["user"] = user_prompt
        return json.dumps(
            {
                "cv_skills": ["python", "sql"],
                "advisor_summary": "CV đã có Python và SQL, cần học thêm PyTorch cho hướng AI/ML.",
                "stages": [
                    {
                        "title": "Nền tảng ngôn ngữ & dữ liệu",
                        "choose_one": False,
                        "skills": [
                            {
                                "skill": "python",
                                "prerequisite_for": ["pytorch"],
                                "blurb": "Ngôn ngữ trung tâm cho hệ thống AI/ML.",
                                "resource_title": "Python Docs",
                                "resource_url": "https://docs.python.org/3/",
                            },
                            {
                                "skill": "sql",
                                "prerequisite_for": [],
                                "blurb": "Truy vấn dữ liệu phục vụ huấn luyện mô hình.",
                                "resource_title": "SQLBolt",
                                "resource_url": "https://sqlbolt.com/",
                            },
                        ],
                    },
                    {
                        "title": "Deep Learning & Triển khai",
                        "choose_one": False,
                        "skills": [
                            {
                                "skill": "pytorch",
                                "prerequisite_for": [],
                                "blurb": "Framework học sâu phổ biến.",
                                "resource_title": "PyTorch Tutorials",
                                "resource_url": "https://pytorch.org/tutorials/",
                            }
                        ],
                    },
                ],
            }
        )

    monkeypatch.setenv("HAIDO_ADVISOR_MODE", "llm")
    monkeypatch.setenv("HAIDO_LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr("haido_api.advisor_service._default_llm_caller", lambda _cfg: fake_llm)

    fake = FakeMarket()
    app = create_app(
        {
            "city_shares": fake,
            "skill_rates": fake,
            "newcomer_roles": fake,
            "learning_path": fake,
            "skill_roles": fake,
            "posting_check": fake,
        }
    )
    resp = await _post_roadmap(
        app,
        filename="cv.pdf",
        content=_minimal_pdf("AI Engineer CV with Python, SQL and data pipelines."),
        content_type="application/pdf",
        data={"role": "ai_ml", "level": "entry", "consent": "true"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["data"]["generation_mode"] == "llm"
    assert body["data"]["path"]["role"] == "ai_ml"
    assert body["data"]["path"]["level"] == "entry"
    assert "AI/ML" in captured["user"]
    assert "ty_le_jd=" in captured["user"]
    # Tỷ lệ của python trên lộ trình phải khớp đúng FakeMarket.skill_rates("ai_ml", "entry")
    rates_env = fake.skill_rates(role="ai_ml", level="entry")
    python_rate = next(r.rate.value for r in rates_env.data.rows if r.skill == "python")
    path_python = next(
        s for st in body["data"]["path"]["stages"] for s in st["skills"] if s["skill"] == "python"
    )
    assert path_python["rate"]["value"] == python_rate
    assert path_python["have"] is True


@pytest.mark.anyio
async def test_advisor_roadmap_chan_khi_chua_dong_y_hoac_cv_scan(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HAIDO_ADVISOR_MODE", "offline")
    fake = FakeMarket()
    app = create_app(
        {
            "city_shares": fake,
            "skill_rates": fake,
            "newcomer_roles": fake,
            "learning_path": fake,
            "skill_roles": fake,
            "posting_check": fake,
        }
    )
    no_consent = await _post_roadmap(app, data={"role": "backend", "level": "entry", "consent": "false"})
    assert no_consent.status_code == 400
    assert no_consent.json()["error"]["code"] == "cv_consent_required"

    scanned = await _post_roadmap(
        app,
        filename="scan.pdf",
        content=_minimal_pdf("CV"),
        content_type="application/pdf",
    )
    assert scanned.status_code == 422
    assert scanned.json()["error"]["code"] == "cv_unreadable"
    assert "Word, Canva hoặc Overleaf" in scanned.json()["error"]["message"]
