from dataclasses import dataclass, field
from datetime import date


@dataclass
class VersionRecord:
    version_id: int
    doc_id: int
    version: str
    status: str = "UPLOADED"
    content_hash: str | None = None
    changelog: str | None = None


@dataclass
class SegmentRecord:
    segment_id: int
    doc_id: int
    version_id: int
    text: str
    chunk_order: int
    metadata: dict[str, object] = field(default_factory=dict)
    status: str = "STORED"
    deleted: bool = False


@dataclass
class DocumentRecord:
    doc_id: int
    title: str
    status: str = "INIT"
    accessible_by: str = "VISITOR"
    expire_date: date | None = None
    current_version_id: int | None = None
    versions: list[VersionRecord] = field(default_factory=list)
    segments: list[SegmentRecord] = field(default_factory=list)


class DocumentStore:
    def __init__(self) -> None:
        self.documents: dict[int, DocumentRecord] = {}
        self._next_doc = 1
        self._next_version = 1
        self._next_segment = 1

    def create(self, title: str, accessible_by: str = "VISITOR") -> DocumentRecord:
        record = DocumentRecord(self._next_doc, title, accessible_by=accessible_by)
        self.documents[record.doc_id] = record
        self._next_doc += 1
        return record

    def add_version(self, record: DocumentRecord, content_hash: str | None = None, changelog: str | None = None) -> VersionRecord:
        version = VersionRecord(self._next_version, record.doc_id, f"{len(record.versions) + 1}.0.0", content_hash=content_hash, changelog=changelog)
        record.versions.append(version)
        record.status = version.status
        self._next_version += 1
        return version

    def activate_version(self, doc_id: int, version_id: int) -> DocumentRecord:
        record = self.documents[doc_id]
        selected = next(version for version in record.versions if version.version_id == version_id)
        for version in record.versions:
            version.status = "STORED" if version.version_id == version_id else "DEACTIVATED"
        selected.status = "VECTOR_STORED"
        record.current_version_id = version_id
        record.status = "VECTOR_STORED"
        return record

    def deactivate_version(self, doc_id: int, version_id: int) -> DocumentRecord:
        record = self.documents[doc_id]
        for version in record.versions:
            if version.version_id == version_id:
                version.status = "DEACTIVATED"
        if record.current_version_id == version_id:
            record.current_version_id = None
            record.status = "CONVERTED"
        return record

    def add_segment(self, record: DocumentRecord, version_id: int, text: str, metadata: dict[str, object] | None = None) -> SegmentRecord:
        segment = SegmentRecord(self._next_segment, record.doc_id, version_id, text, len(record.segments), metadata or {})
        record.segments.append(segment)
        self._next_segment += 1
        return segment
