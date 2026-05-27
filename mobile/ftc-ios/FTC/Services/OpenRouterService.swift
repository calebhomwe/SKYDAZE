import Foundation

actor OpenRouterService {
    static let shared = OpenRouterService()
    private let session = URLSession.shared
    private let base = "https://openrouter.ai/api/v1"

    private let modelSlugs: [Provider: String] = [
        .openrouterFluxSchnell: "black-forest-labs/flux-schnell",
        .openrouterFluxPro: "black-forest-labs/flux-1.1-pro",
        .openrouterGeminiFlashImage: "google/gemini-2.5-flash-image-preview",
    ]

    func generate(_ request: GenerationRequest, provider: Provider) async throws -> Data {
        guard let key = SecretsStore.openrouterKey else {
            throw NSError(domain: "OpenRouterService", code: 401)
        }
        guard let slug = modelSlugs[provider] else {
            throw NSError(domain: "OpenRouterService", code: 400)
        }
        var req = URLRequest(url: URL(string: "\(base)/images/generations")!)
        req.httpMethod = "POST"
        req.setValue("Bearer \(key)", forHTTPHeaderField: "Authorization")
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.setValue("https://github.com/calebhomwe/SKYDAZE", forHTTPHeaderField: "HTTP-Referer")
        req.setValue("FTC FULL TIME CHRISTIAN", forHTTPHeaderField: "X-Title")
        let body: [String: Any] = [
            "model": slug,
            "prompt": request.prompt,
            "size": "\(request.width)x\(request.height)",
        ]
        req.httpBody = try JSONSerialization.data(withJSONObject: body)
        let (data, response) = try await session.data(for: req)
        guard let http = response as? HTTPURLResponse, 200..<300 ~= http.statusCode else {
            throw NSError(domain: "OpenRouterService", code: (response as? HTTPURLResponse)?.statusCode ?? -1)
        }
        guard let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
              let entries = json["data"] as? [[String: Any]],
              let first = entries.first else {
            throw NSError(domain: "OpenRouterService", code: 500)
        }
        if let b64 = first["b64_json"] as? String, let imgData = Data(base64Encoded: b64) {
            return imgData
        }
        if let urlString = first["url"] as? String, let url = URL(string: urlString) {
            let (imgData, _) = try await session.data(from: url)
            return imgData
        }
        throw NSError(domain: "OpenRouterService", code: 500)
    }
}
