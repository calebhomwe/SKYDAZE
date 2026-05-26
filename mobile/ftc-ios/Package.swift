// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "FTC",
    platforms: [
        .iOS(.v17),
        .macOS(.v14),
        .visionOS(.v1),
    ],
    products: [
        .library(name: "FTC", targets: ["FTC"]),
    ],
    dependencies: [
        // Pure SwiftUI for now — no external dependencies for v1.0.
        // Add Alamofire / Kingfisher later if needed.
    ],
    targets: [
        .target(
            name: "FTC",
            path: "FTC",
            exclude: ["Resources/Secrets.plist.example"],
            resources: [
                .process("Resources"),
            ]
        ),
        .testTarget(
            name: "FTCTests",
            dependencies: ["FTC"],
            path: "Tests/FTCTests"
        ),
    ]
)
