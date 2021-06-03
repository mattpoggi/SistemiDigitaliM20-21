//
//  PlayerImageView.swift
//  LALakersAI
//
//  Created by Daniele Colautti on 12/01/21.
//

import SwiftUI

struct PlayerImageView: View {
    let player: String
    
    var body: some View {
        VStack {
            Image(player)
                .resizable()
                .scaledToFit()
                .mask(RoundedRectangle(cornerRadius: 20.0))
            Text(SharedData.extendedNameToShow(player: player))
                .bold()
        }
        .frame(width: 130, height: 150)
    }
}

let playersShortName = labels.dropLast(2)

struct PlayerImageView_Previews: PreviewProvider {
    static var previews: some View {
        ForEach(0..<playersShortName.count) { i in
            PlayerImageView(player: playersShortName[i])
        }
    }
}
