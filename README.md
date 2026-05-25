# FTC streetwear art pipeline

Generates 1000 FTC FULL TIME CHRISTIAN print graphics with:

- trend/reference synthesis from `scrape_targets.yaml`
- standalone transparent SVG artwork at 2048 x 2048
- EPS companions for print shops
- flat mockup SVG previews
- an offline `catalog.html` for review and filtering

Run:

```bash
pip install -r requirements.txt
python scraper.py
python generate_collection.py
python verify_collection.py
```

Outputs are written to `artifacts/collection_v1/`.
