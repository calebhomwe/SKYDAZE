.PHONY: install scrape test full verify package clean lint

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

full:
	python generate_collection.py

verify:
	python verify_collection.py

package:
	python package_catalog.py

clean:
	rm -rf artifacts/scrapes/raw artifacts/concepts artifacts/qa __pycache__ ftc/__pycache__

lint:
	ruff check ftc scraper.py run_test.py generate_collection.py verify_collection.py
