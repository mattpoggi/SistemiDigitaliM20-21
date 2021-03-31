self.model_filename = "model.h5"
self.tflite_filename = "model.tflite"
        
def convert_tflite(self):
    model = load_model(self.save_path + self.model_filename, custom_objects={'softmax_by_string': self.softmax_by_string, 'avg_acc': self.avg_acc, 'catcross_by_string': self.catcross_by_string})
    converter = lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()
    open(self.save_path + self.tflite_filename, "wb").write(tflite_model)