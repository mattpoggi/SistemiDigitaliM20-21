//
//  StatisticsView.swift
//  LALakersAI
//
//  Created by Daniele Colautti on 11/01/21.
//

import SwiftUI

struct StatisticsView: View {
    var sharedData: SharedData
    @State var showEmptyStats = true
    
    var body: some View {
        ScrollView {
            Toggle(isOn: $showEmptyStats) {
                Text("Statistiche nulle")
            }
            .padding(3)
            if showEmptyStats || notAllEmpty() {
                HStack(spacing: 25) {
                    VStack(alignment: .leading, spacing: 5) {
                        Text("Giocatore")
                            .font(.title2)
                            .foregroundColor(.orange)
                            .bold()
                        ForEach(0..<sharedData.playersNumber) { i in
                            if showEmptyStats || statsNotEmpty(i) {
                                Text(SharedData.labelToShowOnlySurname(player: sharedData.playersShortName[i]))
                            }
                        }
                    }
                    VStack(spacing: 5) {
                        Text("Passaggi")
                            .font(.title3)
                            .foregroundColor(.orange)
                            .bold()
                        ForEach(0..<sharedData.playersNumber) { i in
                            if showEmptyStats || statsNotEmpty(i) {
                                Text(String(sharedData.passes[i]))
                            }
                        }
                    }
                    VStack(spacing: 5) {
                        Text("Canestri")
                            .font(.title3)
                            .foregroundColor(.orange)
                            .bold()
                        ForEach(0..<sharedData.playersNumber) { i in
                            if showEmptyStats || statsNotEmpty(i) {
                                Text(String(sharedData.goals[i]))
                            }
                        }
                    }
                }
            } else {
                Text("Tutte le statistiche sono nulle per ora...")
                    .font(.title3)
                    .foregroundColor(.orange)
                    .bold()
                    .multilineTextAlignment(.center)
            }
        }
    }
    
    func notAllEmpty() -> Bool {
        for i in 0..<sharedData.playersNumber {
            if statsNotEmpty(i) {
                return true
            }
        }
        return false
    }
    
    func statsNotEmpty(_ index: Int) -> Bool {
        return sharedData.passes[index] != 0 || sharedData.goals[index] != 0
    }
}

struct StatisticsView_Previews: PreviewProvider {
    static var previews: some View {
        StatisticsView(sharedData: SharedData())
    }
}
