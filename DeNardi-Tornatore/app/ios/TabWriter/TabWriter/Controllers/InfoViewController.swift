//
//  InfoViewController.swift
//  TabWriter
//
//  Created by Dario De Nardi on 17/02/21.
//

import UIKit

class InfoViewController: UIViewController {
    
    @IBOutlet weak var creditsLabel: UILabel!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view.
        print("🟢", #function)
        
        self.creditsLabel.textColor = UIColor(named: "White")
        self.creditsLabel.font = UIFont(name: "Arlon-Regular", size: 17)
    }
    
}
