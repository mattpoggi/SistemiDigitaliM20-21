//
//  CheckBox.swift
//  LALakersAI
//
//  Created by Daniele Colautti on 12/01/21.
//

import SwiftUI

struct PlayerToFollowCheckBox: View {
    var index: Int
    var boxPosition: String
    @ObservedObject var sharedData: SharedData
    
    var body: some View {
        Button(action: {
            sharedData.playerToFollowToggle(i: index)
            sharedData.saveData()
        }, label: {
            HStack{
                if boxPosition == "left" {
                    Image(systemName: sharedData.playersToFollow[index] ? "checkmark.square": "square")
                        .foregroundColor(sharedData.playersToFollow[index] ? .green : .black)
                    Text(nameToShow(player: sharedData.playersShortName[index]))
                        .foregroundColor(.black)
                } else {
                    Text(nameToShow(player: sharedData.playersShortName[index]))
                        .foregroundColor(.black)
                    Image(systemName: sharedData.playersToFollow[index] ? "checkmark.square": "square")
                        .foregroundColor(sharedData.playersToFollow[index] ? .green : .black)
                }
            }
        })
    }
    
    func nameToShow(player: String) -> String {
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
}

struct CheckBox_Previews: PreviewProvider {
    static var previews: some View {
        PlayerToFollowCheckBox(index: 0, boxPosition: "left", sharedData: SharedData())
        PlayerToFollowCheckBox(index: 0, boxPosition: "right", sharedData: SharedData())
    }
}
