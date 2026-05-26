import Foundation

actor NovitaService {
    static let shared = NovitaService()
    private let session = URLSession.shared
    private let base = "https://api.novita.ai/v3"

    private let modelSlugs: [Provider: String] = [
        .novitaFluxSchnell: "FLUX.1-schnell",
    ]

    func generate(_ request: GenerationRequest, provider: Provider) async throws -> Data {
        guard let key = SecretsStore.novitaKey else {
            throw NSError(domain: "NovitaService", code: 401)
        }
        guard let slug = modelSlugs[provider] else {
            throw NSError(domain: "NovitaService", code: 400, userInfo: [NSLocalizedDescriptionKey: "Not supported by Novita: \(provider.rawValue)"])
        }
        // Kick off async task
        var startReq = URLRequest(url: URL(string: "\(base)/async/txt2img")!)
        startReq.httpMethod = "POST"
        startReq.setValue("Bearer \(key)", forHTTPHeaderField: "Authorization")
        startReq.setValue("application/json", forHTTPHeaderField: "Content-Type")
        let body: [String: Any] = [
            "model_name": slug,
            "prompt": request.prompt,
            "width": request.width,
            "height": request.height,
            "image_num": 1,
            "guidance_scale": 3.5,
            "steps": 28,
        ]
        startReq.httpBody = try JSONSerialization.data(withJSONObject: body)
        let (startData, _) = try await session.data(for: startReq)
        guard let startJson = try JSONSerialization.jsonObject(with: startData) as? [String: Any],
              let taskId = startJson["task_id"] as? String else {
            throw NSError(domain: "NovitaService", code: 500)
        }
        // Poll
        for _ in 0..<60 {
            try await Task.sleep(nanoseconds: 2_000_000_000)
            var statusReq = URLRequest(url: URL(string: "\(base)/async/task-result?task_id=\(taskId)")!)
            statusReq.setValue("Bearer \(key)", forHTTPHeaderField: "Authorization")
            let (statusData, _) = try await session.data(for: statusReq)
            guard let json = try JSONSerialization.jsonObject(with: statusData) as? [String: Any] else { continue }
            let status = (json["task"] as? [String: Any])?["status"] as? String
            if status == "TASK_STATUS_SUCCEED" {
                guard let images = json["images"] as? [[String: Any]],
                      let urlString = images.first?["image_url"] as? String,
                      let url = URL(string: urlString) else {
                    throw NSError(domain: "NovitaService", code: 500)
                }
                let (imgData, _) = try await session.data(from: url)
                return imgData
            }
            if status == "TASK_STATUS_FAILED" {
                throw NSError(domain: "NovitaService", code: 502)
            }
        }
        throw NSError(domain: "NovitaService", code: 504, userInfo: [NSLocalizedDescriptionKey: "Timed out"])
    }
}
