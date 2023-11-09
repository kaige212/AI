from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort
import random
from flaskr.auth import login_required
from flaskr.db import get_db
from flask import current_app as app
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, send_from_directory
from PIL import Image
import os
import io
import base64
from flask import send_file
import mmcv
import matplotlib.pyplot as plt
# from mmagic.apis import MMagicInferencer
from mmpose.apis import MMPoseInferencer
import glob
import shutil
bp = Blueprint("ai", __name__, url_prefix="/ai")


@bp.route("/index")
def index():
    return render_template("ai/index.html")

@bp.route("/super_image", methods=['GET', 'POST'])
@login_required
def super_image():
    suffix='.png'
    
    if request.method == 'POST':
        file = request.files['file']
        algo = str(request.form.get('algo_option'))
        filename = secure_filename(file.filename)  # 获取安全的文件名
        suffix = os.path.splitext(filename)[1]  # 获取文件扩展名
        #print(algo,type(algo))
        user_folder_super_image = os.path.join(app.config['UPLOAD_FOLDER'], str(g.user['id']),'super_image')
        if not os.path.exists(user_folder_super_image):
            os.makedirs(user_folder_super_image)
        else:
            extensions = ['*.jpg', '*.jpeg', '*.png']
            for extension in extensions:
                for a in glob.glob(os.path.join(user_folder_super_image, extension)):
                    os.remove(a)
            
        # 保存原图
        origin_image = os.path.join(user_folder_super_image, "origin_image"+suffix)
        
        file.save(origin_image)
        
        algo_dic={
            'real_esrgan':('real_esrgan','realesrnet_c64b23g32_12x4_lr2e-4_1000k_df2k_ost_20210816-4ae3b5a4.pth'),
            'real_esrgan_zk':('real_esrgan','real_esrgan_zk_best_PSNR_iter_222000.pth'),
            'swinir':('swinir','swinir_x4s64w8d6e180_8xb4-lr2e-4-500k_df2k-0502d775.pth'),
            'swinir_xyh':('swinir','swinir_xyh_best_PSNR_iter_480000.pth'),
            'liif':('liif','liif_rdn_norm_c64b16_g1_1000k_div2k_20210717-22d6fdc8.pth'),
            'rdn':('rdn','rdn_x4c64b16_g1_1000k_div2k_20210419-3577d44f.pth'),
            'esrgan':('esrgan','esrgan_psnr_x4c64b23g32_1x16_1000k_div2k_20200420-bf5c993c.pth'),
        }

        action = request.form.get('action')
        if action == 'crop_and_super_resolve':
            crop_data = request.form
            x = int(float(crop_data["x"]))
            y = int(float(crop_data["y"]))
            w = int(float(crop_data["width"]))
            h = int(float(crop_data["height"]))

            image = Image.open(file)
            cropped_image_res = image.crop((x, y, x + w, y + h))


            cropped_image = os.path.join(user_folder_super_image, "cropped_image"+suffix)
            cropped_image_res.save(cropped_image)


            chaofen_image=os.path.join(user_folder_super_image,"chaofen_image"+suffix)
            
            #model_ckpt = os.path.join('./flaskr/static/model',algo+'.pth')
            model_ckpt = os.path.join('/home/aiservice/workspace/model/super_image',algo_dic[algo][1])
            editor = MMagicInferencer(model_name=algo_dic[algo][0], model_ckpt=model_ckpt)
            results = editor.infer(img=cropped_image, result_out_dir=chaofen_image)
        elif action == 'super_resolve':
            file.seek(0)
            cropped_image = os.path.join(user_folder_super_image, "cropped_image"+suffix)
            file.save(cropped_image)
            
            # For super-resolution without cropping, 
            # just use the original image directly
            chaofen_image = os.path.join(user_folder_super_image, "chaofen_image"+suffix)
            model_ckpt = os.path.join('/home/aiservice/workspace/model/super_image', algo_dic[algo][1])
            editor = MMagicInferencer(model_name=algo_dic[algo][0], model_ckpt=model_ckpt)
            results = editor.infer(img=origin_image, result_out_dir=chaofen_image)

        return render_template("ai/super_image.html",suffix=suffix,display=True if g.user['id'] else False)
    return render_template("ai/super_image.html",suffix=suffix,display=True if g.user['id'] else False)
'''
@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    file=[a for a in os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], str(g.user['id']))) if filename in a][0]
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], str(g.user['id'])), filename)
'''
@bp.route('/uploads/<user_id>/<folder>/<filename>')
def uploaded_file(user_id, folder, filename):
    directory = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id), folder)
    return send_from_directory(directory, filename)


@bp.route("/super_video", methods=['GET', 'POST']) 
@login_required
def super_video():
    if request.method == 'POST':
        file = request.files['file']
        algo = request.form.get('algo_option')
        
        # 生成用户的上传文件夹路径
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(g.user['id']))
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
        
        
        # 保存原视频
        origin_video = os.path.join(user_folder, "origin_video.mp4")
        file.save(origin_video)

        # 执行视频超分辨率

        chaofen_video = os.path.join(user_folder, "chaofen_video.mp4")
        algo_dic = {'basicvsr_pp': 'basicvsr_pp', 'basicvsr': 'basicvsr', 'basicvsr_pp_my': 'basicvsr_pp'}
        algo_dic={
            'basicvsr_pp':('basicvsr_pp','basicvsr_plusplus_c64n7_8x1_600k_reds4_20210217-db622b2f.pth'),
            'realbasicvsr':('realbasicvsr','realbasicvsr_c64b20_1x30x8_lr5e-5_150k_reds_20211104-52f77c2c.pth'),
            'iconvsr':('iconvsr','iconvsr_reds4_20210413-9e09d621.pth'),
            'basicvsr':('basicvsr','basicvsr_reds4_20120409-0e599677.pth'),
        }
        model_ckpt = os.path.join('/home/aiservice/workspace/model/super_video', algo_dic[algo][1])
        editor = MMagicInferencer(model_name=algo_dic[algo][0], model_ckpt=model_ckpt)
        results = editor.infer(video=origin_video, result_out_dir=chaofen_video)

        # 返回结果
        return render_template("ai/super_video.html",display=True if g.user['id'] else False)
    
    return render_template("ai/super_video.html",display=True if g.user['id'] else False)


@bp.route("/pose_estimators", methods=['GET', 'POST'])
def pose_estimators():
    if request.method == 'POST':
        file = request.files['file']
        algo = request.form.get('algo_option')

        # 获取上传的视频文件名并保证其安全性
        filename = secure_filename(file.filename)
        # 获取并保存视频的原始扩展名
        suffix = os.path.splitext(filename)[1]

        # 生成用户的上传文件夹路径
        user_folder_pose_estimators = os.path.join(app.config['UPLOAD_FOLDER'], str(g.user['id']), 'pose_estimators')
        if not os.path.exists(user_folder_pose_estimators):
            os.makedirs(user_folder_pose_estimators, exist_ok=True)

        # 保存原视频
        origin_video = os.path.join(user_folder_pose_estimators, "origin_video" + suffix)
        file.save(origin_video)

        algo_dic = {
            'human': ('configs/body_2d_keypoint/topdown_heatmap/coco/td-hm_hrnet-w32_8xb64-210e_coco-256x192.py','hrnet_w32_coco_256x192-c78dce93_20200708.pth'), 
            'basicvsr': 'basicvsr', 
            'basicvsr_pp_my': 'basicvsr_pp',}
        pose2d_config=os.path.join(app.config['UPLOAD_FOLDER'],algo_dic[algo][0])
        pose2d_weights = os.path.join('/home/aiservice/workspace/model/pose_estimators', algo_dic[algo][1])

        # 推力器
        inferencer = MMPoseInferencer(pose2d=pose2d_config,pose2d_weights=pose2d_weights,)

        # 推理并生成处理后的视频结果
        result_generator = inferencer(
            origin_video,
            show=False,
            out_dir=user_folder_pose_estimators,
            radius=4,
            thickness=2
        )
        results = [result for result in result_generator]

        #shutil.copy(os.path.join('user_folder_pose_estimators','visualizations'), destination_file)


        # 返回结果
        return render_template("ai/pose_estimators.html", display=True if g.user['id'] else False)
    return render_template("ai/pose_estimators.html", display=True if g.user['id'] else False)


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
