import SwiftUI

struct GalleryView: View {
    @State private var images: [UIImage] = []

    var body: some View {
        NavigationStack {
            ScrollView {
                if images.isEmpty {
                    ContentUnavailableView(
                        "No saved renders yet",
                        systemImage: "photo.stack",
                        description: Text("Generate a concept on the Generate tab to start your gallery.")
                    )
                    .padding(.top, 80)
                } else {
                    LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                        ForEach(0..<images.count, id: \.self) { idx in
                            Image(uiImage: images[idx])
                                .resizable()
                                .aspectRatio(contentMode: .fit)
                                .clipShape(RoundedRectangle(cornerRadius: 10))
                        }
                    }
                    .padding()
                }
            }
            .navigationTitle("Gallery")
            .onAppear(perform: load)
        }
    }

    private func load() {
        guard let docs = try? FileManager.default.url(for: .documentDirectory, in: .userDomainMask, appropriateFor: nil, create: true).appendingPathComponent("Generations") else {
            return
        }
        guard let files = try? FileManager.default.contentsOfDirectory(at: docs, includingPropertiesForKeys: nil) else { return }
        images = files.compactMap { url in
            guard let data = try? Data(contentsOf: url) else { return nil }
            return UIImage(data: data)
        }
    }
}
