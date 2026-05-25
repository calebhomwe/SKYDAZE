.PHONY: install scrape test full clean lint status status-json sprint sprint-strict

PYTHON ?= python3

install:
	pip install -r requirements.txt

scrape:
	$(PYTHON) scraper.py

scrape-real:
	FTC_RUN_MODE=real $(PYTHON) scraper.py

test:
	$(PYTHON) run_test.py

test-real:
	FTC_RUN_MODE=real $(PYTHON) run_test.py

status:
	$(PYTHON) pipeline_status.py

status-json:
	$(PYTHON) pipeline_status.py --json

sprint:
	$(PYTHON) pipeline_orchestrate.py

sprint-strict:
	$(PYTHON) pipeline_orchestrate.py --strict

clean:
	rm -rf artifacts/scrapes/raw artifacts/concepts artifacts/qa __pycache__ ftc/__pycache__

lint:
	ruff check ftc scraper.py run_test.py
