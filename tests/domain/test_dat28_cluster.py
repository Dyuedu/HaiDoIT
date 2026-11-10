"""#100 — gộp tin trùng chéo nguồn thành cụm và chọn đại diện."""

from datetime import date

import pytest

from haido_core.domain.cluster import ClusterMember, collapse_clusters, identity_key
from haido_core.domain.matching import PostingMatcher
from haido_core.domain.population import ClusterPopulation, CountedPosting
from haido_core.domain.registry import (
    CellKey,
    MatchDecision,
    MatchScope,
    PopulationRequest,
    PostingPair,
)

RANK = ("itviec", "topdev", "topcv")
S = date(2026, 11, 10)


def _tin(
    posting_id: str,
    source: str,
    *,
    company: str | None = "FPT",
    title: str | None = "Backend Dev",
    url: str = "https://example.test/a",
    location: str | None = None,
    experience: str | None = None,
    level: str | None = None,
) -> ClusterMember:
    return ClusterMember(posting_id, source, url, company, title, location, experience, level)


def test_dat28_cong_ty_phap_ly_va_chuc_danh_co_dau_cau_cung_khoa() -> None:
    left = identity_key("Công ty TNHH FPT", "Java-Backend")
    right = identity_key("FPT", "Java Backend")
    assert left is not None
    assert left == right


def test_dat28_fpt_software_khac_fpt() -> None:
    assert identity_key("FPT Software", "Backend Dev") != identity_key("FPT", "Backend Dev")


def test_dat28_thieu_cong_ty_hoac_chuc_danh_thi_khong_co_khoa() -> None:
    assert identity_key(None, "Backend Dev") is None
    assert identity_key("FPT", "   ") is None


def test_dat28_hai_nguon_cung_khoa_la_mot_cum_va_dan_so_la_mot() -> None:
    clusters = collapse_clusters(
        [_tin("1", "itviec", url="https://itviec.test/1"), _tin("2", "topcv", url="https://topcv.test/2")],
        source_rank=RANK,
    )
    assert len(clusters) == 1
    assert clusters[0].member_ids == ("1", "2")
    pop = ClusterPopulation([CountedPosting(clusters[0].cluster_id, S, "backend", "da_nang", "unknown")])
    key = CellKey(S.isoformat(), "backend", None, None, "vn")
    assert pop.population(PopulationRequest(key, 60)) == 1


def test_dat28_thieu_khoa_van_la_cum_rieng_khong_bi_xoa() -> None:
    clusters = collapse_clusters(
        [_tin("1", "itviec", company=None), _tin("2", "topcv", company=None, title="Backend Dev")],
        source_rank=RANK,
    )
    assert len(clusters) == 2
    assert {item.representative_id for item in clusters} == {"1", "2"}


def test_dat28_hang_nguon_thang_so_truong() -> None:
    sparse = _tin("iv", "itviec", url="https://itviec.test/1", location=None)
    rich = _tin(
        "tc",
        "topcv",
        url="https://topcv.test/1",
        location="Hà Nội",
        experience="3 năm",
        level="Senior",
    )
    clusters = collapse_clusters([rich, sparse], source_rank=RANK)
    assert clusters[0].representative_id == "iv"


def test_dat28_cung_hang_thi_nhieu_truong_thang() -> None:
    thin = _tin("a", "topcv", url="https://topcv.test/a")
    thick = _tin("b", "topcv", url="https://topcv.test/b", location="Hà Nội", level="Senior")
    clusters = collapse_clusters([thin, thick], source_rank=RANK)
    assert clusters[0].representative_id == "b"


def test_dat28_cung_hang_va_cung_so_truong_thi_url_co_gia_tri_roi_a_z() -> None:
    empty = _tin("1", "topcv", url="")
    later = _tin("2", "topcv", url="https://z.test/2")
    earlier = _tin("3", "topcv", url="https://a.test/3")
    clusters = collapse_clusters([empty, later, earlier], source_rank=RANK)
    assert clusters[0].representative_id == "3"


def test_dat28_dao_thu_tu_dau_vao_khong_doi_dai_dien_hay_cum() -> None:
    members = [
        _tin("1", "itviec", url="https://itviec.test/1", location="Đà Nẵng"),
        _tin("2", "topcv", url="https://topcv.test/2", location="Hà Nội", level="Senior"),
    ]
    forward = collapse_clusters(members, source_rank=RANK)
    backward = collapse_clusters(list(reversed(members)), source_rank=RANK)
    assert forward == backward


def test_dat28_match_postings_cheo_nguon_va_trong_nguon() -> None:
    matcher = PostingMatcher(
        [
            _tin("1", "itviec"),
            _tin("2", "topcv"),
            _tin("3", "itviec", title="QA Tester"),
            _tin("4", "itviec", company=None),
        ],
        source_rank=RANK,
    )
    assert matcher.match_postings(PostingPair("1", "2", MatchScope.CROSS_SOURCE)).matched is True
    assert matcher.match_postings(PostingPair("1", "2", MatchScope.IN_SOURCE)).matched is False
    assert matcher.match_postings(PostingPair("1", "3", MatchScope.IN_SOURCE)).matched is False
    same = PostingMatcher(
        [_tin("5", "itviec", url="https://itviec.test/5"), _tin("6", "itviec", url="https://itviec.test/6")],
        source_rank=RANK,
    )
    assert same.match_postings(PostingPair("5", "6", MatchScope.IN_SOURCE)).matched is True
    assert same.match_postings(PostingPair("5", "6", MatchScope.CROSS_SOURCE)).matched is False
    assert matcher.match_postings(PostingPair("1", "4", MatchScope.CROSS_SOURCE)).matched is False


def test_dat28_mot_cap_tra_quyet_dinh_va_lo_tra_tuple() -> None:
    matcher = PostingMatcher([_tin("1", "itviec"), _tin("2", "topcv")], source_rank=RANK)
    one = matcher.match_postings(PostingPair("1", "2", MatchScope.CROSS_SOURCE))
    assert isinstance(one, MatchDecision)
    batch = matcher.match_postings(
        [
            PostingPair("1", "2", MatchScope.CROSS_SOURCE),
            PostingPair("1", "2", MatchScope.IN_SOURCE),
        ]
    )
    assert batch == (one, matcher.match_postings(PostingPair("1", "2", MatchScope.IN_SOURCE)))


def test_dat28_ma_tin_khong_co_thi_bao_loi() -> None:
    matcher = PostingMatcher([_tin("1", "itviec")], source_rank=RANK)
    with pytest.raises(ValueError, match="1"):
        matcher.match_postings(PostingPair("1", "khong-co", MatchScope.CROSS_SOURCE))
