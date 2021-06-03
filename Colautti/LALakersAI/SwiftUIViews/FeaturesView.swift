//
//  FeaturesView.swift
//  LALakersAI
//
//  Created by Daniele Colautti on 11/01/21.
//

import SwiftUI

struct FeaturesView: View {
    @ObservedObject var sharedData: SharedData
    @State var selectedTab = 0
    
    var body: some View {
        VStack(spacing: 30) {
            HStack {
                CustomItemTabView(imageName: "gearshape", selected: selectedTab == 0)
                    .onTapGesture {
                        selectedTab = 0
                    }
                CustomItemTabView(imageName: "wallet.pass", selected: selectedTab == 1)
                    .onTapGesture {
                        selectedTab = 1
                    }
                CustomItemTabView(imageName: "person", selected: selectedTab == 2)
                    .onTapGesture {
                        selectedTab = 2
                    }
            }
            .padding(.horizontal, 30)
            
            if (selectedTab == 0) {
                SettingsView(sharedData: sharedData)
            } else if (selectedTab == 1) {
                StatisticsView(sharedData: sharedData)
            } else {
                LineUpView(sharedData: sharedData)
            }
            
            Spacer()
        }
        .animation(.easeInOut(duration: 0.3))
        .padding()
    }
}

struct FeaturesView_Previews: PreviewProvider {
    static var previews: some View {
        FeaturesView(sharedData: SharedData())
    }
}
