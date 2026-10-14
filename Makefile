# Documentation for sidereon-adk. Needs the SDK cloned next to this repository
# (../sidereon-adk) or SIDEREON_ADK_PATH pointing at it.
PY ?= .venv/bin/python
ADK ?= $(or $(SIDEREON_ADK_PATH),../sidereon-adk)

.PHONY: help install docs docs-build clean

help:  ## Show this help
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-11s %s\n", $$1, $$2}'

install:  ## Create .venv with the SDK and the documentation tools
	uv venv --python 3.12 .venv && uv pip install -e "$(ADK)" -r requirements.txt

docs:  ## Live preview at http://127.0.0.1:8000 (rebuilds on save)
	$(PY) -m sphinx_autobuild -b dirhtml -d _build/doctrees docs _build/html --watch $(ADK)/src --watch $(ADK)/examples

docs-build:  ## Strict build into _build/html, exactly as the publishing workflow does
	$(PY) -m sphinx -W --keep-going -b dirhtml -d _build/doctrees docs _build/html

clean:  ## Remove build output and copied SDK files
	rm -rf _build docs/_from_adk docs/examples
