import SwiftUI

struct GenerateView: View {
    @State private var prompt: String = "320gsm garment-washed cotton tee in bone, tonal embroidery at chest, soft north window light, Lemaire restraint"
    @State private var background: GenerationRequest.Background = .white
    @State private var preferredProvider: Provider? = nil
    @State private var isGenerating = false
    @State private var lastResult: GenerationResult?
    @State private var errorMessage: String?

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    Text("Concept")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    TextEditor(text: $prompt)
                        .frame(minHeight: 140)
                        .padding(8)
                        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 12))

                    HStack {
                        Picker("Background", selection: $background) {
                            ForEach(GenerationRequest.Background.allCases) { bg in
                                Text(bg.rawValue.capitalized).tag(bg)
                            }
                        }
                        .pickerStyle(.segmented)
                    }

                    Picker("Provider", selection: $preferredProvider) {
                        Text("Cheapest available").tag(nil as Provider?)
                        ForEach(Provider.costOrdered) { p in
                            Text("\(p.displayName) · $\(String(format: "%.4f", p.costEstimateUSD))").tag(p as Provider?)
                        }
                    }

                    Button {
                        Task { await generate() }
                    } label: {
                        HStack {
                            if isGenerating { ProgressView().controlSize(.small) }
                            Text(isGenerating ? "Generating…" : "Generate")
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(isGenerating || prompt.isEmpty)

                    if let msg = errorMessage {
                        Text(msg).foregroundStyle(.red).font(.caption)
                    }

                    if let result = lastResult,
                       let uiImage = UIImage(data: result.imageData) {
                        VStack(alignment: .leading, spacing: 8) {
                            Image(uiImage: uiImage)
                                .resizable()
                                .aspectRatio(contentMode: .fit)
                                .clipShape(RoundedRectangle(cornerRadius: 14))
                            Text("\(result.provider.displayName) · $\(String(format: "%.4f", result.costUSD)) · \(String(format: "%.1fs", result.durationSeconds))")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                    }
                }
                .padding()
            }
            .navigationTitle("Generate")
        }
    }

    private func generate() async {
        guard SecretsStore.hasAnyKey() else {
            errorMessage = "No provider keys configured. Add to Secrets.plist."
            return
        }
        isGenerating = true
        errorMessage = nil
        defer { isGenerating = false }
        do {
            let request = GenerationRequest(prompt: prompt, background: background, preferredProvider: preferredProvider)
            lastResult = try await ProviderRouter.shared.generate(request)
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
