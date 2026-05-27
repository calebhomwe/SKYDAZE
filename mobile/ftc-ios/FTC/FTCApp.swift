import SwiftUI

@main
struct FTCApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .preferredColorScheme(.dark)
                .tint(Color(red: 0.85, green: 0.78, blue: 0.62)) // sand
        }
    }
}
