"""Phép 1: lượt nhắc → mã kỹ năng qua từ vựng song ngữ (AD-2, #283).

Tra bằng khóa đã bỏ dấu của tên và bí danh. Chuỗi không có trong từ vựng ra `skill_id = None`; không đoán mã.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from haido_core.domain.posting_text import fold
from haido_core.domain.registry import MappedMention, Mention, OneOrMany, as_batch

if TYPE_CHECKING:
    from haido_core.vocab.skills import Vocabulary


class VocabularyMapper:
    """Một thân hàm của phép 1."""

    def __init__(self, vocab: Vocabulary) -> None:
        self.vocab = vocab

    def map_mentions(self, mentions: OneOrMany[Mention]) -> OneOrMany[MappedMention]:
        batch = as_batch(mentions)
        if batch is None:
            return self._one(mentions)  # type: ignore[arg-type]
        return tuple(self._one(item) for item in batch)

    def _one(self, mention: Mention) -> MappedMention:
        return MappedMention(mention.text, self.vocab.lookup.get(fold(mention.text)))
