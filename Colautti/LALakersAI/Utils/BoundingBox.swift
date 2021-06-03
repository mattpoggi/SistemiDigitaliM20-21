import Foundation
import UIKit

class BoundingBox {
  let shapeLayer: CAShapeLayer
  let textLayer: CATextLayer

  init() {
    shapeLayer = CAShapeLayer()
    shapeLayer.fillColor = UIColor.clear.cgColor
    shapeLayer.lineWidth = 1
    shapeLayer.isHidden = true

    textLayer = CATextLayer()
    textLayer.foregroundColor = UIColor.black.cgColor
    textLayer.isHidden = true
    textLayer.contentsScale = UIScreen.main.scale
    textLayer.fontSize = 14
    textLayer.font = UIFont(name: "Avenir", size: textLayer.fontSize)
    textLayer.alignmentMode = CATextLayerAlignmentMode.center
  }

  func addToLayer(_ parent: CALayer) {
    parent.addSublayer(shapeLayer)
    parent.addSublayer(textLayer)
  }

  func show(frame: CGRect, label: String) {
    CATransaction.setDisableActions(true)
    
    var textOrigin: CGPoint
    let attributes = [
      NSAttributedString.Key.font: textLayer.font as Any
    ]
    let textRect = label.boundingRect(with: CGSize(width: 400, height: 100),
                                      options: .truncatesLastVisibleLine,
                                      attributes: attributes, context: nil)
    let textSize = CGSize(width: textRect.width + 12, height: textRect.height)
    
    if label == "ball" || label == "basket" {
        let path = UIBezierPath(rect: frame)
        shapeLayer.path = path.cgPath
        shapeLayer.fillColor =  UIColor.clear.cgColor
        shapeLayer.strokeColor = (label == "ball" ? UIColor.init(.orange) : UIColor.init(.white)).cgColor
        textLayer.string = label == "ball" ? "Ball" : "Basket"
        textLayer.backgroundColor = (label == "ball" ? UIColor.init(.orange) : UIColor.init(.white)).cgColor
        textLayer.foregroundColor = UIColor.init(.black).cgColor
        textOrigin = CGPoint(x: frame.origin.x - 2, y: frame.origin.y - textSize.height)
        textLayer.cornerRadius = 2
    } else {
        let triangle = UIBezierPath()
        let b:CGFloat = 8
        let h:CGFloat = 12
        let triangleOrigin = CGPoint(x: frame.origin.x + frame.width / 2 - b / 2, y: frame.origin.y)
        triangle.move(to: triangleOrigin)
        triangle.addLine(to: CGPoint(x: triangleOrigin.x + b, y: triangleOrigin.y))
        triangle.addLine(to: CGPoint(x: triangleOrigin.x + b / 2, y: triangleOrigin.y + h))
        triangle.addLine(to: triangleOrigin)
        shapeLayer.path = triangle.cgPath
        shapeLayer.fillColor = UIColor.init(.blue).cgColor
        shapeLayer.strokeColor = UIColor.init(.white).cgColor
        shapeLayer.borderWidth = 6
        textLayer.string = SharedData.labelToShowOnlySurname(player: label)
        textLayer.foregroundColor = UIColor.init(.white).cgColor
        textLayer.backgroundColor = UIColor.init(.blue).cgColor
        textLayer.fontSize = 12
        textOrigin = CGPoint(x: triangleOrigin.x - textRect.width / 2, y: triangleOrigin.y - textSize.height - 3)
        textLayer.cornerRadius = 4
    }
    shapeLayer.isHidden = false
    textLayer.isHidden = false
    textLayer.frame = CGRect(origin: textOrigin, size: textSize)
  }

  func hide() {
    shapeLayer.isHidden = true
    textLayer.isHidden = true
  }
}
