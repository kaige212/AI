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
import mmcv
import matplotlib.pyplot as plt
from mmagic.apis import MMagicInferencer

bp = Blueprint("ai", __name__, url_prefix="/ai")


@bp.route("/index")
def index():
    return render_template("ai/index.html")

@bp.route("/sr_image", methods=['GET', 'POST'])
@login_required
def sr_image():
    if request.method == 'POST':
        file = request.files['file']
        algo = str(request.form.get('algo_option'))
        #print(algo,type(algo))
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(g.user['id']))
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
        # 保存原图
        origin_image = os.path.join(user_folder, "origin_image.jpg")
        
        file.save(origin_image)
        


        action = request.form.get('action')
        if action == 'crop_and_super_resolve':
            crop_data = request.form
            x = int(float(crop_data["x"]))
            y = int(float(crop_data["y"]))
            w = int(float(crop_data["width"]))
            h = int(float(crop_data["height"]))

            image = Image.open(file)
            cropped_image_res = image.crop((x, y, x + w, y + h))


            cropped_image = os.path.join(user_folder, "cropped_image.jpg")
            cropped_image_res.save(cropped_image)

            chaofen_image=os.path.join(user_folder,"chaofen_image.jpg")
            
            algo_dic={'real_esrgan':'real_esrgan','swinir':'swinir','liif':'liif','rdn':'rdn','esrgan':'esrgan','real_esrgan_my':'real_esrgan'}

            #model_ckpt = os.path.join('./flaskr/static/model',algo+'.pth')
            model_ckpt = os.path.join('/home/aiservice/workspace/a/model',algo+'.pth')
            editor = MMagicInferencer(model_name=algo_dic[algo], model_ckpt=model_ckpt)
            results = editor.infer(img=cropped_image, result_out_dir=chaofen_image)
        elif action == 'super_resolve':
            file.seek(0)
            cropped_image = os.path.join(user_folder, "cropped_image.jpg")
            file.save(cropped_image)
            
            # For super-resolution without cropping, 
            # just use the original image directly
            chaofen_image = os.path.join(user_folder, "chaofen_image.jpg")
            algo_dic = {'real_esrgan': 'real_esrgan', 'swinir': 'swinir', 'liif': 'liif', 'rdn': 'rdn', 'esrgan': 'esrgan', 'real_esrgan_my': 'real_esrgan'}
            model_ckpt = os.path.join('/home/aiservice/workspace/a/model', algo + '.pth')
            editor = MMagicInferencer(model_name=algo_dic[algo], model_ckpt=model_ckpt)
            results = editor.infer(img=origin_image, result_out_dir=chaofen_image)
        

        return render_template("ai/sr_image.html",display=True if g.user['id'] else False)
    return render_template("ai/sr_image.html",display=True if g.user['id'] else False)

@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], str(g.user['id'])), filename)

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
