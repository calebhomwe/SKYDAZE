import Foundation

actor FalService {
    static let shared = FalService()
    private let session = URLSession.shared

    private let modelSlugs: [Provider: String] = [
        .falFluxPro: "fal-ai/flux-pro/v1.1",
        .falFluxSchnell: "fal-ai/flux/schnell",
        .falSeedream4: "fal-ai/bytedance/seedream/v4/text-to-image",
        .falNanoBanana2: "fal-ai/nano-banana/v2",
    ]

    func generate(_ request: GenerationRequest, provider: Provider) async throws -> Data {
        guard let key = SecretsStore.falKey else {
            throw NSError(domain: "FalService", code: 401, userInfo: [NSLocalizedDescriptionKey: "FAL_KEY missing"])
        }
        guard let slug = modelSlugs[provider] else {
            throw NSError(domain: "FalService", code: 400, userInfo: [NSLocalizedDescriptionKey: "Provider not supported by Fal: \(provider.rawValue)"])
        }
        var urlRequest = URLRequest(url: URL(string: "https://fal.run/\(slug)")!)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("Key \(key)", forHTTPHeaderField: "Authorization")
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        let body: [String: Any] = [
            "prompt": request.prompt,
            "image_size": ["width": request.width, "height": request.height],
            "num_images": 1,
            "enable_safety_checker": true,
        ]
        urlRequest.httpBody = try JSONSerialization.data(withJSONObject: body)
        let (data, response) = try await session.data(for: urlRequest)
        guard let http = response as? HTTPURLResponse, 200..<300 ~= http.statusCode else {
            throw NSError(domain: "FalService", code: (response as? HTTPURLResponse)?.statusCode ?? -1)
        }
        guard let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
              let images = (json["images"] as? [[String: Any]]) ?? (json["data"] as? [[String: Any]]),
              let urlString = images.first?["url"] as? String,
              let imageURL = URL(string: urlString) else {
            throw NSError(domain: "FalService", code: 500)
        }
        let (imgData, _) = try await session.data(from: imageURL)
        return imgData
    }
}
