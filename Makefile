.PHONY: install scrape test full verify package clean lint

install:
	pip install -r requirements.txt

scrape:
	python3 scraper.py

scrape-real:
	FTC_RUN_MODE=real python3 scraper.py

test:
	python3 run_test.py

test-real:
	FTC_RUN_MODE=real python3 run_test.py

full:
	python3 generate_collection.py

verify:
	python3 verify_collection.py

package:
	python3 package_catalog.py

clean:
	rm -rf artifacts/scrapes/raw artifacts/concepts artifacts/qa __pycache__ ftc/__pycache__

lint:
	ruff check ftc scraper.py run_test.py generate_collection.py verify_collection.py
