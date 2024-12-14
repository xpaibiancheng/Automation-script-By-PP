import os
import re
import time
import requests
from app import db
from flask_cors import CORS
from sqlalchemy import func, inspect
from flask import Blueprint, request, jsonify
from app.admin.models import CardKey, Announcement

from app.main.models import Question, NewQuestion
import json  # 用于解析 JSON 字符串

user_bp = Blueprint('user', __name__, url_prefix='/user')
CORS(user_bp)  # 允许跨域请
# 设置上传文件的目录
IMAGES_FOLDER = './images'
os.makedirs(IMAGES_FOLDER, exist_ok=True)  # 如果目录不存在，则创建 'images' 文件夹

def object_to_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

@user_bp.route('/submit_answer', methods=['POST'])
def submit_answer():
    data = request.json
    if not data:
        return jsonify({'success': False, 'message': '未收到数据'})
    object_info_temp = data.get("style")
    new_ti_info = data.get('result')
    style_mapping = {
        '填空题': 'fill',
        '选择题': 'choice',
        '判断题': 'judge'
    }
    new_style = style_mapping.get(object_info_temp, None)
    if not new_style:
        return jsonify({"success": True, "message": "数据已接收", 'data': '暂无该题型'})
    # 步骤 1: 去掉换行符、空格等
    processed_sentence = re.sub(r'\s+', '', new_ti_info)
    print("检查所用关键词", processed_sentence)
    if object_info_temp == "填空题" :
        query = Question.query.filter(
            func.replace(Question.timu, '_', '') == processed_sentence,
            Question.style =='填空题'
        ).first()
    else:
        query = Question.query.filter(
            Question.timu == processed_sentence,
            Question.style == object_info_temp
        ).first()
    result = query.first()
    print("答案",result.answer)
    if result is None or not result:
        new_question = NewQuestion(
            timu=new_ti_info,
            answer='',
            style=new_style
        )
        db.session.add(new_question)
        db.session.commit()
        return jsonify({"success": True, "message": "数据已接收", 'data': '暂无该题型'})
    else:
        answer = result.answer
        print("答案", answer)
        return jsonify({'success': True, 'message': '数据已接收', 'data': answer})
@user_bp.route('/verify_key', methods=['POST'])
def verify_key():
    data = request.json

    keyWord = data.get('keySecret')  # 获取请求中的密钥

    print("前端发送的内容密钥", keyWord)

    if not keyWord:
        return jsonify({'success': False, 'message': '密钥不能为空'})

    # 查找数据库中的卡密记录
    card = CardKey.query.filter_by(key=keyWord).first()

    if not card:
        return jsonify({'success': False, 'message': '无效的密钥'})

    # 检查卡密是否被冻结
    if card.freeze_status == '1':
        return jsonify({'success': False, 'message': '该密钥已被冻结'})

    # 检查卡密是否已达到最大使用次数
    if card.use_count >= card.count:
        return jsonify({'success': False, 'message': '该密钥已达到最大使用次数'})

    card.status = True
    db.session.commit()
    # 密钥有效，返回卡密信息
    return jsonify({
        'success': True,
        'message': '密钥验证成功',
        'data': {
            'duration': card.duration,
            'generate_date': card.generate_date.strftime('%Y-%m-%d %H:%M:%S'),
            'use_count': card.use_count,
            'count': card.count
        }
    })

@user_bp.route('/cutkeycount', methods=['POST'])
def cut_key_count():
    # 获取请求的密钥信息
    data = request.json
    keySecret = data.get('keySecret')  # 获取前端发送的密钥信息

    # 验证密钥是否为空
    if not keySecret:
        return jsonify({'success': False, 'message': '密钥不能为空', 'data': 1})

    # 查询密钥表，找到对应的卡密记录
    card = CardKey.query.filter_by(key=keySecret).first()

    # 如果密钥不存在
    if not card:
        return jsonify({'success': False, 'message': '无效的密钥', 'data': 1})

    # 扣除一次使用次数
    card.use_count += 1
    updateCount = card.use_count
    # 检查卡密的剩余次数是否足够
    if card.count >= card.use_count:  # 剩余次数大于0
        db.session.commit()  # 提交更改到数据库
        # 返回成功状态，包含剩余次数信息
        return jsonify({
            'success': True,
            'message': '次数已成功扣除',
            'data': {
                'duration': card.duration,
                'generate_date': card.generate_date.strftime('%Y-%m-%d %H:%M:%S'),
                'use_count': updateCount,
                'count': card.count,
            }
        })
    # 如果剩余次数小于1
    return jsonify({'success': False, 'message': '次数已用完', 'data': 0})


@user_bp.route('/addkeycount', methods=['POST'])
def add_key_count():
    # 获取请求的密钥信息
    data = request.json
    keySecret = data.get('keySecret')  # 获取前端发送的密钥信息

    # 验证密钥是否为空
    if not keySecret:
        return jsonify({'success': False, 'message': '密钥不能为空', 'data': 0})

    # 查询密钥表，找到对应的卡密记录
    card = CardKey.query.filter_by(key=keySecret).first()

    # 如果密钥不存在
    if not card:
        return jsonify({'success': False, 'message': '无效的密钥', 'data': 0})

    # 增加使用次数（可以根据需求调整）
    card.use_count += 1
    updateCount = card.use_count
    db.session.commit()  # 提交更改到数据库

    # 返回成功状态，包含新的使用次数
    return jsonify({
        'success': True,
        'message': '次数已成功增加',
        'data': {
            'duration': card.duration,
            'generate_date': card.generate_date.strftime('%Y-%m-%d %H:%M:%S'),
            'use_count': updateCount,
            'count': card.count,
        }
    })


@user_bp.route('/announcementsone', methods=['GET'])
def get_announcements_one():
    # 获取最后一个公告（按创建时间降序排列）
    announcement = Announcement.query.order_by(Announcement.created_at.desc()).first()
    print(announcement)
    if announcement:
        return jsonify({
            'announcement': {
                'id': announcement.id,
                'title': announcement.title,
                'content': announcement.content,
                'created_at': announcement.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    else:
        return jsonify({'success': False, 'message': 'No announcements found'})



