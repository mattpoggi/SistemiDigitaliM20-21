import flask
import werkzeug
import os
from preprocessing import preprocessing_file
from flask import jsonify

app = flask.Flask(__name__)

@app.route('/')
def hello_world():
    print(__name__)
    return 'Digital Systems Project'

@app.route('/upload/', methods = ['POST'])
def handle_request():
    audiofile = flask.request.files['file']
    filename = werkzeug.utils.secure_filename(audiofile.filename)
    print("\nReceived audio File name : " + audiofile.filename)
    audiofile.save(filename)

    images, frames = preprocessing_file(filename)
    print(images.shape)
    print(frames)

    #result = predict_model(images)
    #print(result)

    os.remove(filename)

    return jsonify({"images": images.tolist(), "frames": frames})

if __name__=="__main__":
    #app.run(host="0.0.0.0", port=5000, debug=True)
    app.run(host="0.0.0.0", port=5000, debug=True)
