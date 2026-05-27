import Foundation

struct GenerationRequest: Codable, Identifiable {
    let id: UUID
    let prompt: String
    let width: Int
    let height: Int
    let background: Background
    let preferredProvider: Provider?
    let createdAt: Date

    enum Background: String, Codable, CaseIterable, Identifiable {
        case black, white
        var id: String { rawValue }
    }

    init(prompt: String, width: Int = 832, height: Int = 1024,
         background: Background = .white, preferredProvider: Provider? = nil) {
        self.id = UUID()
        self.prompt = prompt
        self.width = width
        self.height = height
        self.background = background
        self.preferredProvider = preferredProvider
        self.createdAt = Date()
    }
}

struct GenerationResult: Codable, Identifiable {
    let id: UUID
    let requestId: UUID
    let imageData: Data
    let provider: Provider
    let costUSD: Double
    let durationSeconds: Double
    let createdAt: Date
}
