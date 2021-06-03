//
//  HomeViewController.swift
//  SistemiDigitali
//
//  Created by Dario De Nardi on 04/02/21.
//

import UIKit
import AVFoundation
import CoreMedia
import Alamofire
import SwiftyJSON

class HomeViewController: UIViewController, AVAudioRecorderDelegate, AVAudioPlayerDelegate {
    
    @IBOutlet weak var recordLabel: UILabel!
    @IBOutlet weak var timerLabel: UILabel!
    @IBOutlet weak var recordButton: UIButton!
    @IBOutlet weak var recordImage: UIImageView!
    
    var db: DBHelper!
    
    var audioRecorder: AVAudioRecorder!
    var audioPlayer : AVAudioPlayer!
    var meterTimer:Timer!
    var isAudioRecordingGranted: Bool!
    var isPlaying = false
    var fileName = ""
    
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view.
        
        self.recordLabel.font = UIFont(name: "Arlon-Regular", size: 22)
        self.recordLabel.textColor = UIColor(named: "White")
        self.timerLabel.textColor = UIColor(named: "White")
        self.timerLabel.font = UIFont(name: "Arlon-Regular", size: 38)
        
        // open db
        db = DBHelper()
        
        // open model
        let ok = TfliteModel.loadModel(on: self)
        if (ok == false) {
            ErrorReporting.showMessage(title: "Error", msg: "Error initializing TensorFlow Lite.", on: self)
        }
        
        check_record_permission()
    }
    
    // check record permission
    func check_record_permission()
    {
        switch AVAudioSession.sharedInstance().recordPermission {
        case AVAudioSessionRecordPermission.granted:
            isAudioRecordingGranted = true
            break
        case AVAudioSessionRecordPermission.denied:
            isAudioRecordingGranted = false
            break
        case AVAudioSessionRecordPermission.undetermined:
            AVAudioSession.sharedInstance().requestRecordPermission({ (allowed) in
                    if allowed {
                        self.isAudioRecordingGranted = true
                    } else {
                        self.isAudioRecordingGranted = false
                    }
            })
            break
        default:
            break
        }
    }
    
    // Setup the recorder
    func setup_recorder()
    {
        if (isAudioRecordingGranted == true)
        {
            let session = AVAudioSession.sharedInstance()
            do
            {
                try session.setCategory(AVAudioSession.Category.playAndRecord, options: .defaultToSpeaker)
                try session.setActive(true)
                let settings = [
                    AVFormatIDKey: Int(kAudioFormatMPEG4AAC),
                    AVNumberOfChannelsKey: 1,
                    AVEncoderBitRateKey: 128000,
                    AVSampleRateKey: 44100,
                    AVEncoderAudioQualityKey:AVAudioQuality.high.rawValue
                ]
                
                let year = Calendar.current.component(.year, from: Date())
                let month = Calendar.current.component(.month, from: Date())
                let day = Calendar.current.component(.day, from: Date())
                let hour = Calendar.current.component(.hour, from: Date())
                let minute = Calendar.current.component(.minute, from: Date())
                let second = Calendar.current.component(.second, from: Date())
                
                fileName = "Recording_" + String(year) + "_" + String(format: "%02d",month) + "_" + String(format: "%02d", day) + "_" + String(format: "%02d", hour) + "_" + String(format: "%02d", minute) + "_" + String(format: "%02d", second)
                
                audioRecorder = try AVAudioRecorder(url: ManageFiles.getFileUrl(filename: fileName + ".aac"), settings: settings)
                audioRecorder.delegate = self
                audioRecorder.isMeteringEnabled = true
                audioRecorder.prepareToRecord()
                
                meterTimer = Timer.scheduledTimer(timeInterval: 0.1, target:self, selector:#selector(self.updateAudioMeter(timer:)), userInfo:nil, repeats:true)
                audioRecorder.record()
            }
            catch let error {
                ErrorReporting.showMessage(title: "Error", msg: error.localizedDescription, on: self)
                self.handlerErrorView()
            }
        }
        else
        {
            ErrorReporting.showMessage(title: "Error", msg: "Don't have access to use your microphone.", on: self)
            self.handlerErrorView()
        }
    }
    
    func finishAudioRecording(success: Bool)
    {
        if success
        {
            audioRecorder.stop()
            audioRecorder = nil
            meterTimer.invalidate()
            self.timerLabel.text = "00:00"
            //print("recorded successfully.")
            let path = ManageFiles.getFileUrl(filename: fileName).absoluteString
            MobileFFmpeg.execute("-i " + path + ".aac" + " -acodec pcm_u8 -ar 44100 " + path.replacingOccurrences(of: ".aac", with: "") + ".wav")
            // delete file .aac
            do
            {
                let fileManager = FileManager.default
                try fileManager.removeItem(at: (path + ".aac").asURL())
            } catch let error {
                print(error.localizedDescription)
            }
        }
        else
        {
            ErrorReporting.showMessage(title: "Error", msg: "Recording failed.", on: self)
            self.handlerErrorView()
        }
    }
    
    func handlerErrorView() {
        self.recordLabel.text = "CLICCA IL BOTTONE PER REGISTRARE"
        self.recordLabel.textColor = UIColor(named: "White")
        self.recordImage.image = UIImage(named: "rec_button_off")
    }
    
    @objc func updateAudioMeter(timer: Timer)
    {
        if audioRecorder.isRecording
        {
            //let hr = Int((audioRecorder.currentTime / 60) / 60)
            let min = Int(audioRecorder.currentTime / 60)
            let sec = Int(audioRecorder.currentTime.truncatingRemainder(dividingBy: 60))
            let totalTimeString = String(format: "%02d:%02d", min, sec)
            self.timerLabel.text = totalTimeString
            audioRecorder.updateMeters()
        }
    }
    
    @IBAction func recordButton_touchUpInside(_ sender: UIButton) {
        
        if (self.recordLabel.text == "CLICCA IL BOTTONE PER REGISTRARE") {
            
            self.recordLabel.text = "STO REGISTRANDO"
            self.recordLabel.textColor = UIColor(named: "Red")
            self.recordImage.image = UIImage(named: "rec_button_on")
            
            setup_recorder()
        } else if (self.recordLabel.text == "STO REGISTRANDO") {
            
            self.recordLabel.text = "STO PENSANDO"
            self.recordLabel.textColor = UIColor(named: "Blue")
            
            finishAudioRecording(success: true)
            
            let urlAudioWav = ManageFiles.getFileUrl(filename: fileName + ".wav")
            
            request(audioFilePath: urlAudioWav)
            
        }
    }
    
    func request(audioFilePath: URL) {
        
        let url: URL = URL(string: "http://" + SettingsViewController.dictionary["server"]! + ":" + SettingsViewController.dictionary["port"]! + "/upload/")!
        let headers: HTTPHeaders = [
                "content-type": "multipart/form-data; boundary=---011000010111000001101001",
                "accept": "application/json"
        ]
        
        AF.upload(multipartFormData: { multipartFormData in
            multipartFormData.append(audioFilePath, withName: "file")
            
        }, to: url, headers: headers)
        .responseJSON { [self] response in
            switch response.result {
            case .success:
                do{
                    let json = try JSON(data: response.data!)
                    
                    var inputImages: [[[[Float32]]]] = []
                    var inputFrames: [Float32] = []
                    let decoder = JSONDecoder()
                    do {
                        inputImages = try decoder.decode([[[[Float32]]]].self, from: json["images"].rawData())
                        inputFrames = try decoder.decode([Float32].self, from: json["frames"].rawData())
                        //debugPrint(inputFrames)
                      } catch {
                          print("Unexpected runtime error. Array")
                          return
                      }
                    
                    var i = 0
                    var positions: String = ""
                    do {
                        // input tensor [1, 192, 9, 1]
                        // output tensor [1, 6, 21]
                        for element in inputImages {
                            
                            if (inputFrames.contains(Float32(i))) {
                                
                                var inputData = Data()
                                for element2 in element {
                                    for element3 in element2 {
                                        for element4 in element3 {
                                            var f = Float32(element4)
                                            //print(f)
                                            let elementSize = MemoryLayout.size(ofValue: f)
                                            var bytes = [UInt8](repeating: 0, count: elementSize)
                                            memcpy(&bytes, &f, elementSize)
                                            inputData.append(&bytes, count: elementSize)
                                        }
                                    }
                                }
                                
                                try TfliteModel.interpreter.allocateTensors()
                                try TfliteModel.interpreter.copy(inputData, toInputAt: 0)
                                try TfliteModel.interpreter.invoke()
                                
                                let output = try TfliteModel.interpreter.output(at: 0)
                                let probabilities =
                                        UnsafeMutableBufferPointer<Float32>.allocate(capacity: 126)
                                output.data.copyBytes(to: probabilities)
                                
                                //print("IMG", i)
                                
                                for string in 0...5 {
                                    //print("CORDA", (y+1))
                                    var maxTempButtonValue: Float32 = 0
                                    var maxTempButtonPosition = 0
                                    for flat in 0...20 {
                                        if (probabilities[string*21 + flat] > maxTempButtonValue) {
                                            maxTempButtonValue = probabilities[string*21 + flat]
                                            maxTempButtonPosition = flat
                                        }
                                        
                                        //print(probabilities[z])
                                    } // for flat
                                    positions += String(maxTempButtonPosition) + " "
                                    
                                } // for string
                                
                            } // inputFrames
                            
                            i += 1
                        } // inputArray
                        
                        self.db.insert(title: fileName, date:"", tab: String(positions.dropLast()))
                        
                    } catch {
                        print("Unexpected predictions")
                        return
                    }
                    
                    // delete file .wav
                    do
                    {
                        let fileManager = FileManager.default
                        try fileManager.removeItem(at: audioFilePath)
                    } catch let error {
                        print(error.localizedDescription)
                    }
                    
                    self.performSegue(withIdentifier: "segueHomeToResultViewController", sender: nil)
                    
                    self.recordLabel.text = "CLICCA IL BOTTONE PER REGISTRARE"
                    self.recordLabel.textColor = UIColor(named: "White")
                    self.recordImage.image = UIImage(named: "rec_button_off")
                    
                }   catch {
                    print(error.localizedDescription)
                }
            
            case .failure(let encodingError):
                ErrorReporting.showMessage(title: "Error", msg: "\(encodingError)", on: self)
                self.handlerErrorView()
            }
            
        }
    }
    
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
            
        // Controllo se il segue ha un identifier o meno, se non ce l'ha esco dalla func
        guard let identifier = segue.identifier else {
            print("🟢 il segue non ha un identifier, esco dal prepareForSegue")
            return
        }
        
        // Controllo l'identifier perché potrebbero esserci più di un Segue che parte da questo VC
        switch identifier {
        case "segueHomeToResultViewController":
            // Accedo al destinationViewController del segue e lo casto del tipo di dato opportuno
            // Modifico la variabile d'appoggio con il contenuto che voglio inviare
            let tabViewController = segue.destination as! TabViewController
            tabViewController.fileName = self.fileName
            
            default:
                return
        }
        
    }
    
}
