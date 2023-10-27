from flask import Flask, render_template, request, send_from_directory
from PIL import Image
import os
import io
import base64

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    cropped_image = None

    if request.method == 'POST':
        file = request.files['file']
        crop_data = request.form

        x = int(float(crop_data["x"]))
        y = int(float(crop_data["y"]))
        w = int(float(crop_data["width"]))
        h = int(float(crop_data["height"]))

        image = Image.open(file)
        cropped_image = image.crop((x, y, x+w, y+h))
        cropped_image_path = os.path.join(UPLOAD_FOLDER, "cropped_image.jpg")
        cropped_image.save(cropped_image_path)

    return render_template('index.html', cropped_image=cropped_image_path if cropped_image else None)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
