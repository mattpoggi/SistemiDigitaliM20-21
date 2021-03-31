//
//  DisplayAlert.swift
//  TabWriter
//
//  Created by Dario De Nardi on 06/03/21.
//

import UIKit

class ErrorReporting: UIViewController {
    
    static func showMessage(title: String, msg: String, `on` controller: UIViewController) {
        let alert = UIAlertController(title: title, message: msg, preferredStyle: UIAlertController.Style.alert)
        alert.addAction(UIAlertAction(title: "Ok", style: UIAlertAction.Style.default, handler: nil))
        controller.present(alert, animated: true, completion: nil)
    }
    
}
