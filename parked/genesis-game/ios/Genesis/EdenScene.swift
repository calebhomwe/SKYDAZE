import SwiftUI

/// First playable vertical slice: walk through Eden, collect items, watch
/// restraint stat respond to walking pace. No combat, no score, no HUD chrome.
struct EdenScene: View {
    @StateObject private var player = GenesisPlayer()
    @State private var items: [PlacedItem] = EdenScene.makeStartingItems()
    @State private var collectedToastItem: GenesisItem?

    var body: some View {
        GeometryReader { geo in
            ZStack {
                // Sky + ground
                LinearGradient(
                    colors: GenesisWorld.eden.palette.prefix(3).map { $0 },
                    startPoint: .top,
                    endPoint: .bottom
                )
                .ignoresSafeArea()

                // Trees (decorative)
                ForEach(0..<22, id: \.self) { i in
                    Tree(palette: GenesisWorld.eden.palette)
                        .frame(width: 28 + CGFloat((i % 5) * 6),
                               height: 60 + CGFloat((i % 7) * 6))
                        .position(
                            x: CGFloat(((i * 67) % Int(geo.size.width)) | 0),
                            y: CGFloat(((i * 113) % Int(geo.size.height - 200)) + 100)
                        )
                        .opacity(0.75)
                }

                // Items the player can collect
                ForEach(items) { placed in
                    ItemPickup(item: placed.item)
                        .position(placed.position)
                        .onTapGesture {
                            collect(placed, at: placed.position)
                        }
                }

                // Player
                PlayerSprite()
                    .position(player.position == .zero
                              ? CGPoint(x: geo.size.width / 2, y: geo.size.height / 2)
                              : player.position)
                    .animation(.easeOut(duration: 0.45), value: player.position)

                // World title overlay
                VStack(alignment: .leading, spacing: 4) {
                    Text("GENESIS · \(GenesisWorld.eden.id)")
                        .font(.caption2)
                        .tracking(4)
                        .opacity(0.7)
                    Text(GenesisWorld.eden.name.uppercased())
                        .font(.system(.title2, design: .serif))
                        .tracking(6)
                    Text("\u{201C}\(GenesisWorld.eden.parable)\u{201D}")
                        .font(.caption.italic())
                        .opacity(0.7)
                        .padding(.top, 4)
                }
                .foregroundStyle(.white)
                .padding()
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(.ultraThinMaterial)
                .frame(maxHeight: .infinity, alignment: .top)

                // Stats overlay (bottom)
                HStack(spacing: 24) {
                    StatPill(label: "Restraint", value: player.restraint, max: 10)
                    StatPill(label: "Weight", value: player.weight, max: 10)
                    StatPill(label: "Carried", value: player.inventory.count, max: 10)
                }
                .padding(.horizontal)
                .padding(.vertical, 10)
                .background(.ultraThinMaterial)
                .clipShape(Capsule())
                .padding(.bottom, 36)
                .frame(maxHeight: .infinity, alignment: .bottom)

                // Toast when an item is picked up
                if let toast = collectedToastItem {
                    Text("Picked up · \(toast.name)")
                        .font(.caption.weight(.medium))
                        .padding(.horizontal, 14).padding(.vertical, 8)
                        .background(.ultraThinMaterial)
                        .clipShape(Capsule())
                        .transition(.opacity.combined(with: .move(edge: .top)))
                        .padding(.top, 140)
                        .frame(maxHeight: .infinity, alignment: .top)
                }
            }
            .contentShape(Rectangle())
            .onTapGesture { location in
                player.step(to: location)
            }
        }
        .navigationTitle("")
        .navigationBarHidden(true)
    }

    private func collect(_ placed: PlacedItem, at point: CGPoint) {
        guard let idx = items.firstIndex(of: placed) else { return }
        // Player must be near the item to collect.
        let dx = placed.position.x - player.position.x
        let dy = placed.position.y - player.position.y
        let distance = (dx * dx + dy * dy).squareRoot()
        if distance > 80 {
            // Walk toward it first.
            player.step(to: placed.position)
            return
        }
        player.collect(placed.item)
        items.remove(at: idx)
        withAnimation { collectedToastItem = placed.item }
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
            withAnimation { collectedToastItem = nil }
        }
    }

    static func makeStartingItems() -> [PlacedItem] {
        [
            PlacedItem(item: .figLeaf, position: CGPoint(x: 90, y: 320)),
            PlacedItem(item: .riverStone, position: CGPoint(x: 280, y: 540)),
            PlacedItem(item: .oliveSprig, position: CGPoint(x: 220, y: 220)),
        ]
    }
}

private struct PlacedItem: Identifiable, Hashable {
    let id = UUID()
    let item: GenesisItem
    let position: CGPoint
}

// MARK: - Sprites

private struct PlayerSprite: View {
    var body: some View {
        ZStack {
            Circle()
                .fill(Color.white.opacity(0.85))
                .frame(width: 18, height: 18)
                .shadow(color: .white.opacity(0.3), radius: 12)
            Circle()
                .stroke(Color.white.opacity(0.6), lineWidth: 1)
                .frame(width: 28, height: 28)
        }
    }
}

private struct Tree: View {
    let palette: [Color]
    var body: some View {
        ZStack {
            Ellipse()
                .fill(palette[1])
                .opacity(0.6)
                .frame(width: 40, height: 6)
                .offset(y: 28)
            Rectangle()
                .fill(palette[1])
                .frame(width: 3, height: 18)
                .offset(y: 18)
            Circle()
                .fill(palette[2])
                .opacity(0.95)
            Circle()
                .fill(palette[3])
                .opacity(0.45)
                .scaleEffect(0.5)
                .offset(x: -6, y: -8)
        }
    }
}

private struct ItemPickup: View {
    let item: GenesisItem
    var body: some View {
        ZStack {
            Circle()
                .fill(itemColor.opacity(0.4))
                .frame(width: 38, height: 38)
            Circle()
                .stroke(itemColor, lineWidth: 1.2)
                .frame(width: 22, height: 22)
            Text(item.name.first.map(String.init) ?? "•")
                .font(.caption.bold())
                .foregroundStyle(.white)
        }
    }

    var itemColor: Color {
        switch item.rarity {
        case .common: return Color(red: 0.85, green: 0.85, blue: 0.78)
        case .uncommon: return Color(red: 0.55, green: 0.69, blue: 0.55)
        case .rare: return Color(red: 0.85, green: 0.76, blue: 0.55)
        case .sacred: return Color(red: 0.95, green: 0.92, blue: 0.78)
        }
    }
}

private struct StatPill: View {
    let label: String
    let value: Int
    let max: Int
    var body: some View {
        VStack(spacing: 2) {
            Text(label.uppercased())
                .font(.system(size: 9, weight: .medium))
                .tracking(2)
                .foregroundStyle(.secondary)
            Text("\(value)/\(max)")
                .font(.caption.weight(.medium).monospacedDigit())
        }
    }
}

#Preview {
    EdenScene()
}
