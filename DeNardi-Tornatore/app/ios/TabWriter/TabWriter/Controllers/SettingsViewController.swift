//
//  SettingsViewController.swift
//  TabWriter
//
//  Created by Dario De Nardi on 25/03/21.
//

import UIKit

class SettingsViewController: UIViewController {
    
    
    @IBOutlet weak var serverTextField: UITextField!
    @IBOutlet weak var portTextField: UITextField!
    @IBOutlet weak var serverLabel: UILabel!
    @IBOutlet weak var portLabel: UILabel!
    
    // Dictionary containing data as provided in your question.
    static var dictionary : [String : String] = ["server":"",
                                             "port":""
                                            ]
    
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view.
        print("🟢", #function)
        
        self.serverLabel.textColor = UIColor(named: "White")
        self.serverLabel.font = UIFont(name: "Arlon-Regular", size: 17)
        self.portLabel.textColor = UIColor(named: "White")
        self.portLabel.font = UIFont(name: "Arlon-Regular", size: 17)
        self.portTextField.font = UIFont(name: "Arlon-Regular", size: 14)
        self.serverTextField.font = UIFont(name: "Arlon-Regular", size: 14)
        
        do {
            let json = try JSONSerialization.loadJSON(withFilename: "settings") as? [String: Any]
            
            self.portTextField.text = json?["port"] as? String
            self.serverTextField.text = json?["server"] as? String
        } catch let error {
            print("parse error: \(error.localizedDescription)")
        }
    }
    
    @IBAction func serverTextField_didEndOnExit(_ sender: Any) {
        SettingsViewController.dictionary["server"] = serverTextField.text
        
        do {
            let ok = try JSONSerialization.save(jsonObject: SettingsViewController.dictionary, toFilename: "settings")
            if (!ok) {
                ErrorReporting.showMessage(title: "Error", msg: "Error save settings", on: self)
            }
            
        } catch let error {
            print("parse error: \(error.localizedDescription)")
        }
    }
    
    @IBAction func portTextField_didEndOnExit(_ sender: Any) {
        SettingsViewController.dictionary["port"] = serverTextField.text
        
        do {
            let ok = try JSONSerialization.save(jsonObject: SettingsViewController.dictionary, toFilename: "settings")
            if (!ok) {
                ErrorReporting.showMessage(title: "Error", msg: "Error save settings", on: self)
            }
            
        } catch let error {
            print("parse error: \(error.localizedDescription)")
        }
    }
    
}
