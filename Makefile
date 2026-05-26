.PHONY: install scrape test full clean lint spawn-plan spawn-preflight spawn-dry spawn-launch game-run game-stress game-cover

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
	ruff check ftc scraper.py run_test.py ops/spawn/launch_swarm.py

spawn-plan:
	python3 ops/spawn/launch_swarm.py --mode plan-only

spawn-preflight:
	python3 ops/spawn/launch_swarm.py --preflight-only

spawn-dry:
	python3 ops/spawn/launch_swarm.py --mode dry-run --max-launches 1

spawn-launch:
	python3 ops/spawn/launch_swarm.py --mode execute

game-run:
	godot --path games/lumenfall res://scenes/Menu.tscn

game-stress:
	mkdir -p artifacts/lumenfall
	godot --headless --path games/lumenfall res://tests/StressScene.tscn

game-cover:
	python3 games/lumenfall/tools/generate_cover.py
