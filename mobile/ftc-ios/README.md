# FTC iOS — AI generation + shopping app

SwiftUI app that generates streetwear concepts on-device prompt-side, calls Fal.ai / Novita / OpenRouter for image gen, and surfaces the FTC catalog in story-first product views.

## What it does
1. **Generate tab** — describe a concept in plain English; app calls one of three providers; image appears in 5-30s.
2. **Gallery tab** — saved renders, organized by drop.
3. **Drops tab** — current FTC catalog, story-first product view.
4. **Creator tab** — for FTC ambassador / influencer creators, shows unique discount code + commission earned.

## Requirements
- Xcode 15.4+
- iOS 17.0+
- A `.env`-style `Secrets.plist` in `FTC/Resources/` with provider keys
- Apple Developer account (for TestFlight + App Store)

## First-run setup

```bash
# Clone and open
cd mobile/ftc-ios
open Package.swift  # or open FTC.xcodeproj if generated

# Provide keys (not committed)
cp FTC/Resources/Secrets.plist.example FTC/Resources/Secrets.plist
# Edit Secrets.plist and fill: FAL_KEY, NOVITA_API_KEY, OPENROUTER_API_KEY
```

## Build instructions

### Local dev
1. Open `Package.swift` in Xcode.
2. Select a simulator (iPhone 15 Pro recommended) or your device.
3. Press ⌘R.

### TestFlight (private beta)
1. Archive: Product → Archive.
2. Window → Organizer → Distribute App → App Store Connect → Upload.
3. In App Store Connect, add internal testers.
4. Wait ~10 minutes for processing.

### App Store submission
1. Same as TestFlight, then submit for review.
2. Review typically 24-48 hours.
3. Required: screenshots (6.7", 6.5", 5.5"), privacy policy URL, support URL.

## Provider routing logic
The app prefers cheapest available provider:
1. **Novita Flux Schnell** — ~$0.001/image, ~3s
2. **OpenRouter Flux Schnell** — ~$0.003/image, ~5s
3. **Fal.ai Seedream-4** — ~$0.04/image, ~8s (premium aesthetic)
4. **OpenRouter Gemini Flash Image** — ~$0.04/image, ~6s
5. **Fal.ai Nano Banana** — ~$0.03/image, ~10s (mockup-specialized)

Fallback chain: if a provider returns 429 or 5xx, try the next.

## Privacy & secrets
- API keys never leave the device.
- All images stored locally in `Documents/Generations/`.
- iCloud sync optional (off by default).
- No analytics SDK. We don't ship user telemetry.

## Project structure
```
FTC/
├── FTCApp.swift              # App entry
├── ContentView.swift          # TabView root
├── Models/
│   ├── Generation.swift       # GenerationRequest + GenerationResult
│   ├── Provider.swift         # Provider enum + routing
│   └── Concept.swift          # FTC Section-4 concept schema
├── Services/
│   ├── FalService.swift
│   ├── NovitaService.swift
│   ├── OpenRouterService.swift
│   ├── ProviderRouter.swift   # tries providers in cost order
│   └── SecretsStore.swift     # loads from Secrets.plist
├── Views/
│   ├── GenerateView.swift     # prompt + provider + button
│   ├── GalleryView.swift      # saved renders
│   ├── DropsView.swift        # current FTC catalog
│   └── CreatorView.swift      # ambassador portal
└── Resources/
    ├── Assets.xcassets        # app icon, colors
    ├── Secrets.plist.example
    └── Info.plist
```

## Roadmap
- v1.0 — Generate + Gallery + Drops tabs. TestFlight beta.
- v1.1 — Creator tab + commission tracking.
- v1.2 — Push notifications for drops.
- v1.3 — Bot-detection on drop checkout.
- v2.0 — visionOS spatial gallery (Apple Vision Pro).

## Cost discipline
Every generation logs to `Documents/cost_log.json`:
```json
{"date": "2026-05-26", "provider": "novita-flux-schnell", "cost_usd": 0.001, "prompt_hash": "abc..."}
```
This feeds `Tier 33 / mobile-cost-monitor` agent.
