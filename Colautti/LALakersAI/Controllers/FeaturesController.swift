//
//  FeaturesController.swift
//  LALakersAI
//
//  Created by Daniele Colautti on 14/01/21.
//

import UIKit
import SwiftUI

class FeaturesController: UIHostingController<FeaturesView> {
    
    var sharedData = SharedData.loadData(start: false)
    var detectionController: DetectionController?
    
    required init?(coder: NSCoder) {
        super.init(coder: coder,rootView: FeaturesView(sharedData: sharedData));
    }

    override func viewDidLoad() {
        super.viewDidLoad()
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        detectionController?.reloadData()
    }

}
