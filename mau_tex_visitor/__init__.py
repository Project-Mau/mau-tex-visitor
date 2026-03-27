import re
from importlib.resources import files

from mau.environment.environment import Environment
from mau.nodes.node import Node
from mau.visitors.jinja_visitor import JinjaVisitor, _load_templates_from_path


TEMPLATES_EXTENSION = ".tex"

HEADER_COMMAND_MAP = {
    "1": r"chapter",
    "2": r"section",
    "3": r"subsection",
    "4": r"subsubsection",
    "5": r"paragraph",
    "6": r"subparagraph",
}

templates = _load_templates_from_path(
    str(files(__package__).joinpath("templates")), TEMPLATES_EXTENSION
)


class TexVisitor(JinjaVisitor):
    format_code = "tex"
    extension = TEMPLATES_EXTENSION

    default_templates = Environment.from_dict(templates)

    def _escape_text(self, text):
        conv = {
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde{}",
            "^": r"\^{}",
            "\\": r"\textbackslash{}",
            "<": r"\textless{}",
            ">": r"\textgreater{}",
        }
        regex = re.compile(
            "|".join(
                re.escape(str(key))
                for key in sorted(conv.keys(), key=lambda item: -len(item))
            )
        )
        return regex.sub(lambda match: conv[match.group()], text)

    def _visit_header(self, node: Node, **kwargs) -> dict:
        result = self._visit_default(node, **kwargs)

        level = str(min(node.level, 6))

        result.update(
            {
                "level": level,
                "internal_id": node.internal_id,
                "name": node.name,
                "command": HEADER_COMMAND_MAP.get(level),
            }
        )

        self._add_visit_content(result, node, **kwargs)
        self._add_visit_labels(result, node, **kwargs)

        return result

    def _visit_text(self, node: Node, **kwargs) -> dict:
        result = super()._visit_text(node, **kwargs)

        result["value"] = self._escape_text(result["value"])

        return result

    def _visit_verbatim(self, node: Node, **kwargs) -> dict:
        result = super()._visit_verbatim(node, **kwargs)

        result["value"] = self._escape_text(result["value"])

        return result

    def _visit_source(self, node: Node, **kwargs) -> dict:
        # Find all lines that are highlighted.
        highlighted_lines = [
            line.line_number for line in node.content if line.highlight_style
        ]

        result = super()._visit_source(node, **kwargs)

        result["highlights"] = highlighted_lines

        return result
