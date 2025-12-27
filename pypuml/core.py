from __future__ import annotations

from pathlib import Path
import tempfile
from typing import Optional, Sequence, TypeVar

from mmdc import MermaidConverter

T = TypeVar("T")


def cat(arr1: Sequence[T], arr2: Sequence[T]) -> list[T]:
    return list(arr1) + list(arr2)


def _format_node(node: str) -> str:
    trimmed = node.strip()
    if " " in trimmed:
        return f'"{trimmed}"'
    return trimmed


def puml_to_mermaid(puml: str) -> str:
    lines = [line.strip() for line in puml.splitlines()]
    mermaid_lines = ["graph TD"]

    for line in lines:
        if not line or line.startswith("'"):
            continue
        if line.startswith("@startuml") or line.startswith("@enduml"):
            continue
        if "->" not in line:
            continue

        left, right = line.split("->", 1)
        source = _format_node(left)
        if ":" in right:
            target_part, label = right.split(":", 1)
            target = _format_node(target_part)
            label = label.strip()
            mermaid_lines.append(f"{source} -->|{label}| {target}")
        else:
            target = _format_node(right)
            mermaid_lines.append(f"{source} --> {target}")

    return "\n".join(mermaid_lines)


def puml_to_svg(puml: str, output_file: Optional[Path] = None, timeout: int = 30) -> Optional[str]:
    mermaid = puml_to_mermaid(puml)
    converter = MermaidConverter(timeout=timeout)

    if output_file is not None:
        output_file = Path(output_file)

    with tempfile.TemporaryDirectory() as tmp_dir:
        mermaid_path = Path(tmp_dir) / "diagram.mmd"
        mermaid_path.write_text(mermaid)
        return converter.to_svg(mermaid_path, output_file=output_file)
