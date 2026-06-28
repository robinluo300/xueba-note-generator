#!/usr/bin/env swift

import Cocoa
import Vision

guard CommandLine.arguments.count > 1 else {
    print("请拖入图片文件")
    exit(1)
}

let imagePath = CommandLine.arguments[1]
let imageURL = URL(fileURLWithPath: imagePath)

guard let image = NSImage(contentsOf: imageURL),
      let tiffData = image.tiffRepresentation,
      let bitmap = NSBitmapImageRep(data: tiffData),
      let cgImage = bitmap.cgImage else {
    print("无法读取图片")
    exit(1)
}

let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.recognitionLanguages = ["zh-Hans", "en-US"]
request.usesLanguageCorrection = true

let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
try? handler.perform([request])

var lines: [String] = []
if let results = request.results {
    for result in results {
        if let candidate = result.topCandidates(1).first {
            lines.append(candidate.string)
        }
    }
}

if lines.isEmpty {
    print("未识别到文字")
    exit(1)
}

let text = lines.joined(separator: "\n")
print(text)
