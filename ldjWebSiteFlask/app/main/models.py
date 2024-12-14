
from app import db, bcrypt
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    registration_time = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, email):
        self.email = email

# 用户查询日志表
class UserQueryLog(db.Model):
    __tablename__ = 'user_query_logs'
    id = db.Column(db.Integer, primary_key=True)  # 主键
    user = db.Column(db.String(100), nullable=False)  # 用户账号
    code = db.Column(db.String(100), nullable=False)  # 查询的防伪码
    query_time = db.Column(db.DateTime, default=datetime.utcnow)  # 查询时间

class ChoiceQuestionNew(db.Model):
    __tablename__ = 'choice_question_new'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    review_status = db.Column(db.Integer, default=0)
class JudgeQuestionNew(db.Model):
    __tablename__ = 'judge_question_new'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    review_status = db.Column(db.Integer, default=0)
class FillInBlankQuestionNew(db.Model):
    __tablename__ = 'fill_in_blank_question_new'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    review_status = db.Column(db.Integer, default=0)

class Question(db.Model):
    __tablename__ = 'knowledge'  # 数据表名称
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键
    timu = db.Column(db.Text, nullable=False, comment="题目内容")  # 题目内容
    answer = db.Column(db.String(255), nullable=True, comment="答案")  # 答案，允许为空
    style = db.Column(db.String(255), nullable=False, comment="题目类型")  # 题目类型

class NewQuestion(db.Model):
    __tablename__ = 'new_knowledge'  # 数据表名称
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键
    timu = db.Column(db.Text, nullable=False, comment="题目内容")  # 题目内容
    answer = db.Column(db.String(255), nullable=True, comment="答案")  # 答案，允许为空
    style = db.Column(db.String(255), nullable=False, comment="题目类型")  # 题目类型