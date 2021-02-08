//
//  SettingsView.swift
//  LALakersAI
//
//  Created by Daniele Colautti on 11/01/21.
//

import SwiftUI

struct SettingsView: View {
    @ObservedObject var sharedData: SharedData
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 8) {
                Text("Selezionare i giocatori da segnalare durante l'acquisizione delle immagini:")
                    .font(.headline)
                Toggle(isOn: $sharedData.onlyBallPossessor) {
                    Text("Solo il possessore di palla")
                }
                .onChange(of: sharedData.onlyBallPossessor, perform: { value in
                    sharedData.saveData(element: SharedData.Element.Elements)
                })
                .padding(3)
                if !sharedData.onlyBallPossessor {
                    ForEach(0..<sharedData.playersNumber / 2 + 1) { i in
                        HStack {
                            PlayerToFollowCheckBox(index: i*2, boxPosition: "left", sharedData: sharedData)
                            Spacer()
                            if sharedData.playersNumber > i*2+1 {
                                PlayerToFollowCheckBox(index: i*2+1, boxPosition: "right", sharedData: sharedData)
                            }
                        }
                    }
                }
                Text("Scegli se riquadrare il pallone e/o i canestri:")
                    .font(.headline)
                Button(action: {
                    sharedData.boxBallToggle()
                    sharedData.saveData()
                }, label: {
                    HStack{
                        Image(systemName: sharedData.boxBall ? "checkmark.square": "square")
                            .foregroundColor(sharedData.boxBall ? .green : .black)
                        Text("Pallone")
                            .foregroundColor(.black)
                    }
                })
                Button(action: {
                    sharedData.boxBasketToggle()
                    sharedData.saveData()
                }, label: {
                    HStack{
                        Image(systemName: sharedData.boxBasket ? "checkmark.square": "square")
                            .foregroundColor(sharedData.boxBasket ? .green : .black)
                        Text("Canestri")
                            .foregroundColor(.black)
                    }
                })
                Text("Scegli per quali canestri mostrare l'effetto:")
                    .font(.headline)
                Button(action: {
                    sharedData.showAllGoals = true
                    sharedData.saveData()
                }, label: {
                    HStack{
                        Image(systemName: sharedData.showAllGoals ? "smallcircle.fill.circle": "circle")
                            .foregroundColor(sharedData.showAllGoals ? .green : .black)
                        Text("Tutti")
                            .foregroundColor(.black)
                    }
                })
                Button(action: {
                    sharedData.showAllGoals = false
                    sharedData.saveData()
                }, label: {
                    HStack{
                        Image(systemName: !sharedData.showAllGoals ? "smallcircle.fill.circle": "circle")
                            .foregroundColor(!sharedData.showAllGoals ? .green : .black)
                        Text("Solo se il tiratore è stato riconosciuto")
                            .foregroundColor(.black)
                    }
                })
            }
        }
    }
}

struct SettingsView_Previews: PreviewProvider {
    static var previews: some View {
        SettingsView(sharedData: SharedData())
    }
}
