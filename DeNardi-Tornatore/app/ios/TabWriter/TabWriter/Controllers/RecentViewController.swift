//
//  RecentViewController.swift
//  SistemiDigitali
//
//  Created by Dario De Nardi on 05/02/21.
//

import UIKit
import Alamofire
import SwiftyJSON

class RecentViewController: UIViewController {
    
    @IBOutlet weak var tableView: UITableView!
    
    var fileList: [Tab] = []
    var fileName = ""
    var db: DBHelper!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view.
        print("🟢", #function)
        
        tableView.backgroundColor = UIColor(named: "Grey")
        
        findAllRecording()
        self.tableView.delegate = self
        self.tableView.dataSource = self
    }
    
    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        findAllRecording()
        self.tableView.reloadData()
    }
    
    func findAllRecording() {
        fileList = []
        
        db = DBHelper()
        fileList = db.readAll()
        //db.delete()
    }
    
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
            
        // Controllo se il segue ha un identifier o meno, se non ce l'ha esco dalla func
        guard let identifier = segue.identifier else {
            print("🟢 il segue non ha un identifier, esco dal prepareForSegue")
            return
        }
        
        // Controllo l'identifier perché potrebbero esserci più di un Segue che parte da questo VC
        switch identifier {
        case "segueTabToResultViewController":
            // Accedo al destinationViewController del segue e lo casto del tipo di dato opportuno
            // Modifico la variabile d'appoggio con il contenuto che voglio inviare
            let tabViewController = segue.destination as! TabViewController
            tabViewController.fileName = self.fileName
            
            default:
                return
        }
        
    }
    
} //RecentViewController

extension RecentViewController: UITableViewDelegate {
    
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        
        fileName = fileList[indexPath.row].title
        
        self.performSegue(withIdentifier: "segueTabToResultViewController", sender: nil)
    }
    
}

extension RecentViewController: UITableViewDataSource {
    
    func numberOfSections(in tableView: UITableView) -> Int {
        return 1
    }
    
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return fileList.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "cell", for: indexPath)
        
        cell.backgroundColor = UIColor(named: "Grey")
        
        let row = fileList[indexPath.row]
        
        cell.textLabel?.text = row.title
        cell.textLabel?.font = UIFont(name: "Arlon-Regular", size: 17)
        
        return cell
    }
    
    func tableView(_ tableView: UITableView, commit editingStyle: UITableViewCell.EditingStyle, forRowAt indexPath: IndexPath) {
        if editingStyle == UITableViewCell.EditingStyle.delete {
            let row = fileList[indexPath.row]
            fileList.remove(at: indexPath.row)
            tableView.deleteRows(at: [indexPath], with: UITableView.RowAnimation.automatic)
            db.deleteByID(title: row.title)
        }
    }
    
}
