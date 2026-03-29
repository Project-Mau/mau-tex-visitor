from pathlib import Path

import pytest

from mau import Mau
from mau.test_helpers import NullMessageHandler

from mau_tex_visitor import TexVisitor

# End-to-end tests that exercise the full Mau
# pipeline (lexer -> parser -> TeX visitor)
# on real `.mau` source files stored in `cases/`.
#
# Each `.mau` file has a companion `.tex`
# reference. The test processes the source
# and asserts that the output matches the
# reference.
#
# Run with `--update-e2e-refs` to regenerate
# every reference file from the current output.

CASES_DIR = Path(__file__).parent / "cases"


def discover_cases():
    cases = []
    for mau_path in sorted(CASES_DIR.glob("*.mau")):
        tex_path = mau_path.with_suffix(".tex")
        cases.append(pytest.param(mau_path, tex_path, id=mau_path.stem))
    return cases


@pytest.mark.parametrize("mau_path,tex_path", discover_cases())
def test_e2e(mau_path, tex_path, request):
    source = mau_path.read_text()

    mau = Mau(NullMessageHandler())
    result = mau.process(TexVisitor, source, str(mau_path))

    if request.config.getoption("--update-e2e-refs"):
        tex_path.write_text(result)
        pytest.skip("reference updated")

    if not tex_path.exists():
        pytest.fail(
            f"Reference file {tex_path.name} not found. "
            f"Run with --update-e2e-refs to generate it."
        )

    expected = tex_path.read_text()

    assert result == expected


# Some TeX templates are intentionally empty because
# LaTeX handles these features natively (e.g. footnotes
# via \footnote{}) or because they are not applicable
# to the TeX output format.
TEMPLATES_DIR = Path(__file__).parents[2] / "mau_tex_visitor" / "templates"

INTENTIONALLY_EMPTY_TEMPLATES = [
    "blockgroup-item.tex",
    "footnotes.tex",
    "footnotes-item.tex",
    "macro.tex",
    "toc.tex",
    "toc-item.tex",
]


@pytest.mark.parametrize("template_name", INTENTIONALLY_EMPTY_TEMPLATES)
def test_empty_templates(template_name):
    template_path = TEMPLATES_DIR / template_name
    assert template_path.exists(), f"Template {template_name} does not exist"
    content = template_path.read_text().strip()
    assert content == "", (
        f"Template {template_name} is expected to be empty but contains: {content!r}"
    )
