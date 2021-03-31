//
//  TabViewController.swift
//  SistemiDigitali
//
//  Created by Dario De Nardi on 05/02/21.
//

import UIKit
import Firebase
import TensorFlowLite
import Charts
import TinyConstraints

class TabViewController: UIViewController, ChartViewDelegate {
    
    @IBOutlet weak var titleLabel: UILabel!
    
    var tabValues: [BubbleChartDataEntry] = []
    var fileName = ""
    
    lazy var chartView: BubbleChartView = {
       let chartView = BubbleChartView()
        
        chartView.backgroundColor = UIColor(named: "Grey")
        
        return chartView
    }()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view.
        print("🟢", #function)
        
        let appearance = UINavigationBarAppearance()
        appearance.configureWithOpaqueBackground()
        appearance.backgroundColor = UIColor(named: "Black")
        self.navigationController?.navigationBar.tintColor = .white
        self.navigationController?.navigationBar.standardAppearance = appearance
        self.navigationController?.navigationBar.scrollEdgeAppearance = appearance
        
        self.titleLabel.text = fileName
        
        self.titleLabel.textColor = UIColor(named: "White")
        
        view.addSubview(chartView)
        chartView.centerInSuperview()
        chartView.width(to: view)
        chartView.heightToWidth(of: view)
        
        chartView.delegate = self
        
        chartView.doubleTapToZoomEnabled = false
        chartView.scaleXEnabled = true
        chartView.scaleYEnabled = false
        chartView.highlightPerTapEnabled = false
        chartView.highlightPerDragEnabled = true
        chartView.setVisibleXRangeMaximum(5)
        
        chartView.drawGridBackgroundEnabled = false
        chartView.dragEnabled = true
        chartView.dragXEnabled = true
        chartView.dragYEnabled = false
        chartView.pinchZoomEnabled = false
        chartView.xAxis.enabled = false
        chartView.leftAxis.enabled = true
        chartView.rightAxis.enabled = false
        chartView.chartDescription?.enabled = false
        chartView.legend.enabled = false
        
        chartView.leftAxis.labelFont = UIFont(name: "Arlon-Regular", size: 10)!
        
        let array = ["E","A","D","G","B","e"]
        chartView.leftAxis.valueFormatter = IndexAxisValueFormatter(values: array)
        chartView.leftAxis.drawGridLinesEnabled = true
        chartView.leftAxis.granularityEnabled = true
        chartView.leftAxis.drawZeroLineEnabled = false
        chartView.leftAxis.labelFont = UIFont.boldSystemFont(ofSize: 12)
        chartView.leftAxis.labelTextColor = .white
        chartView.leftAxis.granularity = 1
        chartView.leftAxis.axisMinimum = 0
        chartView.leftAxis.axisMaximum = 5
        
        chartView.xAxis.axisMinimum = 0
        
        chartView.xAxis.labelFont = UIFont.boldSystemFont(ofSize: 12)
        tabValues = []
        
        let db = DBHelper()
        let tab = db.read(title: fileName)
        let tabArray = tab.tab.components(separatedBy: " ")
        //print(tabArray)
        chartView.xAxis.axisMaximum = Double(tabArray.count/6 + 1)
        if (tabArray[0] != "") {
            var i = 1
            var string = 0
            for value in tabArray {
                
                // colonna[0]: se suono o no = 1 no suono
                // colonna[1]: se non suono i tasti ma solo la corda
                if (value != "0") {
                    tabValues.append(BubbleChartDataEntry(x: Double(i), y: Double(5-string), size: CGFloat(Int(value)! - 1)))
                    i += 1
                }
                
                if (string == 5) {
                    string = -1
                }
                
                string += 1
            }
        } // if there is a element
        
        setChartDataSet()
        
    }
    
    func chartValueSelected(_ chartView: ChartViewBase, entry: ChartDataEntry, highlight: Highlight) {
        //print(entry)
    }
    
    func setChartDataSet() {
        let set1 = BubbleChartDataSet(entries: tabValues, label: "")
        set1.drawIconsEnabled = false
        set1.setColor(.white, alpha: 0.0)
        //set1.drawValuesEnabled = true
        set1.valueFormatter = DefaultValueFormatter(decimals: 0)
        
        let data = BubbleChartData(dataSet: set1)
        data.setDrawValues(true)
        data.setValueFont(UIFont(name: "Arlon-Regular", size: 16)!)
        data.setHighlightCircleWidth(0)
        data.setValueTextColor(.white)
        
        chartView.data = data
    }
    
}
