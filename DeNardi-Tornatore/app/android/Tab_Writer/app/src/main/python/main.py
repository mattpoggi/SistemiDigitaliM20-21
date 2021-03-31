from preprocessing import preprocessing_file
from predict import predict_model

def main(path):
	images, frames = preprocessing_file(path)
	result = predict_model(images, frames)

	return result