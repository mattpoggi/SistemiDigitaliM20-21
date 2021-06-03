//
//  LineUpView.swift
//  LALakersAI
//
//  Created by Daniele Colautti on 11/01/21.
//

import SwiftUI

struct LineUpView: View {
    var sharedData: SharedData
    
    var body: some View {
        ScrollView {
            HStack {
                if (sharedData.lastLineUp.count >= 1) {
                    PlayerImageView(player: sharedData.lastLineUp[0])
                }
                if (sharedData.lastLineUp.count >= 2) {
                    PlayerImageView(player: sharedData.lastLineUp[1])
                }
            }
            HStack {
                if (sharedData.lastLineUp.count >= 3) {
                    PlayerImageView(player: sharedData.lastLineUp[2])
                }
                if (sharedData.lastLineUp.count >= 4) {
                    PlayerImageView(player: sharedData.lastLineUp[3])
                }
            }
            if (sharedData.lastLineUp.count == 5) {
                PlayerImageView(player: sharedData.lastLineUp[4])
            }
        }
    }
}

struct LineUpView_Previews: PreviewProvider {
    static var previews: some View {
        LineUpView(sharedData: SharedData())
    }
}
