import Foundation

actor ProviderRouter {
    static let shared = ProviderRouter()

    /// Try providers in cost order. If `preferred` set, try it first.
    func generate(_ request: GenerationRequest) async throws -> GenerationResult {
        var attempts: [Provider] = Provider.costOrdered
        if let preferred = request.preferredProvider {
            attempts.removeAll(where: { $0 == preferred })
            attempts.insert(preferred, at: 0)
        }
        var lastError: Error?
        for provider in attempts {
            let start = Date()
            do {
                let data = try await dispatch(request, provider: provider)
                let duration = Date().timeIntervalSince(start)
                let result = GenerationResult(
                    id: UUID(),
                    requestId: request.id,
                    imageData: data,
                    provider: provider,
                    costUSD: provider.costEstimateUSD,
                    durationSeconds: duration,
                    createdAt: Date()
                )
                logCost(result)
                return result
            } catch {
                lastError = error
                continue
            }
        }
        throw lastError ?? NSError(domain: "ProviderRouter", code: 500, userInfo: [NSLocalizedDescriptionKey: "All providers failed"])
    }

    private func dispatch(_ request: GenerationRequest, provider: Provider) async throws -> Data {
        switch provider {
        case .falFluxPro, .falFluxSchnell, .falSeedream4, .falNanoBanana2:
            return try await FalService.shared.generate(request, provider: provider)
        case .novitaFluxSchnell:
            return try await NovitaService.shared.generate(request, provider: provider)
        case .openrouterFluxSchnell, .openrouterFluxPro, .openrouterGeminiFlashImage:
            return try await OpenRouterService.shared.generate(request, provider: provider)
        }
    }

    private func logCost(_ result: GenerationResult) {
        let entry: [String: Any] = [
            "date": ISO8601DateFormatter().string(from: result.createdAt),
            "provider": result.provider.rawValue,
            "cost_usd": result.costUSD,
            "duration_s": result.durationSeconds,
        ]
        do {
            let url = try FileManager.default.url(for: .documentDirectory, in: .userDomainMask, appropriateFor: nil, create: true).appendingPathComponent("cost_log.jsonl")
            let line = (try? JSONSerialization.data(withJSONObject: entry)).flatMap { String(data: $0, encoding: .utf8) } ?? ""
            try (line + "\n").appendIngestingTo(url: url)
        } catch {
            // best-effort logging
        }
    }
}

private extension String {
    func appendIngestingTo(url: URL) throws {
        if FileManager.default.fileExists(atPath: url.path) {
            let handle = try FileHandle(forWritingTo: url)
            try handle.seekToEnd()
            if let data = self.data(using: .utf8) { try handle.write(contentsOf: data) }
            try handle.close()
        } else {
            try self.write(to: url, atomically: true, encoding: .utf8)
        }
    }
}
