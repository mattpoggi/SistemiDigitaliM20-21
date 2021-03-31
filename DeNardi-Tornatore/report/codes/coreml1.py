import tfcoreml as tf_converter
tf_converter.convert(
            tf_model_path = './output/frozen_model.pb',
            mlmodel_path = './output/frozen.mlmodel',
            output_feature_names = ['Softmax:0'])
