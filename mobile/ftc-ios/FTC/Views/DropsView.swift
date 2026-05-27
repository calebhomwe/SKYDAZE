import SwiftUI

struct DropsView: View {
    let drops = [
        Drop(name: "Cornerstone", season: "2026 SS", pieces: 30, color: Color(red: 0.69, green: 0.55, blue: 0.43)),
        Drop(name: "Veil", season: "2026 SS", pieces: 28, color: Color(red: 0.21, green: 0.23, blue: 0.28)),
        Drop(name: "Wilderness", season: "2026 FW", pieces: 32, color: Color(red: 0.42, green: 0.45, blue: 0.36)),
    ]

    var body: some View {
        NavigationStack {
            List(drops) { drop in
                HStack(spacing: 16) {
                    RoundedRectangle(cornerRadius: 8)
                        .fill(drop.color)
                        .frame(width: 60, height: 80)
                    VStack(alignment: .leading, spacing: 4) {
                        Text(drop.name).font(.headline)
                        Text("\(drop.season) · \(drop.pieces) pieces").font(.caption).foregroundStyle(.secondary)
                    }
                    Spacer()
                    Image(systemName: "chevron.right").foregroundStyle(.tertiary)
                }
                .padding(.vertical, 6)
            }
            .navigationTitle("Drops")
        }
    }
}

struct Drop: Identifiable {
    let id = UUID()
    let name: String
    let season: String
    let pieces: Int
    let color: Color
}
