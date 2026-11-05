import Foundation
import PDFKit
for path in CommandLine.arguments.dropFirst() {
 guard let pdf = PDFDocument(url: URL(fileURLWithPath: path)) else { fatalError("Cannot read PDF: \(path)") }
 var text = "pages=\(pdf.pageCount)\n"
 for i in 0..<pdf.pageCount { text += "\n=== PDF PAGE \(i+1) ===\n" + (pdf.page(at:i)?.string ?? "[no text]") + "\n" }
 let dest = URL(fileURLWithPath:path).deletingPathExtension().appendingPathExtension("txt")
 try text.write(to:dest, atomically:true, encoding:.utf8)
 print("\(path): pages=\(pdf.pageCount) -> \(dest.path)")
}
