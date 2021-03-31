//
//  ManageFiles.swift
//  TabWriter
//
//  Created by Dario De Nardi on 06/03/21.
//

import Foundation

class ManageFiles {
    
    // generate path where you want to save that recording as myRecording.m4a
    static func getDocumentsDirectory() -> URL
    {
        let paths = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)
        let documentsDirectory = paths[0]
        
        return documentsDirectory
    }
    
    static func getFileUrl(filename: String) -> URL
    {
        let filePath = getDocumentsDirectory().appendingPathComponent(filename)
        
        return filePath
    }
    
    static func fileExits(filename: String) -> Bool
    {
        let path = NSSearchPathForDirectoriesInDomains(.documentDirectory, .userDomainMask, true)[0] as String
        let url = NSURL(fileURLWithPath: path)
        if let pathComponent = url.appendingPathComponent(filename) {
            let filePath = pathComponent.path
            let fileManager = FileManager.default
            if fileManager.fileExists(atPath: filePath) {
                return true
            } else {
                return false
            }
        } else {
            return false
        }
    }
    
    static func writeDataToFile(filename: String, text: String)-> Bool{
    
        let path = NSSearchPathForDirectoriesInDomains(.documentDirectory, .userDomainMask, true)[0] as String
        let url = NSURL(fileURLWithPath: path)
        
        let fileName = url.appendingPathComponent(filename)
        
        do{
            try text.write(to: fileName!, atomically: false, encoding: String.Encoding.utf8)
            return true
        } catch _ as NSError {
            return false
        }
    }
    
}
