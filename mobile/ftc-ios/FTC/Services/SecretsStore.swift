import Foundation

enum SecretsStore {
    private static let bundle = Bundle.main

    static var falKey: String? { value(for: "FAL_KEY") }
    static var novitaKey: String? { value(for: "NOVITA_API_KEY") }
    static var openrouterKey: String? { value(for: "OPENROUTER_API_KEY") }

    static func value(for key: String) -> String? {
        // 1) ProcessInfo env (for dev / TestFlight via xcconfig)
        if let v = ProcessInfo.processInfo.environment[key], !v.isEmpty {
            return v
        }
        // 2) Secrets.plist (gitignored, user-supplied)
        if let url = bundle.url(forResource: "Secrets", withExtension: "plist"),
           let data = try? Data(contentsOf: url),
           let dict = try? PropertyListSerialization.propertyList(from: data, format: nil) as? [String: String] {
            return dict[key]
        }
        return nil
    }

    static func hasAnyKey() -> Bool {
        falKey != nil || novitaKey != nil || openrouterKey != nil
    }
}
