from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from flask import current_app as app

from flask import Flask, render_template, request, send_from_directory
from PIL import Image
import os
import io
import base64
from flask import send_file

bp = Blueprint("ai", __name__, url_prefix="/ai")


@bp.route("/index")
def index():
    return render_template("ai/index.html")

@bp.route("/sr_image", methods=['GET', 'POST'])
def sr_image():
    cropped_image = None

    if request.method == 'POST':
        file = request.files['file']
        # 保存原图
        original_image_path = os.path.join(app.config['UPLOAD_FOLDER'], "original_image.jpg")
        file.save(original_image_path)

        crop_data = request.form
        x = int(float(crop_data["x"]))
        y = int(float(crop_data["y"]))
        w = int(float(crop_data["width"]))
        h = int(float(crop_data["height"]))

        image = Image.open(file)
        cropped_image = image.crop((x, y, x + w, y + h))
        cropped_image_path = os.path.join(app.config['UPLOAD_FOLDER'], "cropped_image.jpg")
        cropped_image.save(cropped_image_path)

    return render_template("ai/sr_image.html", cropped_image=cropped_image_path if cropped_image else None)

@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@bp.route("/sr_video", methods=['GET', 'POST'])
def sr_video():

    return render_template("ai/sr_video.html")


import random

@bp.route('/temp')
# @login_required
def temp():
    # video_folder = os.path.join(app.config['UPLOAD_FOLDER'],'video-enhancer.mp4')
    # videos = os.listdir(video_folder)
    # if not videos:
    #     abort(404, "No videos found in the specified directory")
    # selected_video = random.choice(videos)
    video_path = os.path.join(app.config['UPLOAD_FOLDER'],'video-enhancer.mp4')
    return send_file(video_path)


@bp.route('/video_display')
# @login_required
def video_display():
    return render_template('ai/video_display.html')
