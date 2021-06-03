//
//  MusicRequest.swift
//  TabWriter
//
//  Created by Dario De Nardi on 06/03/21.
//

import Firebase
import TensorFlowLite

class TfliteModel {
        
    static var interpreter: Interpreter!
    
    static func loadModel(`on` controller: UIViewController) -> Bool {
        
        guard let modelPath = Bundle.main.path(forResource: "model", ofType: "tflite")
          else {
            // Invalid model path
            return false
          }
        
        do {
            interpreter = try Interpreter(modelPath: modelPath)
          } catch {
              return false
          }
        
        return true
    }
    
}
