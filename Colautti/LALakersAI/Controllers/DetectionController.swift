import UIKit
import Vision
import AVFoundation
import CoreMedia
import VideoToolbox

class DetectionController: UIViewController {
  @IBOutlet var videoPreview: UIView!
  @IBOutlet var timeLabel: UILabel!
    
  var sharedData = SharedData.loadData(start: true)

  let model = Model()

  var videoCapture: VideoCapture!
  var request: VNCoreMLRequest!
  var startTimes: [CFTimeInterval] = []

  var boundingBoxes = [BoundingBox]()
    
  var lastTimeShowingGoal: CFTimeInterval?
  let secondsToShowGoal = 3

  let ciContext = CIContext()
  var resizedPixelBuffer: CVPixelBuffer?

  var framesDone = 0
  var frameCapturingStartTime = CACurrentMediaTime()
  let semaphore = DispatchSemaphore(value: 2)

  override func viewDidLoad() {
    super.viewDidLoad()
    
    timeLabel.text = ""

    setUpBoundingBoxes()
    setUpCoreImage()
    setUpVision()
    setUpCamera()

    frameCapturingStartTime = CACurrentMediaTime()
  }
    
    override func viewWillDisappear(_ animated: Bool) {
        if videoCapture != nil {
            videoCapture.stop()
        }
    }
    
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        sharedData.saveData()
        if segue.destination is FeaturesController {
            let featuresController = segue.destination as? FeaturesController
            featuresController?.detectionController = self
        }
    }
    
    func reloadData() {
        sharedData = SharedData.loadData(start: false)
    }

  override func didReceiveMemoryWarning() {
    super.didReceiveMemoryWarning()
    print(#function)
  }

  func setUpBoundingBoxes() {
    for _ in 0..<Model.maxBoundingBoxes {
      boundingBoxes.append(BoundingBox())
    }
  }

  func setUpCoreImage() {
    let status = CVPixelBufferCreate(nil, Model.inputWidth, Model.inputHeight,
                                     kCVPixelFormatType_32BGRA, nil,
                                     &resizedPixelBuffer)
    if status != kCVReturnSuccess {
      print("Error: could not create resized pixel buffer", status)
    }
  }

  func setUpVision() {
    guard let visionModel = try? VNCoreMLModel(for: model.currentModel.model) else {
      print("Error: could not create Vision model")
      return
    }

    request = VNCoreMLRequest(model: visionModel, completionHandler: {_,_ in })
    request.imageCropAndScaleOption = .scaleFill
  }

  func setUpCamera() {
    videoCapture = VideoCapture()
    videoCapture.delegate = self
    videoCapture.fps = 50
    videoCapture.setUp(sessionPreset: AVCaptureSession.Preset.vga640x480) { success in
      if success {
        if let previewLayer = self.videoCapture.previewLayer {
          self.videoPreview.layer.addSublayer(previewLayer)
          self.resizePreviewLayer()
        }

        for box in self.boundingBoxes {
          box.addToLayer(self.videoPreview.layer)
        }

        self.videoCapture.start()
      }
    }
  }

  override func viewWillLayoutSubviews() {
    super.viewWillLayoutSubviews()
    resizePreviewLayer()
  }

  override var preferredStatusBarStyle: UIStatusBarStyle {
    return .lightContent
  }

  func resizePreviewLayer() {
    videoCapture.previewLayer?.frame = videoPreview.bounds
  }

  func predict(pixelBuffer: CVPixelBuffer) {
    let startTime = CACurrentMediaTime()
    guard let resizedPixelBuffer = resizedPixelBuffer else { return }
    let ciImage = CIImage(cvPixelBuffer: pixelBuffer)
    let sx = CGFloat(Model.inputWidth) / CGFloat(CVPixelBufferGetWidth(pixelBuffer))
    let sy = CGFloat(Model.inputHeight) / CGFloat(CVPixelBufferGetHeight(pixelBuffer))
    let scaleTransform = CGAffineTransform(scaleX: sx, y: sy)
    let scaledImage = ciImage.transformed(by: scaleTransform)
    ciContext.render(scaledImage, to: resizedPixelBuffer)
    if var boundingBoxes = try? model.predict(image: resizedPixelBuffer) {
      let elapsed = CACurrentMediaTime() - startTime
      //let startProcessingTime = CACurrentMediaTime()
      boundingBoxes = sharedData.filterPredictions(predictions: boundingBoxes)
      sharedData.updateLineUp(predictions: boundingBoxes)
      let goal = sharedData.goalVerify(predictions: boundingBoxes)
      sharedData.ballPossessor(predictions: boundingBoxes)
      sharedData.detectPass()
      let possiblePossessor = sharedData.lastPossiblePossessor()
      //print(String(format: "Processing done in %.5f seconds", CACurrentMediaTime() - startProcessingTime))
      showOnMainThread(boundingBoxes, elapsed, goal: goal, player: possiblePossessor)
    }
  }
    
    let secondsFPSUpdate = 0.5
    var lastFPSUpdate: CFTimeInterval?

    func showOnMainThread(_ boundingBoxes: [Model.Prediction], _ elapsed: CFTimeInterval, goal: Bool, player: String?) {
    DispatchQueue.main.async {
      self.show(predictions: boundingBoxes)
      self.showOrHideGoal(goal: goal, player: player)
      let fps = self.measureFPS()
      if self.lastFPSUpdate == nil ||
            CACurrentMediaTime() - self.lastFPSUpdate! >= self.secondsFPSUpdate {
        self.timeLabel.text = String(format: "%.1f FPS", fps)
        self.lastFPSUpdate = CACurrentMediaTime()
      }

      self.semaphore.signal()
    }
  }
    
    @IBOutlet weak var goalBall: UIImageView!
    @IBOutlet weak var goalLabel: UILabel!
    
    var lastColorChange: CFTimeInterval?
    let secondsChangingColor = 0.25
    
    func showOrHideGoal(goal: Bool, player: String?) {
        if goalBall != nil && goalLabel != nil {
            if goal && (sharedData.showAllGoals || player != nil) {
                if player == nil {
                    goalLabel.text = "Canestro!"
                } else {
                    goalLabel.text = SharedData.extendedNameToShow(player: player!)
                }
                goalLabel.isHidden = false
                goalBall.isHidden = false
                lastTimeShowingGoal = CACurrentMediaTime()
            } else if !goalBall.isHidden {
                if lastTimeShowingGoal != nil && Int(CACurrentMediaTime() - lastTimeShowingGoal!) >= secondsToShowGoal {
                    goalBall.isHidden = true
                    goalLabel.isHidden = true
                } else if lastColorChange == nil || CACurrentMediaTime() - lastColorChange! >= secondsChangingColor {
                    goalLabel.textColor = goalLabel.textColor == UIColor.systemOrange ? UIColor.systemPurple : UIColor.systemOrange
                    lastColorChange = CACurrentMediaTime()
                }
            }
        }
    }

  func measureFPS() -> Double {
    framesDone += 1
    let frameCapturingElapsed = CACurrentMediaTime() - frameCapturingStartTime
    let currentFPSDelivered = Double(framesDone) / frameCapturingElapsed
    if frameCapturingElapsed > 1 {
      framesDone = 0
      frameCapturingStartTime = CACurrentMediaTime()
    }
    return currentFPSDelivered
  }

  func show(predictions: [Model.Prediction]) {
    for i in 0..<boundingBoxes.count {
      boundingBoxes[i].hide()
      if i < predictions.count {
        let prediction = predictions[i]
        if !sharedData.predictionToShow(prediction: prediction) {
            continue
        }

        let width = view.bounds.width
        let height = width * 4 / 3
        let scaleX = width / CGFloat(Model.inputWidth)
        let scaleY = height / CGFloat(Model.inputHeight)
        let top = (view.bounds.height - height) / 2

        let label = String(format: "%@", labels[prediction.classIndex])
        var rect = prediction.rect
        rect.origin.x *= scaleX
        rect.origin.y *= scaleY
        rect.origin.y += top
        rect.size.width *= scaleX
        rect.size.height *= scaleY

        boundingBoxes[i].show(frame: rect, label: label)
      }
    }
  }
}

extension DetectionController: VideoCaptureDelegate {
  func videoCapture(_ capture: VideoCapture, didCaptureVideoFrame pixelBuffer: CVPixelBuffer?, timestamp: CMTime) {
    semaphore.wait()
    
    if let pixelBuffer = pixelBuffer {
      DispatchQueue.global().async {
        self.predict(pixelBuffer: pixelBuffer)
      }
    }
  }
}
