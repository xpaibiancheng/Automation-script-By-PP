# app/admin/routes.py
import os
import string
import random
from app import db
import pandas as pd
from flask_cors import CORS
from sqlalchemy import inspect
from app.admin.models import Admin
from sqlalchemy.exc import SQLAlchemyError
from app.admin.models import CardKey, Announcement
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import create_access_token,jwt_required, get_jwt_identity
from app.main.models import ChoiceQuestionNew, JudgeQuestionNew, FillInBlankQuestionNew, NewQuestion, Question

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
CORS(admin_bp)  # 允许跨域请

@admin_bp.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    admin = Admin.query.filter_by(username=username).first()
    print(username,password,admin,admin.check_password(password))
    if admin and admin.check_password(password):
        access_token = create_access_token(identity=username)
        return jsonify(success=True, token=access_token, fullname=admin.fullname), 200
    else:
        return jsonify(success=False, message="账号密码错误"), 401

@admin_bp.route('/verify-token', methods=['GET'])
@jwt_required()
def verify_token():
    try:
        current_user = get_jwt_identity()
        return jsonify(isValid=True, user=current_user), 200
    except Exception as e:
        return jsonify(isValid=False, message=str(e)), 401
def object_to_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

'''
筛选题目
'''
@admin_bp.route('/question/filter', methods=['POST'])
def filter_questions():
    data = request.json
    query = data.get('query', '')  # 获取筛选的查询内容
    page = data.get('page', 1)  # 当前页
    per_page = data.get('per_page', 30)  # 每页条数

    results = Question.query.filter(Question.timu.like(f"%{query}%")).paginate(page=int(page), per_page=int(per_page),
                                                                               error_out=False)
    questions = [object_to_dict(result) for result in results.items]

    return jsonify({
        'total': results.total,
        'questions': questions,
        'page': results.page,
        'pages': results.pages
    })


@admin_bp.route('/question/collection', methods=['GET'])
def get_question_collection():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 30, type=int)

    results = Question.query.paginate(page, per_page, False)
    questions = [object_to_dict(result) for result in results.items]

    return jsonify({
        'total': results.total,
        'questions': questions,
        'page': results.page,
        'pages': results.pages
    })

@admin_bp.route('/question/byonebyadd', methods=['POST'])
def upload_question_batch():
    file = request.files.get('file')
    try:
        # 直接读取上传的文件对象
        df = pd.read_excel(file)
        # 将 DataFrame 中的 NaN 替换为 None
        df = df.where(pd.notnull(df), None)
        for _, row in df.iterrows():
            question = Question(
                timu=row['题目'],
                answer=row['答案'],
                style=row['题型']
            )
            db.session.add(question)
        db.session.commit()
        return jsonify({"success": True, "message": "题库导入成功！"})
    except Exception as e:
        db.session.rollback()
        print(str(e))
        return jsonify({"success": False, "message": f"导入失败: {str(e)}"})


@admin_bp.route('/question/updatetimu', methods=['POST'])
def update_timu():
    data = request.json
    question_id = data.get('id')
    new_timu = data.get('timu')

    question = Question.query.get(question_id)
    if not question:
        return jsonify({'success': False, 'message': 'Question not found.'})

    question.timu = new_timu
    try:
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@admin_bp.route('/question/updateanswer', methods=['POST'])
def update_answer_old():
    data = request.json
    question_id = data.get('id')
    new_answer = data.get('answer')

    question = Question.query.get(question_id)
    if not question:
        return jsonify({'success': False, 'message': 'Question not found.'})

    question.answer = new_answer
    try:
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@admin_bp.route('/question/deleteold', methods=['POST'])
def delete_question_one():
    data = request.json
    question_id = data.get('id')
    question = Question.query.get(question_id)
    if not question:
        return jsonify({'success': False, 'message': 'Question not found.'})

    try:
        db.session.delete(question)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


'''
单个添加新题目
'''
@admin_bp.route('/question/oneadd', methods=['POST'])
def add_question():
    data = request.json
    question = Question(
        timu=data.get('timu'),
        answer=data.get('answer'),
        style=data.get('style')
    )

    try:
        db.session.add(question)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


'''
删除新添加的题目
'''
@admin_bp.route('/questions/delete', methods=['POST'])
def delete_question():
    data = request.json
    question_type = data.get('type')
    question_id = data.get('id')
    print(question_type,question_id)
    try:
        question = NewQuestion.query.get(question_id)
        db.session.delete(question)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        print(str(e))
        return jsonify({'success': True,"message":str(e)})
'''
下载模板
'''
@admin_bp.route('/questions/download_template', methods=['GET'])
def download_template():

    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'files'))

    file_path = os.path.join(base_path, '统一导入题库模板.xlsx')

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"success": False, "message": "模板文件不存在！"})
@admin_bp.route('/questions/new', methods=['GET'])
def get_new_questions():
    GetNewQuestion = NewQuestion.query.all()
    results = []
    for question in GetNewQuestion:
        results.append({
            "id": question.id,
            "question": question.timu,
            "answer": question.answer,
            "type": question.style
        })
    return jsonify(results)


@admin_bp.route('/questions/new/<int:id>/edit', methods=['PUT'])
def edit_question(id):
    data = request.json
    question = (
        NewQuestion.query.get(id)
    )
    if question:
        question.timu = data.get("question", question.question)
        db.session.commit()
        return jsonify({"success": True, "message": "题目修改成功"})
    return jsonify({"success": False, "message": "记录不存在"})


@admin_bp.route('/questions/new/<int:id>/answer', methods=['PUT'])
def edit_answer(id):
    data = request.json
    question = (
        NewQuestion.query.get(id)
    )
    if question:
        question.answer = data.get("answer", question.answer)
        db.session.commit()
        return jsonify({"success": True, "message": "答案修订成功"})
    return jsonify({"success": False, "message": "记录不存在"})

# 通用更新函数
def get_question_model_by_type(question_type):
    if question_type == 'choice':
        return ChoiceQuestionNew
    elif question_type == 'judge':
        return JudgeQuestionNew
    elif question_type == 'fill':
        return FillInBlankQuestionNew
    else:
        return None

# 更新题目接口
@admin_bp.route('/questions/update-question', methods=['POST'])
def update_question():
    try:
        data = request.json
        question_id = data.get('id')
        new_question = data.get('question')
        question_type = data.get('type')
        print(question_type,question_id,new_question)
        if not question_id or not new_question or not question_type:
            return jsonify({'success': False, 'message': '参数缺失'}), 400

        question = NewQuestion.query.get(question_id)
        if not question:
            return jsonify({'success': False, 'message': '题目未找到'}), 404

        question.timu = new_question
        db.session.commit()

        return jsonify({'success': True, 'message': '题目修改成功'})

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'数据库错误: {str(e)}'}), 500

# 更新答案接口
@admin_bp.route('/questions/update-answer', methods=['POST'])
def update_answer():
    try:
        data = request.json
        question_id = data.get('id')
        new_answer = data.get('answer')
        question_type = data.get('type')

        if not question_id or not new_answer or not question_type:
            return jsonify({'success': False, 'message': '参数缺失'}), 400




        question = NewQuestion.query.get(question_id)
        if not question:
            return jsonify({'success': False, 'message': '题目未找到'}), 404

        question.answer = new_answer
        db.session.commit()

        return jsonify({'success': True, 'message': '答案修订成功'})

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'数据库错误: {str(e)}'}), 500


@admin_bp.route('/questions/review', methods=['POST'])
def review_question():
    """
    加入知识库逻辑
    """
    data = request.json
    question_id = data.get("id")
    question_type = data.get("type")  # 判断题型
    print(question_type, question_id)
    try:
        # 根据题型和 ID 获取待加入知识库的记录
        question = NewQuestion.query.get(question_id)

        if not question:
            return jsonify({'success': False, 'message': '未找到对应的题目'}), 404

        # 将数据插入到目标表 Question
        new_question = Question(
            timu=question.timu,
            answer=question.answer,
            style=question.style
        )
        db.session.add(new_question)

        # 删除 NewQuestion 表中的记录
        db.session.delete(question)

        # 提交事务
        db.session.commit()

        return jsonify({'success': True, 'message': '加入知识库成功，题目已删除'})

    except Exception as e:
        db.session.rollback()
        print(str(e))
        return jsonify({'success': False, 'message': f'加入知识库失败: {str(e)}'})


# 获取卡密信息
@admin_bp.route('/card-keys', methods=['GET'])
def get_card_keys():
    card_keys = CardKey.query.all()
    return jsonify({
        'card_keys': [
            {
                'id': key.id,
                'key': key.key,
                'duration': key.duration,
                'generate_date': key.generate_date.strftime('%Y-%m-%d %H:%M:%S'),
                'mac_address': key.mac_address,
                'status': '已使用' if key.status == '1' else '未使用',
                'use_count': key.use_count,
                'count': key.count,
                'freeze_status': '已冻结' if key.freeze_status == '1' else '未冻结',
            }
            for key in card_keys
        ]
    })


# 生成卡密
@admin_bp.route('/card-keys/generate', methods=['POST'])
def generate_card_key():
    data = request.json
    duration = data.get('duration')
    count = data.get('count')
    batch_count = data.get('batchCount', 1)  # 批量生成数量，默认为1

    if not duration or not count:
        return jsonify({'success': False, 'message': '时长和总次数是必须的'}), 400

    keys = []
    for _ in range(batch_count):
        key = ''.join(random.choices(string.ascii_letters + string.digits, k=24))
        card_key = CardKey(key=key, duration=duration, count=count)
        db.session.add(card_key)
        keys.append(card_key)

    db.session.commit()
    return jsonify({'success': True, 'message': f'{batch_count} 个卡密生成成功', 'generated_keys': [key.key for key in keys]})



# 增加天数
@admin_bp.route('/card-keys/add-days', methods=['POST'])
def add_days():
    data = request.json
    card_id = data.get('id')
    days = data.get('days')

    card_key = CardKey.query.get(card_id)
    if not card_key:
        return jsonify({'success': False, 'message': '卡密未找到'}), 404

    card_key.duration = f"{card_key.duration}+{days}天"
    db.session.commit()
    return jsonify({'success': True, 'message': '天数增加成功'})

# 冻结卡密
@admin_bp.route('/card-keys/freeze', methods=['POST'])
def freeze_card_key():
    data = request.json
    card_id = data.get('id')

    # 查询卡密信息
    card_key = CardKey.query.get(card_id)
    if not card_key:
        return jsonify({'success': False, 'message': '卡密未找到'}), 404

    # 确保 freeze_status 是字符串或整数，并进行类型处理
    freeze_status = str(card_key.freeze_status)  # 将状态转换为字符串进行对比

    if freeze_status == '1':  # 如果当前为冻结状态，则解冻
        card_key.freeze_status = '0'
    elif freeze_status == '0':  # 如果当前为未冻结状态，则冻结
        card_key.freeze_status = '1'
    else:
        return jsonify({'success': False, 'message': '未知冻结状态'}), 400

    # 提交更改
    db.session.commit()
    return jsonify({'success': True, 'message': '卡密冻结状态已更新'})


# 删除卡密
@admin_bp.route('/card-keys/delete', methods=['POST'])
def delete_card_key():
    data = request.json
    card_id = data.get('id')
    card_key = CardKey.query.get(card_id)
    if not card_key:
        return jsonify({'success': False, 'message': '卡密未找到'}), 404

    db.session.delete(card_key)
    db.session.commit()
    return jsonify({'success': True, 'message': '卡密已删除'})


@admin_bp.route('/announcements', methods=['GET'])
def get_announcements():
    announcements = Announcement.query.filter().all()
    return jsonify({
        'announcements': [{'id': a.id, 'title': a.title, 'content': a.content,
                           'created_at': a.created_at.strftime('%Y-%m-%d %H:%M:%S')} for a in announcements]
    })

@admin_bp.route('/announcements', methods=['POST'])
def create_announcement():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    if not title or not content:
        return jsonify({'success': False, 'message': 'Title and Content are required'})
    new_announcement = Announcement(title=title, content=content)
    db.session.add(new_announcement)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Announcement created successfully'})


@admin_bp.route('/announcements/<int:id>', methods=['DELETE'])
def delete_announcement(id):
    announcement = Announcement.query.get(id)
    if not announcement:
        return jsonify({'success': False, 'message': 'Announcement not found'})

    db.session.delete(announcement)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Announcement deleted successfully'})