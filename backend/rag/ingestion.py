"""
Stage 1: Data Ingestion Module
Extracts raw text, headings, and tables from source datasets (.docx / text).
"""

import os
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DocumentSection:
    heading: str
    body_lines: list[str] = field(default_factory=list)
    tables: list[list[list[str]]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RawDocument:
    source_path: str
    filename: str
    sections: list[DocumentSection] = field(default_factory=list)
    raw_text: str = ""


class DocxIngestor:
    """Ingests and parses Microsoft Word (.docx) dataset files."""

    XML_NAMESPACE = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

    def __init__(self, search_paths: list[Path] | None = None):
        if search_paths is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            self.search_paths = [
                base_dir / "data" / "Innovate_AI_Hackathon_Rulebook_DataSet.docx",
                base_dir / "data" / "rulebook_dataset.docx",
                base_dir / "Innovate_AI_Hackathon_Rulebook_DataSet.docx",
            ]
        else:
            self.search_paths = search_paths

    def find_dataset_file(self) -> Path | None:
        for path in self.search_paths:
            if path.is_file():
                return path
        return None

    def ingest(self, file_path: str | Path | None = None) -> RawDocument:
        target_path = Path(file_path) if file_path else self.find_dataset_file()
        if not target_path or not target_path.is_file():
            print(f"[Ingestion Warning] No source file found at {target_path}. Using fallback document structure.")
            return RawDocument(source_path="none", filename="none")

        paragraphs: list[str] = []
        try:
            with zipfile.ZipFile(target_path) as docx_zip:
                xml_content = docx_zip.read("word/document.xml")
                tree = ET.fromstring(xml_content)
                for p in tree.iter(f"{{{self.XML_NAMESPACE['w']}}}p"):
                    texts = [node.text for node in p.iter(f"{{{self.XML_NAMESPACE['w']}}}t") if node.text]
                    if texts:
                        line = "".join(texts).strip()
                        if line:
                            paragraphs.append(line)
        except Exception as exc:
            print(f"[Ingestion Error] Failed to parse {target_path}: {exc}")

        raw_text = "\n".join(paragraphs)
        sections = self._parse_sections(paragraphs)

        return RawDocument(
            source_path=str(target_path),
            filename=target_path.name,
            sections=sections,
            raw_text=raw_text,
        )

    def _parse_sections(self, paragraphs: list[str]) -> list[DocumentSection]:
        sections: list[DocumentSection] = []
        current_section = DocumentSection(heading="Introduction")

        for p in paragraphs:
            # Check if paragraph looks like a section header (e.g. "Section 1.1", "1. Overview", "Appendix")
            if any(p.startswith(prefix) for prefix in ["Section ", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.", "Appendix", "Table "]):
                if current_section.body_lines:
                    sections.append(current_section)
                current_section = DocumentSection(heading=p)
            else:
                current_section.body_lines.append(p)

        if current_section.body_lines:
            sections.append(current_section)

        return sections
