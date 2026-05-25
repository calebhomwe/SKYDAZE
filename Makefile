.PHONY: install scrape test full clean lint

install:
	pip install -r requirements.txt

scrape:
	python scraper.py

scrape-real:
	FTC_RUN_MODE=real python scraper.py

test:
	python run_test.py

test-real:
	FTC_RUN_MODE=real python run_test.py

clean:
	rm -rf artifacts/scrapes/raw artifacts/concepts artifacts/qa __pycache__ ftc/__pycache__

lint:
	ruff check ftc scraper.py run_test.py
