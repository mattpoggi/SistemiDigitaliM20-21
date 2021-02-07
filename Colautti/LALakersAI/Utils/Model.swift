import Foundation
import UIKit
import CoreML

class Model {
  public static let inputWidth = 416
  public static let inputHeight = 416
  public static let maxBoundingBoxes = 8 // 5 players + 1 ball + 2 baskets
    
  let currentModel = LakersModelDetector()
    
  let confidenceThreshold: Float = 0.5
  let iouThreshold: Float = 0.5

  public init() { }

  public func predict(image: CVPixelBuffer) throws -> [Prediction] {
    if let output = try? currentModel.prediction(input: image) {
      return computeBoundingBoxes(features: [output.output13, output.output26, output.output52])
    } else {
      return []
    }
  }
    
    struct Prediction {
      let classIndex: Int
      let score: Float
      let rect: CGRect
    }

  public func computeBoundingBoxes(features: [MLMultiArray]) -> [Prediction] {
    var predictions = [Prediction]()

    let blockSize: Float = 32
    let boxesPerCell = 3
    let indexStride = [2,3,4]
    let numClasses = 19
    
    let gridHeight = [13, 26, 52]
    let gridWidth = [13, 26, 52]
    
    var featurePointer: UnsafeMutablePointer<Double>
    var channelStride: Int
    var yStride: Int
    var xStride: Int
    
    func offset(_ channel: Int, _ x: Int, _ y: Int) -> Int {
      return channel*channelStride + y*yStride + x*xStride
    }

    for i in 0..<3 {
        featurePointer = UnsafeMutablePointer<Double>(OpaquePointer(features[i].dataPointer))
        
        channelStride = features[i].strides[indexStride[0]].intValue
        yStride = features[i].strides[indexStride[1]].intValue
        xStride = features[i].strides[indexStride[2]].intValue
        
        for cy in 0..<gridHeight[i] {
            for cx in 0..<gridWidth[i] {
                for b in 0..<boxesPerCell {
                    
                    let channel = b*(numClasses + 5)

                    let tx = Float(featurePointer[offset(channel    , cx, cy)])
                    let ty = Float(featurePointer[offset(channel + 1, cx, cy)])
                    let tw = Float(featurePointer[offset(channel + 2, cx, cy)])
                    let th = Float(featurePointer[offset(channel + 3, cx, cy)])
                    let tc = Float(featurePointer[offset(channel + 4, cx, cy)])
                    

                    let scale = powf(2.0,Float(i))
                    let x = (Float(cx) * blockSize + sigmoid(tx))/scale
                    let y = (Float(cy) * blockSize + sigmoid(ty))/scale
                    
                    let w = exp(tw) * anchors[i][2*b    ]
                    let h = exp(th) * anchors[i][2*b + 1]
                    
                    let confidence = sigmoid(tc)
                    
                    var classes = [Float](repeating: 0, count: numClasses)
                    for c in 0..<numClasses {
                        classes[c] = Float(featurePointer[offset(channel + 5 + c, cx, cy)])
                    }
                    classes = softmax(classes)
                    
                    let (detectedClass, bestClassScore) = classes.argmax()
                    let confidenceInClass = bestClassScore * confidence
                    
                    if confidenceInClass > confidenceThreshold {
                        let rect = CGRect(x: CGFloat(x - w/2), y: CGFloat(y - h/2),
                                          width: CGFloat(w), height: CGFloat(h))
                        
                        let prediction = Prediction(classIndex: detectedClass,
                                                    score: confidenceInClass,
                                                    rect: rect)
                        predictions.append(prediction)
                    }
                }
            }
        }
    }
    
    return nonMaxSuppression(boxes: predictions, limit: Model.maxBoundingBoxes, threshold: iouThreshold)
  }
}
