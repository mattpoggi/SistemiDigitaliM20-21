//
//  AppDelegate.swift
//  TabWriter
//
//  Created by Dario De Nardi on 06/02/21.
//

import UIKit
import Firebase

@main
class AppDelegate: UIResponder, UIApplicationDelegate {

    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        // Override point for customization after application launch.
        UITabBar.appearance().tintColor = .white
        UITabBarItem.appearance().setTitleTextAttributes([NSAttributedString.Key.font: UIFont(name: "Arlon-Regular", size: 10)!], for: .normal)
        UITabBarItem.appearance().setTitleTextAttributes([NSAttributedString.Key.font: UIFont(name: "Arlon-Regular", size: 10)!], for: .selected)
        
        let exist = ManageFiles.fileExits(filename: "settings.json")
        if (!exist) {
            _ = ManageFiles.writeDataToFile(filename: "settings.json", text: "{\"server\": \"192.168.1.6\",\"port\": \"5000\"}")
        } else {
            
            do {
                let json = try JSONSerialization.loadJSON(withFilename: "settings") as? [String: Any]
                
                SettingsViewController.dictionary["port"] = json?["port"] as? String
                SettingsViewController.dictionary["server"] = json?["server"] as? String
            } catch let error {
                print("parse error: \(error.localizedDescription)")
            }
            
        }
        
        FirebaseApp.configure()
        
        return true
    }

    // MARK: UISceneSession Lifecycle

    func application(_ application: UIApplication, configurationForConnecting connectingSceneSession: UISceneSession, options: UIScene.ConnectionOptions) -> UISceneConfiguration {
        // Called when a new scene session is being created.
        // Use this method to select a configuration to create the new scene with.
        return UISceneConfiguration(name: "Default Configuration", sessionRole: connectingSceneSession.role)
    }

    func application(_ application: UIApplication, didDiscardSceneSessions sceneSessions: Set<UISceneSession>) {
        // Called when the user discards a scene session.
        // If any sessions were discarded while the application was not running, this will be called shortly after application:didFinishLaunchingWithOptions.
        // Use this method to release any resources that were specific to the discarded scenes, as they will not return.
    }


}

