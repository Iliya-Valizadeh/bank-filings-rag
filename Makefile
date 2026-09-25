# Reproduces every number in the README. Needs data/raw/rbc_2024.pdf (see data/README.md).
# Without make (e.g. on Windows), run the two python commands directly.
PDF ?= data/raw/rbc_2024.pdf

eval:
	python -m eval.check_gold --pdf $(PDF)
	python -m eval.evaluate --pdf $(PDF)

test:
	ruff check .
	pytest -q

.PHONY: eval test
