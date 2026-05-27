import SwiftUI

struct ContentView: View {
    var body: some View {
        TabView {
            GenerateView()
                .tabItem { Label("Generate", systemImage: "sparkles") }
            GalleryView()
                .tabItem { Label("Gallery", systemImage: "photo.stack") }
            DropsView()
                .tabItem { Label("Drops", systemImage: "bag") }
            CreatorView()
                .tabItem { Label("Creator", systemImage: "person.fill.viewfinder") }
        }
    }
}
