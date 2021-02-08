//
//  CustomItemTabView.swift
//  LALakersAI
//
//  Created by Daniele Colautti on 02/12/20.
//

import SwiftUI

struct CustomItemTabView: View {
    var imageName: String
    var selected: Bool
    
    var body: some View {
        if selected {
            Image(systemName: imageName)
                .resizable()
                .frame(width: 25, height: 25)
                .foregroundColor(.orange)
                .padding()
                .overlay(
                    RoundedRectangle(cornerRadius: 10)
                        .stroke(Color.orange, lineWidth: 2)
                )
        } else {
            Image(systemName: imageName)
                .resizable()
                .frame(width: 15, height: 15)
                .foregroundColor(.gray)
                .padding()
        }
    }
}

struct CustomItemTabView_Previews: PreviewProvider {
    static var previews: some View {
        CustomItemTabView(imageName: "gearshape", selected: true)
        CustomItemTabView(imageName: "person", selected: false)
    }
}
