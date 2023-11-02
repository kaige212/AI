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

from flask import Flask, render_template, request, send_from_directory
from PIL import Image
import os
import io
import base64
from flask import send_file
import mmcv
import matplotlib.pyplot as plt
from mmagic.apis import MMagicInferencer
#from mmpose.apis import MMPoseInferencer

bp = Blueprint("ai", __name__, url_prefix="/ai")


@bp.route("/index")
def index():
    return render_template("ai/index.html")

@bp.route("/super_image", methods=['GET', 'POST'])
@login_required
def super_image():
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
        
        algo_dic={
            'real_esrgan':('real_esrgan','realesrnet_c64b23g32_12x4_lr2e-4_1000k_df2k_ost_20210816-4ae3b5a4.pth'),
            'real_esrgan_zk':('real_esrgan','zk_real_esrgan_best_PSNR_iter_222000.pth'),
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


            cropped_image = os.path.join(user_folder, "cropped_image.jpg")
            cropped_image_res.save(cropped_image)

            chaofen_image=os.path.join(user_folder,"chaofen_image.jpg")
            
            

            #model_ckpt = os.path.join('./flaskr/static/model',algo+'.pth')
            model_ckpt = os.path.join('/home/aiservice/workspace/model/super_image',algo_dic[algo][1])
            editor = MMagicInferencer(model_name=algo_dic[algo][0], model_ckpt=model_ckpt)
            results = editor.infer(img=cropped_image, result_out_dir=chaofen_image)
        elif action == 'super_resolve':
            file.seek(0)
            cropped_image = os.path.join(user_folder, "cropped_image.jpg")
            file.save(cropped_image)
            
            # For super-resolution without cropping, 
            # just use the original image directly
            chaofen_image = os.path.join(user_folder, "chaofen_image.jpg")
            model_ckpt = os.path.join('/home/aiservice/workspace/model/super_image', algo_dic[algo][1])
            editor = MMagicInferencer(model_name=algo_dic[algo][0], model_ckpt=model_ckpt)
            results = editor.infer(img=origin_image, result_out_dir=chaofen_image)

        return render_template("ai/super_image.html",display=True if g.user['id'] else False)
    return render_template("ai/super_image.html",display=True if g.user['id'] else False)

@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], str(g.user['id'])), filename)

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
            
            'real_esrgan_zk':('real_esrgan','realesrnet_c64b23g32_12x4_lr2e-4_1000k_df2k_ost_20210816-4ae3b5a4.pth'),
            'swinir':('swinir','swinir_x4s64w8d6e180_8xb4-lr2e-4-500k_df2k-0502d775.pth'),
            'swinir_xyh':('swinir','swinir_xyh_best_PSNR_iter_480000.pth'),
            'liif':('liif','liif_rdn_norm_c64b16_g1_1000k_div2k_20210717-22d6fdc8.pth'),
            'rdn':('rdn','rdn_x4c64b16_g1_1000k_div2k_20210419-3577d44f.pth'),
            'esrgan':('esrgan','esrgan_psnr_x4c64b23g32_1x16_1000k_div2k_20200420-bf5c993c.pth'),
        }
        model_ckpt = os.path.join('/home/aiservice/workspace/model/super_video', algo_dic[algo][1])
        editor = MMagicInferencer(model_name=algo_dic[algo][0], model_ckpt=model_ckpt)
        results = editor.infer(video=origin_video, result_out_dir=chaofen_video)

        # 返回结果
        return render_template("ai/super_video.html",display=True if g.user['id'] else False)
    
    return render_template("ai/super_video.html",display=True if g.user['id'] else False)


@bp.route("/pose_estimators", methods=['GET', 'POST'])
def pose_estimators ():
    if request.method == 'POST':
        file = request.files['file']
        algo = request.form.get('algo_option')
        
        # 生成用户的上传文件夹路径
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(g.user['id']))
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
        
        # 保存原视频
        origin_pose_video = os.path.join(user_folder, "origin_pose_video.mp4")
        file.save(origin_pose_video)

        # 执行视频超分辨率

        estimate_pose_video = os.path.join(user_folder, "estimate_pose_video.mp4")
        algo_dic = {
            'human': 'rtmpose-m_simcc-body7_pt-body7_420e-256x192-e48f03d0_20230504.pth', 
            'basicvsr': 'basicvsr', 
            'basicvsr_pp_my': 'basicvsr_pp',}
        model_ckpt = os.path.join('/home/aiservice/workspace/model/pose_estimators', algo_dic[algo])



        # 使用模型别名创建推断器
        inferencer = MMPoseInferencer('human')
        # MMPoseInferencer采用了惰性推断方法，在给定输入时创建一个预测生成器
        result_generator = inferencer(origin_pose_video, pred_out_dir='./',show=True)
        results = [result for result in result_generator]
        


        # 返回结果
        return render_template("ai/pose_estimators.html",display=True if g.user['id'] else False)
    
    return render_template("ai/pose_estimators.html",display=True if g.user['id'] else False)


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
