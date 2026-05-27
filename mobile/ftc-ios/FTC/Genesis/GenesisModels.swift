import Foundation
import SwiftUI

// MARK: - World

struct GenesisWorld: Identifiable, Hashable {
    let id: String
    let name: String
    let kind: WorldKind
    let biome: Biome
    let palette: [Color]
    let region: String
    let parable: String

    enum WorldKind: String { case biblical, modern, diaspora }
    enum Biome: String {
        case cedarForest = "cedar-forest"
        case desertSand = "desert-sand"
        case marbleCity = "marble-city"
        case concreteSuburb = "concrete-suburb"
        case snowMountain = "snow-mountain"
        case oliveGrove = "olive-grove"
        case coastalPier = "coastal-pier"
        case riverValley = "river-valley"
        case rooftopGarden = "rooftop-garden"
        case stoneCourtyard = "stone-courtyard"
    }
}

extension GenesisWorld {
    static let eden = GenesisWorld(
        id: "W-001",
        name: "Eden",
        kind: .biblical,
        biome: .cedarForest,
        palette: [
            Color(red: 0.102, green: 0.165, blue: 0.122),
            Color(red: 0.243, green: 0.361, blue: 0.259),
            Color(red: 0.533, green: 0.639, blue: 0.482),
            Color(red: 0.835, green: 0.867, blue: 0.722),
            Color(red: 0.953, green: 0.933, blue: 0.859),
        ],
        region: "The First Garden",
        parable: "What was given without asking is what we forget to thank for."
    )

    static let scarborough = GenesisWorld(
        id: "W-101",
        name: "Scarborough",
        kind: .modern,
        biome: .concreteSuburb,
        palette: [
            Color(red: 0.055, green: 0.078, blue: 0.090),
            Color(red: 0.165, green: 0.188, blue: 0.212),
            Color(red: 0.420, green: 0.439, blue: 0.467),
            Color(red: 0.706, green: 0.725, blue: 0.741),
            Color(red: 0.894, green: 0.902, blue: 0.898),
        ],
        region: "Ontario · the eastern suburbs of Toronto",
        parable: "Bus-shelter prayer at 5:47 AM. The faithful keep their hours."
    )

    static let starterWorlds: [GenesisWorld] = [.eden, .scarborough]
}

// MARK: - Player

@MainActor
final class GenesisPlayer: ObservableObject {
    @Published var position: CGPoint = .init(x: 0, y: 0)
    @Published var restraint: Int = 5
    @Published var weight: Int = 0
    @Published var inventory: [GenesisItem] = []
    @Published var parableFragments: [String] = []
    @Published var lastStepTime: Date = Date()

    func step(to point: CGPoint) {
        let now = Date()
        let interval = now.timeIntervalSince(lastStepTime)
        // Slow walking increases restraint; rushing decreases it.
        if interval > 1.2 {
            restraint = min(10, restraint + 1)
        } else if interval < 0.4 {
            restraint = max(0, restraint - 1)
        }
        position = point
        lastStepTime = now
    }

    func collect(_ item: GenesisItem) {
        guard weight + item.weight <= 10 else { return }
        inventory.append(item)
        weight += item.weight
    }
}

// MARK: - Item

struct GenesisItem: Identifiable, Hashable {
    let id: String
    let name: String
    let weight: Int
    let rarity: Rarity
    let lore: String

    enum Rarity: String { case common, uncommon, rare, sacred }
}

extension GenesisItem {
    static let figLeaf = GenesisItem(id: "I-001", name: "Fig Leaf", weight: 1, rarity: .common,
                                     lore: "What we sewed when we knew we were seen.")
    static let riverStone = GenesisItem(id: "I-002", name: "River Stone", weight: 2, rarity: .common,
                                        lore: "Smooth from a thousand years of being moved.")
    static let oliveSprig = GenesisItem(id: "I-003", name: "Olive Sprig", weight: 1, rarity: .uncommon,
                                        lore: "Dove brought it back. The flood admitted defeat.")
    static let edenItems: [GenesisItem] = [.figLeaf, .riverStone, .oliveSprig]
}
