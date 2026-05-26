.PHONY: install scrape scrape-real test test-real collection package render render-dry \
        render-comfy render-comfy-dry render-comfy-cn \
        caveman-install caveman-uninstall caveman-update \
        spawn-plan spawn-dry spawn-launch \
        youtube-harvest youtube-harvest-real \
        clean lint

install:
	pip install -r requirements.txt
	git submodule update --init --recursive

scrape:
	python scraper.py

scrape-real:
	FTC_RUN_MODE=real python scraper.py

test:
	python run_test.py

test-real:
	FTC_RUN_MODE=real python run_test.py

collection:
	python generate_collection.py

package:
	python package_catalog.py

render-dry:
	python workers/render_worker.py --dry-run

render:
	FTC_RUN_MODE=real python workers/render_worker.py

# --- ComfyUI (self-hosted / RunPod, cheapest path) -------------------------
render-comfy-dry:
	python workers/comfyui_worker.py --dry-run --limit 5

render-comfy:
	python workers/comfyui_worker.py

render-comfy-cn:
	python workers/comfyui_worker.py --controlnet

# --- caveman (token-compression skill) --------------------------------------
caveman-install:
	@if [ ! -f tools/caveman/install.sh ]; then \
	  echo "Submodule missing; running git submodule update --init --recursive"; \
	  git submodule update --init --recursive; \
	fi
	bash tools/caveman/install.sh

caveman-update:
	git submodule update --remote tools/caveman

caveman-uninstall:
	@if [ -f tools/caveman/install.sh ]; then \
	  bash tools/caveman/install.sh --uninstall; \
	else \
	  echo "tools/caveman/install.sh not present; nothing to uninstall"; \
	fi

# --- spawn swarm ------------------------------------------------------------
spawn-plan:
	python3 ops/spawn/launch_swarm.py --mode plan-only

spawn-dry:
	python3 ops/spawn/launch_swarm.py --mode dry-run --max-launches 1

spawn-launch:
	python3 ops/spawn/launch_swarm.py --mode execute

# --- YouTube intelligence (Tier 16) ----------------------------------------
youtube-harvest:
	python -m ftc.youtube

youtube-harvest-real:
	FTC_RUN_MODE=real python -m ftc.youtube --real

clean:
	rm -rf artifacts/scrapes/raw artifacts/concepts artifacts/qa __pycache__ ftc/__pycache__

lint:
	ruff check ftc scraper.py run_test.py generate_collection.py package_catalog.py workers ops/spawn/launch_swarm.py
