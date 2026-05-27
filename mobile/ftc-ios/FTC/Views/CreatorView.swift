import SwiftUI

struct CreatorView: View {
    @State private var creatorCode = "FTC-OBSERVER"
    @State private var commission: Double = 0.00

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    VStack(spacing: 8) {
                        Text("Your code")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                        Text(creatorCode)
                            .font(.system(.largeTitle, design: .serif))
                            .tracking(4)
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 16))

                    VStack(alignment: .leading, spacing: 10) {
                        Text("Commission this month")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                        Text("$\(String(format: "%.2f", commission))")
                            .font(.title)
                        Text("Paid on the 1st of next month.")
                            .font(.caption2)
                            .foregroundStyle(.tertiary)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding()
                    .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 16))

                    VStack(alignment: .leading, spacing: 10) {
                        Text("Content pack")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                        Link("Latest brief →", destination: URL(string: "https://github.com/calebhomwe/SKYDAZE/blob/main/research/STREETWEAR_PLAYBOOK.md")!)
                        Link("Shot list →", destination: URL(string: "https://github.com/calebhomwe/SKYDAZE")!)
                        Link("Audio direction →", destination: URL(string: "https://github.com/calebhomwe/SKYDAZE")!)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding()
                    .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 16))
                }
                .padding()
            }
            .navigationTitle("Creator")
        }
    }
}
