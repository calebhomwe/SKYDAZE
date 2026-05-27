import Foundation

enum Provider: String, Codable, CaseIterable, Identifiable {
    case novitaFluxSchnell = "novita-flux-schnell"
    case openrouterFluxSchnell = "openrouter-flux-schnell"
    case falFluxSchnell = "fal-flux-schnell"
    case falSeedream4 = "fal-seedream-4"
    case openrouterFluxPro = "openrouter-flux-pro"
    case falFluxPro = "fal-flux-pro"
    case openrouterGeminiFlashImage = "openrouter-gemini-flash-image"
    case falNanoBanana2 = "fal-nano-banana-2"

    var id: String { rawValue }

    var displayName: String {
        switch self {
        case .novitaFluxSchnell: "Novita · Flux Schnell"
        case .openrouterFluxSchnell: "OpenRouter · Flux Schnell"
        case .falFluxSchnell: "Fal.ai · Flux Schnell"
        case .falSeedream4: "Fal.ai · Seedream 4"
        case .openrouterFluxPro: "OpenRouter · Flux 1.1 Pro"
        case .falFluxPro: "Fal.ai · Flux Pro"
        case .openrouterGeminiFlashImage: "OpenRouter · Gemini Flash Image"
        case .falNanoBanana2: "Fal.ai · Nano Banana 2"
        }
    }

    var costEstimateUSD: Double {
        switch self {
        case .novitaFluxSchnell: 0.001
        case .openrouterFluxSchnell, .falFluxSchnell: 0.003
        case .falNanoBanana2: 0.03
        case .falSeedream4, .openrouterFluxPro, .openrouterGeminiFlashImage: 0.04
        case .falFluxPro: 0.05
        }
    }

    /// Cheapest first.
    static var costOrdered: [Provider] {
        Provider.allCases.sorted { $0.costEstimateUSD < $1.costEstimateUSD }
    }
}
