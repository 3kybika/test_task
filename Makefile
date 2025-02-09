PYTHON?=python3.10
SOURCE_DIR=./src
TESTS_DIR=./tests
COVERAGE?=coverage
COVERAGE_HTML_REPORT_DIR?=./htmlcov/
PEX_FILE=search_quality_dags-$(shell poetry version -s).pex


all: help


help:
	#@echo "test         - run tests"
	#@echo "coverage     - run tests with code coverage"
	#@echo "htmlcoverage - run tests with code coverage and generate html report"
	@echo "lint         - run avito linter"
	@echo "fmt          - run avito formatter"


poetry-install:
	#$(PYTHON) -m ensurepip
	$(PYTHON) -m pip install -U --user poetry==1.7.0 poetry-core==1.8.1 poetry-dynamic-versioning==1.2.0 poetry-plugin-export==1.6.0


shell:
	$(PYTHON) -m poetry shell


test: clean
	$(PYTHON) -m pytest $(TESTS_DIR) -v


coverage: clean
	$(COVERAGE) run --branch --source=$(SOURCE_DIR) -m pytest $(TESTS_DIR) --durations 0
	$(COVERAGE) report --fail-under=100 && echo "Coverage OK"


lint-ruff:
	@echo === RUFF ===
	ruff check app

lint-black:
	@echo === BLACK ===
	black --check app

lint-flake8:
	@echo === FLAKE8 ===
	flake8 app

lint-mypy:
	@echo === MYPY ===
	mypy app
	mypy tests --explicit-package-bases


lint: lint-ruff lint-black #lint-flake8 lint-mypy lint-dead


start:
	export HOST=${HOST:-127.0.0.1}
	export PORT=${PORT:-8081}
	exec uvicorn --reload --host ${HOST} --port ${PORT} "app.main:app" --reload