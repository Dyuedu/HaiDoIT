"""Phép 7: so khớp một cặp tin (#100, AD-2).

Thân hàm duy nhất của `match_postings`. Khớp khi hai tin cùng khóa danh tính và đúng phạm vi.
Phép không xóa tin.
"""

from collections.abc import Sequence

from haido_core.domain.cluster import ClusterMember, identity_key
from haido_core.domain.registry import (
    MatchDecision,
    MatchScope,
    OneOrMany,
    PostingPair,
    as_batch,
)


class PostingMatcher:
    """Một đối tượng trả một quyết định. Một lô trả tuple cùng độ dài."""

    def __init__(self, members: Sequence[ClusterMember], *, source_rank: Sequence[str]) -> None:
        self._members = {member.posting_id: member for member in members}
        if len(self._members) != len(tuple(members)):
            raise ValueError("Mã tin lặp.")
        self._source_rank = tuple(source_rank)

    def match_postings(self, pairs: OneOrMany[PostingPair]) -> OneOrMany[MatchDecision]:
        batch = as_batch(pairs)
        if batch is None:
            return self._one(pairs)
        return tuple(self._one(pair) for pair in batch)

    def _one(self, pair: PostingPair) -> MatchDecision:
        left = self._members.get(pair.left_id)
        right = self._members.get(pair.right_id)
        if left is None or right is None:
            raise ValueError(f"Cặp có mã tin không có: {pair.left_id}, {pair.right_id}.")
        left_key = identity_key(left.company, left.title)
        right_key = identity_key(right.company, right.title)
        same_key = left_key is not None and left_key == right_key
        same_source = left.source.casefold().strip() == right.source.casefold().strip()
        if pair.scope is MatchScope.IN_SOURCE:
            matched = same_key and same_source and left.posting_id != right.posting_id
        elif pair.scope is MatchScope.CROSS_SOURCE:
            matched = same_key and not same_source
        else:
            raise ValueError(f"Phạm vi so khớp không hỗ trợ: {pair.scope}.")
        return MatchDecision(pair.left_id, pair.right_id, matched)
