from watchlist import db
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
# 创建数据库模型类
class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key = True)  # 主键
    name = db.Column(db.String(20))
    username = db.Column(db.String(20)) # 用户名
    password_hash = db.Column(db.String(128)) # 密码散列值

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def validate_password(self, password):
        return check_password_hash(self.password_hash,password)

class Ariticle(db.Model):
    id = db.Column(db.Integer, primary_key = True)  # 主键
    title = db.Column(db.String(100))
    content = db.Column(db.String(20000))
    pubdate = db.Column(db.String(30))