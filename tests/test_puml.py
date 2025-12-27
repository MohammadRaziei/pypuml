from pathlib import Path

from pypuml import puml_to_mermaid, puml_to_svg


def test_puml_to_mermaid_simple_graph():
    puml = """
    @startuml
    Alice -> Bob: Hello
    Bob -> Carol
    @enduml
    """

    assert (
        puml_to_mermaid(puml)
        == "graph TD\nAlice -->|Hello| Bob\nBob --> Carol"
    )


def test_puml_to_svg_uses_mermaid_converter(monkeypatch, tmp_path):
    captured = {}

    class DummyConverter:
        def __init__(self, timeout=30):
            captured["timeout"] = timeout

        def to_svg(self, input_file: Path, output_file=None):
            captured["content"] = input_file.read_text()
            captured["output_file"] = output_file
            if output_file is None:
                return "<svg>ok</svg>"
            return None

    monkeypatch.setattr("pypuml.core.MermaidConverter", DummyConverter)

    output_path = tmp_path / "diagram.svg"
    result = puml_to_svg("A -> B", output_file=output_path, timeout=10)

    assert result is None
    assert captured["timeout"] == 10
    assert captured["output_file"] == output_path
    assert captured["content"] == "graph TD\nA --> B"


def test_puml_to_mermaid_from_file(tmp_path):
    puml_path = tmp_path / "diagram.puml"
    puml_path.write_text("@startuml\nA -> B: Hi\n@enduml\n")

    puml = puml_path.read_text()

    assert puml_to_mermaid(puml) == "graph TD\nA -->|Hi| B"


def test_puml_to_svg_writes_svg_file(monkeypatch, tmp_path):
    class DummyConverter:
        def __init__(self, timeout=30):
            self.timeout = timeout

        def to_svg(self, input_file: Path, output_file=None):
            svg = f"<svg>{input_file.read_text()}</svg>"
            if output_file is None:
                return svg
            output_file.write_text(svg)
            return None

    monkeypatch.setattr("pypuml.core.MermaidConverter", DummyConverter)

    output_path = tmp_path / "diagram.svg"
    result = puml_to_svg("A -> B", output_file=output_path)

    assert result is None
    assert output_path.read_text() == "<svg>graph TD\nA --> B</svg>"
