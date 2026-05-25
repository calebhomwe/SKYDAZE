# FTC FULL TIME CHRISTIAN — Business Plan v0.1

> One page that any investor, manufacturer, or operator can read in 8 minutes.

## 1. Thesis

Luxury Christian streetwear. Quiet, restrained, theologically literate.
Priced like Lemaire (entry) to FOG mainline (top). Sells like Stampd at
launch, builds like a heritage label over five years.

There is no serious luxury Christian brand. There is loud merch, and there is
quiet luxury. We are the bridge.

## 2. Product Architecture (Collection V1 — 1000 SKUs)

| Section | Count | MSRP Band | Avg COGS | Avg Margin |
| :--- | ---: | :--- | ---: | ---: |
| Tracksuit | 250 | $160–$240 | ~$50 | **70–78%** |
| Outerwear | 250 | $220–$480 | ~$95 | **75–80%** |
| Tee & Top | 250 | $80–$160 | ~$27 | **72–80%** |
| Accessory | 250 | $60–$220 | ~$28 | **70–82%** |

All four sections share fabric mills, finishing techniques, and palette
families to compress purchase orders and unlock volume pricing.

Live numbers are in `artifacts/collection_v1/summary.json` and
`artifacts/collection_v1/pricing.csv` after running
`python generate_collection.py`.

## 3. Drop Cadence (Year 1)

| Quarter | Drop | Pieces | Purpose |
| :--- | :--- | ---: | :--- |
| Q1 | First Light (capsule) | 12 | Define the brand on press + DSM walls |
| Q2 | The Cloister | 36 | First full retail line; first paid Meta + TikTok |
| Q3 | Vespers (FW) | 80 | Outerwear-heavy; press peak |
| Q4 | Lectionary (holiday) | 24 | Gifting; accessories pulled forward |

Restocks every 4 weeks on best-sellers (top 10% by sell-through). New
silhouettes only at drop boundaries.

## 4. Unit Economics (per piece, average)

```
MSRP                $180
Estimated COGS      $52
Fulfillment + ship   $9
Returns reserve     $7   (3.9% of MSRP)
Payment proc        $5   (2.9% + $0.30)
-----------------------
Contribution        $107  (~59% contribution margin)
```

Marketing target ≤ 25% of revenue. Net contribution after marketing ~$62 /
piece. At a Q3 drop of 80 pieces × 1.6 sell-through = 128 units → ~$23k
quarterly contribution from one drop alone. Drop scale grows linearly with
brand maturity.

## 5. Channels

1. **DTC Shopify** (default). 60-70% of revenue Y1.
2. **DSM / SSENSE pitch** by Q3. Wholesale at 50% MSRP; press value > margin.
3. **Trunk shows at concept stores** in NYC / LA / London / Tokyo / Lagos.
4. **Capsule with a peer brand** (Q4) — co-sign as cultural credential.

## 6. Marketing

- Seeding budget > paid ads in Y1 (Section 10 of master context).
- Two posts/week on IG, one on TikTok, one email/week. Hard cap.
- Press: SSENSE editorial, Highsnobiety, Hypebeast premium — pitched
  individually with one image per editor.
- Cultural seeding: musicians, designers, athletes whose audience aligns with
  brand tone. No paid creators in tier-1.

## 7. Production

- Fabric mill: Portuguese / Japanese partners for 280-320gsm garment-washed
  cotton. Plan two seasons ahead.
- Cut & sew: Portugal preferred (Y1), Turkey for outerwear (Y2).
- Embroidery: domestic for tonal samples; production at mill.
- Lead time: 90 days drop-to-door. Pre-orders absorb 30% of demand at full
  price.

## 8. Risk register

| Risk | Mitigation |
| :--- | :--- |
| Brand confused with merch tier | Auto-kill gates (Section 1 forbidden list) |
| Doctrinal misread | `theological-review-counsel` (FTC-082) before publish |
| Fabric mill delays | Two mills minimum from Q2; safety stock on core fabric |
| Over-saturation | Drop cadence locked; restocks only on top decile |
| Trademark collision | `trademark-sentinel` (FTC-081) before every name lock |

## 9. The 18-month plan

- **Month 0-3:** First Light capsule. Press hit. DSM meeting.
- **Month 4-6:** The Cloister. First $50k month.
- **Month 7-9:** Vespers. Wholesale orders. First celebrity unpaid wear.
- **Month 10-12:** Lectionary. Year close at $750k-$1.2M revenue.
- **Month 13-18:** Y2 mainline. Second mill. First permanent retail partner.

## 10. What the AI village automates

All 100 agents are documented in `agents/REGISTRY.yaml`. The shortlist that
removes the most operator time:

- `theology-concept-architect` (FTC-006) — never run out of concepts
- `seedream-prompt-engineer` (FTC-026) — every hero shot is editorial-grade
- `quality-gate-keeper` (FTC-004) — nothing off-brand ships
- `shopify-sync-agent` (FTC-071) — drop launches itself
- `cost-monitor` (FTC-090) — kills runaway API spend
- `theological-review-counsel` (FTC-082) — protects pastoral credibility

Operator hours per drop drop from ~120 (manual) to ~12 (review + approve).
