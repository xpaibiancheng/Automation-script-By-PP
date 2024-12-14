# app/admin/models.py
from app import db, bcrypt
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(128))
    fullname = db.Column(db.String(128))

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
class LogoSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(64), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f'<LogoSetting {self.username} {self.image_path}>'
class OperationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    operator = db.Column(db.String(255), nullable=False)
    operation_time = db.Column(db.DateTime, nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    command = db.Column(db.Text, nullable=False)
    def __repr__(self):
        return f'<OperationLog {self.operator} at {self.operation_time}>'

class MultipleChoiceQuestion(db.Model):
    __tablename__ = 'multiple_choice_questions'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.Text, nullable=True)
    option_b = db.Column(db.Text, nullable=True)
    option_c = db.Column(db.Text, nullable=True)
    option_d = db.Column(db.Text, nullable=True)

class TrueFalseQuestion(db.Model):
    __tablename__ = 'true_false_questions'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)

class FillInTheBlankQuestion(db.Model):
    __tablename__ = 'fill_in_the_blank_questions'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)

class CardKey(db.Model):
    __tablename__ = 'card_keys'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键 ID')
    key = db.Column(db.String(255), nullable=False, unique=True, comment='卡密')
    duration = db.Column(db.String(255), nullable=False, comment='有效时长')
    generate_date = db.Column(db.DateTime, default=datetime.utcnow, comment='生成日期')
    mac_address = db.Column(db.String(255), nullable=True, comment='绑定的 Mac 地址')
    status = db.Column(db.Enum('0', '1'), default='0', comment='状态：0未使用，1已使用')
    use_count = db.Column(db.Integer, default=0, comment='使用次数')
    count = db.Column(db.Integer, nullable=False, comment='总次数')
    freeze_status = db.Column(db.Enum('0', '1'), default='0', comment='冻结状态：0未冻结，1冻结')


class Announcement(db.Model):
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)

    def __repr__(self):
        return f'<Announcement {self.id}: {self.title}>'





