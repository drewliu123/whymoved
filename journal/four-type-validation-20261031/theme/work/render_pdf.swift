import Foundation
import PDFKit
import AppKit
let path=CommandLine.arguments[1]
let index=Int(CommandLine.arguments[2])!-1
let out=CommandLine.arguments[3]
let pdf=PDFDocument(url:URL(fileURLWithPath:path))!
let page=pdf.page(at:index)!
let image=page.thumbnail(of:NSSize(width:1500,height:1000),for:.mediaBox)
let data=NSBitmapImageRep(data:image.tiffRepresentation!)!.representation(using:.png,properties:[:])!
try data.write(to:URL(fileURLWithPath:out))
print(out)
