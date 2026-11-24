from dataclasses import dataclass, field
import re
from typing import Iterable


@dataclass(frozen=True)
class SegmentPart:
    text: str
    order: int
    metadata: dict[str, object] = field(default_factory=dict)


def split_length(text: str, max_length: int = 800, overlap: int = 0) -> list[SegmentPart]:
    if max_length <= 0 or overlap < 0 or overlap >= max_length:
        raise ValueError("max_length must be positive and overlap must be smaller than max_length")
    result: list[SegmentPart] = []
    start = 0
    order = 0
    while start < len(text):
        end = min(len(text), start + max_length)
        result.append(SegmentPart(text[start:end], order))
        order += 1
        if end == len(text):
            break
        start = end - overlap
    return result


def split_regex(text: str, pattern: str, *, keep_separator: bool = False) -> list[SegmentPart]:
    if not pattern:
        raise ValueError("pattern is required")
    pieces = re.split(f"({pattern})" if keep_separator else pattern, text)
    return [SegmentPart(piece.strip(), index) for index, piece in enumerate(pieces) if piece and piece.strip()]


def split_markdown_parent_child(text: str, max_length: int = 1200) -> list[SegmentPart]:
    headings = list(re.finditer(r"(?m)^(#{1,6})\s+(.+?)\s*$", text))
    if not headings:
        return split_length(text, max_length)
    result: list[SegmentPart] = []
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        section = text[heading.start():end].strip()
        parent = heading.group(2).strip()
        result.append(SegmentPart(section, len(result), {"parent_heading": parent, "is_parent": True}))
        for child_index, part in enumerate(split_length(section, max_length)):
            metadata = {"parent_heading": parent, "child_index": child_index, "is_parent": False, "parent_generated": True}
            result.append(SegmentPart(part.text, len(result), metadata))
    return result


def split_markdown_sibling(text: str, max_length: int = 1200, sibling_window: int = 1) -> list[SegmentPart]:
    base = split_markdown_parent_child(text, max_length)
    result: list[SegmentPart] = []
    for index, part in enumerate(base):
        siblings = [base[pos].text for pos in range(max(0, index - sibling_window), min(len(base), index + sibling_window + 1)) if pos != index]
        metadata = dict(part.metadata)
        metadata["sibling_indices"] = [pos for pos in range(max(0, index - sibling_window), min(len(base), index + sibling_window + 1)) if pos != index]
        metadata["sibling_context"] = siblings
        result.append(SegmentPart(part.text, index, metadata))
    return result


def split_excel_rows(rows: Iterable[Iterable[object]], max_rows: int = 50) -> list[SegmentPart]:
    materialized = [list(row) for row in rows]
    if not materialized:
        return []
    headers = [str(value) for value in materialized[0]]
    result: list[SegmentPart] = []
    for offset in range(1, len(materialized), max_rows):
        chunk_rows = materialized[offset:offset + max_rows]
        lines = [" | ".join(f"{header}: {value}" for header, value in zip(headers, row, strict=False)) for row in chunk_rows]
        result.append(SegmentPart("\n".join(lines), len(result), {"headers": headers, "row_start": offset, "row_count": len(chunk_rows)}))
    return result


def split_smart(text: str, max_length: int = 1200) -> list[SegmentPart]:
    if re.search(r"(?m)^#{1,6}\s+", text):
        return split_markdown_sibling(text, max_length)
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    result: list[SegmentPart] = []
    buffer = ""
    for paragraph in paragraphs:
        candidate = f"{buffer}\n\n{paragraph}".strip() if buffer else paragraph
        if buffer and len(candidate) > max_length:
            result.append(SegmentPart(buffer, len(result)))
            buffer = paragraph
        else:
            buffer = candidate
    if buffer:
        result.append(SegmentPart(buffer, len(result)))
    return result or split_length(text, max_length)
