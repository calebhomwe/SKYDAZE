import SwiftUI

/// Root view for the GENESIS game module. World list → walk into a world.
/// Designed as a sibling to the FTC shopping app, sharing SwiftUI infrastructure
/// but living in its own module.
struct GenesisRootView: View {
    @State private var path = NavigationPath()
    let worlds: [GenesisWorld] = GenesisWorld.starterWorlds

    var body: some View {
        NavigationStack(path: $path) {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("GENESIS")
                            .font(.system(.largeTitle, design: .serif))
                            .tracking(12)
                        Text("WALK SLOWLY · CARRY LESS · BUILD TRUE")
                            .font(.caption2)
                            .tracking(3)
                            .foregroundStyle(.secondary)
                    }
                    .padding(.horizontal)
                    .padding(.top, 24)

                    ForEach(worlds) { world in
                        WorldCard(world: world)
                            .onTapGesture { path.append(world) }
                    }
                    .padding(.horizontal)
                }
            }
            .navigationDestination(for: GenesisWorld.self) { world in
                if world.id == "W-001" {
                    EdenScene()
                } else {
                    PlaceholderWorld(world: world)
                }
            }
        }
    }
}

private struct WorldCard: View {
    let world: GenesisWorld
    var body: some View {
        HStack(spacing: 14) {
            ZStack {
                LinearGradient(colors: world.palette,
                               startPoint: .topLeading,
                               endPoint: .bottomTrailing)
                Image(systemName: iconName)
                    .font(.title2)
                    .foregroundStyle(.white.opacity(0.85))
            }
            .frame(width: 72, height: 96)
            .clipShape(RoundedRectangle(cornerRadius: 12))

            VStack(alignment: .leading, spacing: 4) {
                Text(world.name)
                    .font(.system(.headline, design: .serif))
                Text(world.region)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Text("\u{201C}\(world.parable)\u{201D}")
                    .font(.caption2.italic())
                    .foregroundStyle(.tertiary)
                    .lineLimit(2)
                    .padding(.top, 2)
            }
            Spacer()
            Image(systemName: "chevron.right")
                .foregroundStyle(.tertiary)
        }
        .padding(12)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 14))
    }

    private var iconName: String {
        switch world.biome {
        case .cedarForest: return "tree.fill"
        case .concreteSuburb: return "building.2.fill"
        case .desertSand: return "sun.haze.fill"
        case .marbleCity: return "building.columns.fill"
        case .snowMountain: return "mountain.2.fill"
        case .oliveGrove: return "leaf.fill"
        case .coastalPier: return "water.waves"
        case .riverValley: return "drop.fill"
        case .rooftopGarden: return "house.fill"
        case .stoneCourtyard: return "square.stack.3d.up.fill"
        }
    }
}

private struct PlaceholderWorld: View {
    let world: GenesisWorld
    var body: some View {
        VStack(spacing: 12) {
            Text(world.name)
                .font(.system(.largeTitle, design: .serif))
            Text("Coming soon")
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(LinearGradient(colors: world.palette, startPoint: .top, endPoint: .bottom))
    }
}
