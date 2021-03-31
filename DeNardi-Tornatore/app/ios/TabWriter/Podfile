# Uncomment the next line to define a global platform for your project
# platform :ios, '9.0'

target 'TabWriter' do
  # Comment the next line if you don't want to use dynamic frameworks
  use_frameworks!

  # Pods for TabWriter
  pod 'Firebase/MLModelInterpreter'
  pod 'TensorFlowLiteSwift'
  pod 'Firebase/Analytics'
  pod 'Charts'
  pod 'TinyConstraints'
  pod 'mobile-ffmpeg-full-gpl', '~> 4.2'
  pod 'SwiftyJSON', '~> 4.0'
  pod 'Alamofire', '~> 5.2'

end

# You can setup your podfile to automatically match the deployment target of all the podfiles to your # current project deployment target like this :
post_install do |installer|
  installer.pods_project.targets.each do |target|
    target.build_configurations.each do |config|
      if Gem::Version.new('12.0') > Gem::Version.new(config.build_settings['IPHONEOS_DEPLOYMENT_TARGET'])
        config.build_settings['IPHONEOS_DEPLOYMENT_TARGET'] = '12.0'
      end
    end
  end
end