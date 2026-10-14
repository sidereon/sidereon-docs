"""Sphinx configuration for the sidereon-adk developer documentation.

Build locally with `make docs` (live preview) or `make docs-build` (strict, as on Netlify).
"""

from __future__ import annotations

import ast
import os
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse

DOCS = Path(__file__).resolve().parent
# The SDK repository (sidereon-adk) is read at build time for the API reference, the
# example pages, the changelog and the sample policy. Locally it is the sibling clone;
# in GitHub Actions the workflow checks it out and sets SIDEREON_ADK_PATH.
ADK = Path(os.environ.get("SIDEREON_ADK_PATH") or DOCS.parent.parent / "sidereon-adk").resolve()
FROM_ADK = DOCS / "_from_adk"  # copied from the SDK on every build; never edit by hand
if not (ADK / "src" / "sidereon_adk").is_dir():
    raise RuntimeError(f"sidereon-adk not found at {ADK}. Clone it next to this repository "
                       "or set SIDEREON_ADK_PATH.")
sys.path.insert(0, str(ADK / "src"))

import sidereon_adk  # noqa: E402

# -- Project -----------------------------------------------------------------------------

project = "sidereon-adk"
author = "Sidereon"
copyright = "2026, Sidereon"  # noqa: A001
release = version = sidereon_adk.__version__

# -- Extensions --------------------------------------------------------------------------

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.githubpages",
    "sphinx_design",
    "sphinx_copybutton",
    "sphinxcontrib.mermaid",
    "notfound.extension",
]

source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
exclude_patterns = ["_build", "_from_adk", "Thumbs.db", ".DS_Store"]
root_doc = "index"

# Markdown (MyST)
myst_enable_extensions = ["colon_fence", "deflist", "fieldlist", "attrs_inline", "tasklist"]
myst_heading_anchors = 3
myst_fence_as_directive = ["mermaid"]

# API reference from docstrings (Google style)
autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
    "member-order": "bysource",
    "exclude-members": "model_config, model_fields, model_computed_fields",
}
autodoc_typehints = "description"
autodoc_typehints_format = "short"
autodoc_class_signature = "separated"
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_use_ivar = True
napoleon_use_rtype = False
default_role = "literal"  # `name` in docstrings renders as code

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True

# -- HTML (Furo theme) -------------------------------------------------------------------

html_theme = "furo"
html_title = f"sidereon-adk {release}"
html_logo = "_static/logo.svg"
html_favicon = "_static/logo.svg"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_copy_source = False
html_show_sourcelink = False

html_theme_options = {
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "top_of_page_buttons": ["view", "edit"],
    "light_css_variables": {"color-brand-primary": "#4b3fd6", "color-brand-content": "#4b3fd6"},
    "dark_css_variables": {"color-brand-primary": "#a5a0ff", "color-brand-content": "#a5a0ff"},
}

# -- Publishing settings (all optional, from environment variables) -----------------------
#
# DOCS_BASE_URL        Full address of the published site, e.g.
#                      https://sidereon.github.io/sidereon-docs/  (sitemap, 404 page links).
#                      On Netlify it is taken from Netlify's own variables when not set.
# DOCS_SHOW_SOURCE     "true" adds "[source]" pages with the library's full source code.
#                      Off by default: the SDK repository is private and the site is public.
# DOCS_REPOSITORY_URL  Adds "edit this page" links. Only set it for a repository readers can open.

if os.environ.get("DOCS_SHOW_SOURCE", "").lower() == "true":
    extensions.append("sphinx.ext.viewcode")

_repository = os.environ.get("DOCS_REPOSITORY_URL", "")
if _repository.startswith("https://"):
    html_theme_options.update(
        {
            "source_repository": _repository.removesuffix(".git").rstrip("/") + "/",
            "source_branch": os.environ.get("DOCS_REPOSITORY_BRANCH", "main"),
            "source_directory": "docs/",
        }
    )

_netlify_url = (
    os.environ.get("URL")
    if os.environ.get("CONTEXT") == "production"
    else os.environ.get("DEPLOY_PRIME_URL")
)
_base = os.environ.get("DOCS_BASE_URL") or _netlify_url
if _base:
    html_baseurl = _base.rstrip("/") + "/"
    extensions.append("sphinx_sitemap")
    sitemap_url_scheme = "{link}"

# Links on the "page not found" page must be absolute, including any sub-path
# (GitHub Pages project sites live under /<repository>/).
notfound_urls_prefix = urlparse(_base).path.rstrip("/") + "/" if _base else "/"

# -- Example pages, generated from examples/*.py -----------------------------------------


def _write_if_changed(path: Path, text: str) -> None:
    """Avoid touching unchanged files, so the live preview does not rebuild in a loop."""
    if not path.exists() or path.read_text() != text:
        path.write_text(text)


def copy_from_adk(app: object) -> None:
    """Copy the SDK files the pages show: examples, changelog and the sample policy."""
    (FROM_ADK / "examples").mkdir(parents=True, exist_ok=True)
    for source in [*sorted((ADK / "examples").glob("[0-9]*.py")), ADK / "CHANGELOG.md",
                   ADK / "policies" / "tools.rego"]:
        relative = source.relative_to(ADK)
        target = FROM_ADK / ("examples" if relative.parts[0] == "examples" else "") / source.name
        _write_if_changed(target, source.read_text())


def generate_example_pages(app: object) -> None:
    """Create one page per example (title from its docstring) and an index table."""
    target = DOCS / "examples"
    target.mkdir(exist_ok=True)
    rows = []
    for source in sorted((FROM_ADK / "examples").glob("[0-9]*.py")):
        summary = (ast.get_docstring(ast.parse(source.read_text())) or source.stem).strip()
        title = summary.splitlines()[0].rstrip(".")
        details = "\n".join(summary.splitlines()[1:]).strip()
        page = (
            f"# {source.stem[:2]} · {title}\n\n"
            + (f"```text\n{details}\n```\n\n" if details else "")
            + f"Run it with `python examples/{source.name}`.\n\n"
            + f"```{{literalinclude}} ../_from_adk/examples/{source.name}\n:language: python\n```\n"
        )
        _write_if_changed(target / f"{source.stem}.md", page)
        rows.append(f"| [{source.stem[:2]}]({source.stem}.md) | {title} |")
    index = (
        "# Examples\n\n"
        "Every example is a complete program. Set a model and its key, then run it:\n\n"
        "```bash\nexport SIDEREON_MODEL=openai:gpt-4o-mini OPENAI_API_KEY=...\n"
        "python examples/01_simple_agent.py\n```\n\n"
        "| # | Example |\n|---|---|\n" + "\n".join(rows) + "\n\n"
        "```{toctree}\n:hidden:\n:glob:\n\n[0-9]*\n```\n"
    )
    _write_if_changed(target / "index.md", index)


# -- Markdown code fences inside docstrings ----------------------------------------------


def markdown_fences_to_code_blocks(
    app: object, what: str, name: str, obj: object, options: object, lines: list[str]
) -> None:
    """Docstrings use ```python fences (readable in editors); turn them into code blocks."""
    converted: list[str] = []
    inside = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            if not inside:
                indent = line[: len(line) - len(line.lstrip())]
                language = stripped[3:].strip() or "text"
                converted += [f"{indent}.. code-block:: {language}", ""]
            else:
                converted.append("")
            inside = not inside
            continue
        converted.append(f"   {line}" if inside and stripped else line)
    lines[:] = converted


def copy_not_found_page(app: object, exception: Exception | None) -> None:
    """GitHub Pages serves /404.html for unknown addresses; the dirhtml builder writes 404/."""
    page = Path(app.outdir) / "404" / "index.html"  # type: ignore[attr-defined]
    if exception is None and page.exists():
        shutil.copyfile(page, page.parent.parent / "404.html")


def setup(app: object) -> None:
    """Register the build hooks."""
    app.connect("builder-inited", copy_from_adk)  # type: ignore[attr-defined]
    app.connect("builder-inited", generate_example_pages)  # type: ignore[attr-defined]
    app.connect("build-finished", copy_not_found_page)  # type: ignore[attr-defined]
    app.connect("autodoc-process-docstring", markdown_fences_to_code_blocks)  # type: ignore[attr-defined]
