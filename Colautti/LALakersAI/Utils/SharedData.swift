//
//  SharedData.swift
//  LALakersAI
//
//  Created by Daniele Colautti on 11/01/21.
//

import Foundation
import CoreMedia
import AVFoundation

class SharedData: ObservableObject {
    
    let playersNumber = 17
    let playersShortName = ["kuzma",
                            "cook",
                            "caldwell-pope",
                            "davis",
                            "caruso",
                            "horton-tucker",
                            "matthews",
                            "dudley",
                            "cacok",
                            "gasol",
                            "harrell",
                            "schroder",
                            "james",
                            "mckinnie",
                            "smith",
                            "antetokounmpo",
                            "morris"]
    var passes = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    var goals = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    var lastLineUp = [String]()
    @Published var playersToFollow = [true,true,true,true,true,true,true,true,true,true,true,true,true,true,true,true,true]
    @Published var onlyBallPossessor = true
    @Published var boxBall = true
    @Published var boxBasket = true
    @Published var showAllGoals = true
    
    public func boxBallToggle() {
        boxBall.toggle()
    }
    
    public func boxBasketToggle() {
        boxBasket.toggle()
    }
    
    public func playerToFollowToggle(i: Int) {
        playersToFollow[i].toggle()
    }
    
    public func saveData() {
        UserDefaults.standard.set(try? PropertyListEncoder().encode(playersToFollow), forKey: "players")
        UserDefaults.standard.set(try? PropertyListEncoder().encode(lastLineUp), forKey: "lineUp")
        UserDefaults.standard.set(try? PropertyListEncoder().encode([onlyBallPossessor,boxBall,boxBasket,showAllGoals]), forKey: "elements")
        UserDefaults.standard.set(try? PropertyListEncoder().encode(goals), forKey: "goals")
        UserDefaults.standard.set(try? PropertyListEncoder().encode(passes), forKey: "passes")
    }
    
    enum Element {
        case Elements, Players, LineUp, Goals, Passes
    }
    public func saveData(element: Element) {
        switch element {
        case Element.Elements:
            UserDefaults.standard.set(try? PropertyListEncoder().encode([onlyBallPossessor,boxBall,boxBasket,showAllGoals]), forKey: "elements")
        case Element.Players:
            UserDefaults.standard.set(try? PropertyListEncoder().encode(playersToFollow), forKey: "players")
        case Element.LineUp:
            UserDefaults.standard.set(try? PropertyListEncoder().encode(lastLineUp), forKey: "lineUp")
        case Element.Goals:
            UserDefaults.standard.set(try? PropertyListEncoder().encode(goals), forKey: "goals")
        case Element.Passes:
            UserDefaults.standard.set(try? PropertyListEncoder().encode(passes), forKey: "passes")
        }
    }
    
    static public func loadData(start: Bool) -> SharedData {
        let sharedData = SharedData()
        if let playersD = UserDefaults.standard.value(forKey: "players") as? Data {
            if let players = try? PropertyListDecoder().decode(Array<Bool>.self, from: playersD) {
                sharedData.playersToFollow = players
            }
        }
        if let lineUpD = UserDefaults.standard.value(forKey: "lineUp") as? Data {
            if let lineUp = try? PropertyListDecoder().decode(Array<String>.self, from: lineUpD) {
                sharedData.lastLineUp = lineUp
            }
        }
        if let elementsD = UserDefaults.standard.value(forKey: "elements") as? Data {
            if let elements = try? PropertyListDecoder().decode(Array<Bool>.self, from: elementsD) {
                sharedData.onlyBallPossessor = elements[0]
                sharedData.boxBall = elements[1]
                sharedData.boxBasket = elements[2]
                sharedData.showAllGoals = elements[3]
            }
        }
        if start {
            sharedData.passes = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            sharedData.goals = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            sharedData.saveData()
        } else {
            if let goalsD = UserDefaults.standard.value(forKey: "goals") as? Data {
                if let goals = try? PropertyListDecoder().decode(Array<Int>.self, from: goalsD) {
                    sharedData.goals = goals
                }
            }
            if let passesD = UserDefaults.standard.value(forKey: "passes") as? Data {
                if let passes = try? PropertyListDecoder().decode(Array<Int>.self, from: passesD) {
                    sharedData.passes = passes
                }
            }
        }
        return sharedData
    }
    
    func labelInPredictionArray(predictions: [Model.Prediction], label: String, times: Int) -> Bool {
        var timesFound = 0
        for i in 0..<predictions.count {
            if labels[predictions[i].classIndex] == label {
                timesFound += 1
                if timesFound == times {
                    return true
                }
            }
        }
        return false
    }
    
    public func filterPredictions(predictions: [Model.Prediction]) -> [Model.Prediction] {
        var filteredPredictions = [Model.Prediction]()
        for i in 0..<predictions.count {
            let label = labels[predictions[i].classIndex]
            if !labelInPredictionArray(predictions: filteredPredictions, label: label, times: 1) {
                filteredPredictions.append(predictions[i])
            }
        }
        /*var debug = ""
        for i in 0..<filteredPredictions.count {
            debug += String(filteredPredictions[i].classIndex) + " "
        }
        print(debug)*/
        return filteredPredictions
    }
    
    func updateLineUp(predictions: [Model.Prediction]) {
        var playersFound = [String]()
        //var debug = ""
        for i in 0..<predictions.count {
            let name = labels[predictions[i].classIndex]
            if name != "ball" && name != "basket" {
                playersFound.append(name)
                //debug += name + " "
            }
        }
        if playersFound.count != 5 {
            //debug += " ( "
            for player in lastLineUp {
                if !playersFound.contains(player) {
                    playersFound.append(player)
                    //debug += player + " "
                    if playersFound.count == 5 {
                        break
                    }
                }
            }
            //debug += ")"
        }
        //print(debug)
        lastLineUp = playersFound
    }
    
    var lastBallRect: CGRect?
    var lastGoalTime: CFTimeInterval?
    let waitSecondsBeforeNewGoal = 3
    
    func goalVerify(predictions: [Model.Prediction]) -> Bool {
        if lastGoalTime == nil || Int(CACurrentMediaTime() - lastGoalTime!) >= waitSecondsBeforeNewGoal {
            var goal = false
            let ballRect = readRect(label: "ball", predictions: predictions)
            let basketRect = readRect(label: "basket", predictions: predictions)
            if ballRect != nil {
                if basketRect != nil {
                    goal = goalSoluction1(ball: ballRect!, basket: basketRect!)
                    if !goal && lastBallRect != nil {
                        goal = goalSoluction2(previousBall: lastBallRect!, actualBall: ballRect!, basket: basketRect!)
                    }
                }
                lastBallRect = ballRect
            }
            if goal {
                let player = lastPossiblePossessor()
                if  player != nil {
                    updateStatistics(player: player!, stat: Stats.Goals)
                }
                lastGoalTime = CACurrentMediaTime()
                return true
            }
        }
        return false
    }
    
    func readRect(label: String, predictions: [Model.Prediction]) -> CGRect? {
        var result: CGRect?
        for i in 0..<predictions.count {
            if labels[predictions[i].classIndex] == label {
                result = predictions[i].rect
                break
            }
        }
        return result
    }
    
    func goalSoluction1(ball: CGRect, basket: CGRect) -> Bool {
        let perc = 0.5
        let intersection = basket.intersection(ball)
        let intersectionArea = Float(intersection.width * intersection.height)
        let ballArea = Float(ball.width * ball.height)
        /*
        let res = intersectionArea >= ballArea * Float(perc)
        if res {
            print("Solution1: " + String(res) + " (" + String(ballArea) + "," + String(intersectionArea) + ")")
        }
        */
        return intersectionArea >= ballArea * Float(perc)
    }
    
    func goalSoluction2(previousBall: CGRect, actualBall: CGRect, basket: CGRect) -> Bool {
        let xPerc = CGFloat(1)
        let yPerc1 = CGFloat(0.5)
        let yPerc2 = CGFloat(0.5)
        let lowLimitPerc = CGFloat(1.5)
        let p1 = CGPoint(x: previousBall.origin.x, y: previousBall.origin.y + previousBall.height)
        let p2 = CGPoint(x: previousBall.origin.x + previousBall.width, y: previousBall.origin.y + previousBall.height)
        let p3 = CGPoint(x: basket.origin.x - basket.width * xPerc, y: basket.origin.y + basket.height * yPerc1)
        let p4 = CGPoint(x: basket.origin.x + basket.width + basket.width * xPerc, y: basket.origin.y + basket.height * yPerc1)
        let p5 = CGPoint(x: actualBall.origin.x, y: actualBall.origin.y)
        let p6 = CGPoint(x: actualBall.origin.x + actualBall.width, y: actualBall.origin.y)
        let p7 = CGPoint(x: basket.origin.x - basket.width * xPerc, y: basket.origin.y + basket.height - basket.height * yPerc2)
        let p8 = CGPoint(x: basket.origin.x + basket.width + basket.width * xPerc, y: basket.origin.y + basket.height - basket.height * yPerc2)
        if p1.x < p3.x || p1.y > p3.y || p2.x > p4.x || p2.y > p4.y ||
            p5.x < p7.x || p5.y < p7.y || p6.x > p8.x || p6.y < p8.y  ||
            p5.y > p7.y + basket.height * lowLimitPerc || p6.y > p7.y + basket.height * lowLimitPerc {
            return false
        }
        //print("Solution2: true")
        return true
    }
    
    let secondsForRealPossess = 0.1
    var ballPossessor: String?
    
    var candidatePossessor: String?
    var lastTimeCandidatePossess: CFTimeInterval?
    
    func ballPossessor(predictions: [Model.Prediction]) {
        let minIntersectionPerc = 0.75
        var player: String?
        var maxInteresctionArea = Float(0)
        let ballRect = readRect(label: "ball", predictions: predictions)
        if ballRect != nil {
            ballPossessor = nil
            for i in 0..<predictions.count {
                if labels[predictions[i].classIndex] != "ball" && labels[predictions[i].classIndex] != "basket" {
                    let intersection = predictions[i].rect.intersection(ballRect!)
                    let intersectionArea = Float(intersection.width * intersection.height)
                    let ballArea = Float(ballRect!.width * ballRect!.height)
                    if intersectionArea >= ballArea * Float(minIntersectionPerc) && intersectionArea > maxInteresctionArea {
                        player = labels[predictions[i].classIndex]
                        maxInteresctionArea = intersectionArea
                        if candidatePossessor == nil || candidatePossessor! != player {
                            candidatePossessor = player
                            lastTimeCandidatePossess = CACurrentMediaTime()
                        } else {
                            if CACurrentMediaTime() - lastTimeCandidatePossess! >= secondsForRealPossess {
                                ballPossessor = player
                                lastFoundBallPossessor = player
                                lastStore = CACurrentMediaTime()
                            }
                        }
                    }
                }
            }
            /*
            if ballPossessor != nil {
                print("Found real ball possessor: " + ballPossessor! + " - " + String(CACurrentMediaTime()))
            }
            */
        }
    }
    
    var lastFoundBallPossessor: String?
    let secondsToStoreLastPossessor = 3
    var lastStore: CFTimeInterval?
    
    func lastPossiblePossessor() -> String? {
        if lastFoundBallPossessor != nil && Int(CACurrentMediaTime() - lastStore!) > secondsToStoreLastPossessor {
            lastFoundBallPossessor = nil
        }
        return lastFoundBallPossessor
    }
    
    var previousPosssessor: String?
    let secondsToStorePreviousPossessor = 8
    var lastPrevious: CFTimeInterval?
    
    func detectPass() {
        if previousPosssessor != nil && lastFoundBallPossessor != nil && previousPosssessor! != lastFoundBallPossessor! &&
            Int(CACurrentMediaTime() - lastPrevious!) <= secondsToStorePreviousPossessor {
            //print("Detect pass from " + previousPosssessor! + " to " + lastFoundBallPossessor!)
            updateStatistics(player: previousPosssessor!, stat: Stats.Passes)
            previousPosssessor = lastFoundBallPossessor
            lastPrevious = CACurrentMediaTime()
        } else {
            if lastFoundBallPossessor != nil && (previousPosssessor == nil || previousPosssessor! != lastFoundBallPossessor!) {
                previousPosssessor = lastFoundBallPossessor
                lastPrevious = CACurrentMediaTime()
            } else if previousPosssessor != nil && Int(CACurrentMediaTime() - lastPrevious!) > secondsToStorePreviousPossessor {
                previousPosssessor = nil
            }
        }
        saveData(element: Element.Passes)
    }
    
    func predictionToShow(prediction: Model.Prediction) -> Bool {
        let label = labels[prediction.classIndex]
        if label == "ball" {
            return boxBall
        } else if label == "basket" {
            return boxBasket
        } else {
            if onlyBallPossessor {
                return lastFoundBallPossessor == nil ? false : lastFoundBallPossessor == label
            } else {
                return playersToFollow[prediction.classIndex]
            }
        }
    }
    
    enum Stats {
        case Goals, Passes
    }
    func updateStatistics(player: String, stat: Stats) {
        switch stat {
        case Stats.Goals:
            goals[playersShortName.firstIndex(of: player)!] += 1
            //print("Update " + player + " goals!")
            saveData(element: Element.Goals)
        case Stats.Passes:
            passes[playersShortName.firstIndex(of: player)!] += 1
            //print("Update " + player + " passes!")
            saveData(element: Element.Passes)
        }
    }
    
    static func labelToShowOnlySurname(player: String) -> String {
        var result = ""
        switch player {
        case "kuzma":
            result = "Kuzma"
        case "cook":
            result = "Cook"
        case "caldwell-pope":
            result = "Caldwell-Pope"
        case "davis":
            result = "Davis"
        case "caruso":
            result = "Caruso"
        case "horton-tucker":
            result = "Horton-Tucker"
        case "matthews":
            result = "Matthews"
        case "dudley":
            result = "Dudley"
        case "cacok":
            result = "Cacok"
        case "gasol":
            result = "Gasol"
        case "harrell":
            result = "Harrell"
        case "schroder":
            result = "Schroder"
        case "james":
            result = "James"
        case "mckinnie":
            result = "McKinnie"
        case "smith":
            result = "Smith"
        case "antetokounmpo":
            result = "Antetokounmpo"
        case "morris":
            result = "Morris"
        default:
            result = ""
        }
        return result
    }
    
    static func extendedNameToShow(player: String) -> String {
        var result = ""
        switch player {
            case "james":
                result = "LeBron James"
            case "davis":
                result = "Anthony Davis"
            case "harrell":
                result = "M. Harrell"
            case "horton-tucker":
                result = "Horton-Tucker"
            case "schroder":
                result = "D. Schroder"
            case "kuzma":
                result = "K. Kuzma"
            case "antetokounmpo":
                result = "Antetokounmpo"
            case "cacok":
                result = "D. Cacok"
            case "caldwell-pope":
                result = "Caldwell-Pope"
            case "caruso":
                result = "A. Caruso"
            case "cook":
                result = "Q. Cook"
            case "dudley":
                result = "J. Dudley"
            case "gasol":
                result = "M. Gasol"
            case "matthews":
                result = "W. Matthews"
            case "mckinnie":
                result = "A. McKinnie"
            case "morris":
                result = "M. Morris"
            default:
                result = ""
        }
        return result
    }
    
}
