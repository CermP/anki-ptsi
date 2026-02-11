
import SwiftUI
import UniformTypeIdentifiers

// A helper struct to allow the file exporter to save our generated zip file.
struct ZipDocument: FileDocument {
    static var readableContentTypes: [UTType] = [.zip]
    var url: URL

    init(url: URL) {
        self.url = url
    }

    init(configuration: ReadConfiguration) throws {
        // This initializer is required but we won't use it.
        fatalError("init(configuration:) has not been implemented")
    }

    func fileWrapper(configuration: WriteConfiguration) throws -> FileWrapper {
        // Provides the zip file data to the system for saving.
        return try FileWrapper(url: url, options: .immediate)
    }
}


struct ContentView: View {
    @State private var outputMessage: String = "Welcome to Anki Companion!"
    @State private var isRunning: Bool = false
    
    // States for controlling the file dialogs
    @State private var isShowingImporter = false
    @State private var isShowingExporter = false
    @State private var documentToExport: ZipDocument?

    var body: some View {
        VStack {
            Text("Anki Companion")
                .font(.largeTitle)
                .padding()

            if isRunning {
                ProgressView()
                    .padding()
                Text("Running script...")
            } else {
                Button("Export Decks & Media...") {
                    exportAndZipDecks()
                }
                .padding()
                .fileExporter(
                    isPresented: $isShowingExporter,
                    document: documentToExport,
                    contentType: .zip,
                    defaultFilename: "Anki_Decks_Export.zip"
                ) { result in
                    switch result {
                    case .success(let url):
                        self.outputMessage = "Successfully saved export to \(url.path)"
                    case .failure(let error):
                        self.outputMessage = "Failed to save export: \(error.localizedDescription)"
                    }
                }

                Button("Import Deck from CSV...") {
                    isShowingImporter = true
                }
                .padding()
                .fileImporter(
                    isPresented: $isShowingImporter,
                    allowedContentTypes: [.commaSeparatedText]
                ) { result in
                    switch result {
                    case .success(let url):
                        // We need to access the file, so we secure access first.
                        if url.startAccessingSecurityScopedResource() {
                            defer { url.stopAccessingSecurityScopedResource() }
                            runPythonScript(named: "scripts/imports_decks.py", arguments: [url.path])
                        } else {
                            self.outputMessage = "Could not access the selected file."
                        }
                    case .failure(let error):
                        self.outputMessage = "Failed to select file: \(error.localizedDescription)"
                    }
                }
            }

            Divider()

            ScrollView {
                Text(outputMessage)
                    .font(.body)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding()
            }
            .frame(height: 200)
            .background(Color(.textBackgroundColor))
            .cornerRadius(8)
            
        }
        .padding()
        .frame(minWidth: 450, minHeight: 400)
    }
    
    private func exportAndZipDecks() {
        // Step 1: Run the export script.
        runPythonScript(named: "scripts/export_with_media.py") { success, output in
            if !success {
                self.outputMessage = "Export script failed:\n\(output)"
                return
            }
            
            self.outputMessage = "Export successful. Now creating zip archive..."
            
            // Step 2: On success, zip the results.
            zipExportedFiles { zipURL in
                guard let zipURL = zipURL else {
                    self.outputMessage = "Error: Failed to create zip archive."
                    return
                }
                
                // Step 3: Present the save dialog (file exporter).
                self.documentToExport = ZipDocument(url: zipURL)
                self.isShowingExporter = true
            }
        }
    }
    
    private func zipExportedFiles(completion: @escaping (URL?) -> Void) {
        guard let resourcePath = Bundle.main.resourcePath else {
            completion(nil)
            return
        }

        let tempURL = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString).appendingPathExtension("zip")
        
        let task = Process()
        task.executableURL = URL(fileURLWithPath: "/usr/bin/zip")
        // The -j flag junks paths, putting all files at the root of the zip.
        // We cd into the resource path to use relative paths.
        task.arguments = ["-r", tempURL.path, "decks", "media"]
        task.currentDirectoryPath = resourcePath

        task.terminationHandler = { process in
            DispatchQueue.main.async {
                if process.terminationStatus == 0 {
                    completion(tempURL)
                } else {
                    completion(nil)
                }
            }
        }
        
        do {
            try task.run()
        } catch {
            DispatchQueue.main.async {
                self.outputMessage = "Failed to run zip command: \(error.localizedDescription)"
                completion(nil)
            }
        }
    }

    private func runPythonScript(named scriptPath: String, arguments: [String] = [], completion: ((Bool, String) -> Void)? = nil) {
        isRunning = true
        if completion == nil { // Only show this for simple runs
             outputMessage = "Running \(scriptPath)..."
        }

        // --- Python 3 Check ---
        let checkTask = Process()
        checkTask.executableURL = URL(fileURLWithPath: "/usr/bin/env")
        checkTask.arguments = ["python3", "-c", "import sys; print(sys.executable)"]
        let checkPipe = Pipe()
        checkTask.standardOutput = checkPipe
        do {
            try checkTask.run()
            checkTask.waitUntilExit()
            if checkTask.terminationStatus != 0 {
                 throw NSError(domain: "PythonCheck", code: 1, userInfo: [NSLocalizedDescriptionKey: "Python 3 executable not found."])
            }
        } catch {
            self.outputMessage = "Python 3 is not installed or not in your PATH. Please install Python 3 to continue."
            self.isRunning = false
            completion?(false, outputMessage)
            return
        }
        // --- End Check ---

        let pathComponents = scriptPath.split(separator: "/").map(String.init)
        guard let scriptFilename = pathComponents.last else {
            self.outputMessage = "Invalid script path."
            self.isRunning = false
            completion?(false, outputMessage)
            return
        }
        let subdirectory = pathComponents.dropLast().joined(separator: "/")
        let scriptName = scriptFilename.replacingOccurrences(of: ".py", with: "")

        guard let scriptURL = Bundle.main.url(forResource: scriptName, withExtension: "py", subdirectory: subdirectory) else {
            self.outputMessage = "Could not find script \(scriptPath) in the app bundle."
            isRunning = false
            completion?(false, outputMessage)
            return
        }

        let runTask = Process()
        runTask.executableURL = URL(fileURLWithPath: "/usr/bin/env")
        runTask.arguments = ["python3", scriptURL.path] + arguments
        
        runTask.currentDirectoryURL = Bundle.main.resourceURL
        
        let outputPipe = Pipe()
        let errorPipe = Pipe()
        runTask.standardOutput = outputPipe
        runTask.standardError = errorPipe

        runTask.terminationHandler = { process in
            DispatchQueue.main.async {
                self.isRunning = false
                let outputData = outputPipe.fileHandleForReading.readDataToEndOfFile()
                let errorData = errorPipe.fileHandleForReading.readDataToEndOfFile()
                let output = String(data: outputData, encoding: .utf8) ?? ""
                let errorOutput = String(data: errorData, encoding: .utf8) ?? ""
                let fullOutput = output + "\n" + errorOutput

                if process.terminationStatus == 0 {
                    if completion == nil { self.outputMessage = "Script finished successfully:\n\(output)" }
                    completion?(true, output)
                } else {
                    if completion == nil { self.outputMessage = "Script failed:\n\(fullOutput)" }
                    completion?(false, fullOutput)
                }
            }
        }

        do {
            try runTask.run()
        } catch {
            self.outputMessage = "Failed to start script: \(error.localizedDescription)"
            isRunning = false
            completion?(false, outputMessage)
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
