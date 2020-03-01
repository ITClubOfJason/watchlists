import os
import sys
import click
from flask import Flask
from flask import render_template,request,url_for,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import current_user,login_required,logout_user,LoginManager,UserMixin,login_user


app = Flask(__name__)

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///' # 如果是Windows系统，三个斜杠
else:
    prefix = 'sqlite:////'  # Mac， Linux， 四个斜杠


# 配置
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path,os.getenv('DATABASE_FILE','data.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 关闭对模型修改的监控
app.config['SECRET_KEY']= os.getenv('SECRET_KEY','dev')
db = SQLAlchemy(app)

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

# 自定义initdb
@app.cli.command()
@click.option('--drop', is_flag = True, help = '删除之后再创键')
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('初始化数据库')

#生成admin账号的函数
@app.cli.command()
@click.option('--username',prompt=True,help='用来登录的用户名')
@click.option('--password',prompt=True,hide_input=True,confirmation_prompt=True,help='用来登录的密码')
def admin(username,password):
    db.create_all()
    user = User.query.first()
    if user is not None:
        click.echo('更新用户')
        user.username = username
        user.set_password(password)
    else:
        click.echo('创建用户')
        user = User(username=username,name='蒋丰')
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    click.echo('创建管理员账号完成')


# flask-login  初始化操作
login_manager = LoginManager(app)  # 实例化扩展类
@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户ID作为参数
    user = User.query.get(int(user_id))
    return user
    
#
login_manager.login_view = 'login'
login_manager.login_manager = '没有登录'

    # 首页

@app.route('/',methods=['GET','POST'])
def index(): 
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return  redirect(url_for('index'))
    ariticles = Ariticle.query.all()
    return render_template('index.html', ariticles = ariticles)

@app.route('/insert',methods=['GET','POST'])
def insert():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
        # 获取表单的数据
        title = request.form['title']
        pubdate = request.form['pubdate']
        content = request.form['content']
        print(content)

        # 验证title，pubdate,content不为空，并且pubdate的长度不大于4
        if not title or not pubdate or not content or len(pubdate)>30 :
            flash('输入错误')  # 错误提示
            return redirect(url_for('insert'))  # 重定向回主页
        
        ariticle = Ariticle(title=title,pubdate=pubdate,content=content)  # 创建记录
        db.session.add(ariticle)  # 添加到数据库会话
        db.session.commit()   # 提交数据库会话
        flash('数据创建成功')
        return redirect(url_for('index'))

    return render_template('insert.html')

# 编辑电影信息页面
@app.route('/ariticle/edit/<int:ariticle_id>',methods=['GET','POST'])
@login_required
def edit(ariticle_id):
    ariticle = Ariticle.query.get_or_404(ariticle_id)

    if request.method == 'POST':
        title = request.form['title']
        pubdate = request.form['pubdate']
        content = request.form['content']
        print(content)

        if not title or not pubdate or not content or len(pubdate)>30:
            flash('输入错误')
            return redirect(url_for('edit'),ariticle_id=ariticle_id)
        ariticle.title = title
        ariticle.pubdate = pubdate
        ariticle.content = content
        db.session.commit()
        flash('博文信息已经更新')
        return redirect(url_for('index'))
    return render_template('edit.html',ariticle=ariticle)

#内容
@app.route('/ariticle/content/<int:ariticle_id>')
def content(ariticle_id):
    ariticle = Ariticle.query.get_or_404(ariticle_id)
    return render_template('content.html',ariticle=ariticle)




#设置
@app.route('/settings',methods=['GET','POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name)>20:
            flash('输入错误')
            return redirect(url_for('settings'))
        current_user.name = name
        db.session.commit()
        flash('设置name成功')
        return redirect(url_for('index'))

    return render_template('settings.html')


#删除信息
@app.route('/ariticle/delete/<int:ariticle_id>',methods=['POST'])
@login_required
def delete(ariticle_id):
    ariticle = Ariticle.query.get_or_404(ariticle_id)
    db.session.delete(ariticle)
    db.session.commit()
    flash('删除数据成功')
    return redirect(url_for('index'))


# 用户登录flask 提供的login——user（）函数
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('输入错误')
            return redirect(url_for('login'))
        user = User.query.first()
        if username == user.username and user.validate_password(password):
            login_user(user)  # 登录用户
            flash('登录成功')
            return redirect(url_for('index')) #登录成功返回首页
        
        flash('用户名或密码输入错误')
        return redirect(url_for('login'))
    return render_template('login.html')



# 用户登出
@app.route('/logout')
def logout():
    logout_user()
    flash('退出登录')
    return redirect(url_for('index'))




@app.errorhandler(404) # 传入要处理的错误代码
def page_not_found(e):
    return render_template('errors/404.html'),404
@app.errorhandler(400) # 传入要处理的错误代码
def bad_request(e):
    return render_template('errors/400.html'),400
@app.errorhandler(500) # 传入要处理的错误代码
def internal_server_error(e):
    return render_template('errors/500.html'),500

@app.context_processor  # 模板上下文处理函数
def inject_user():
    user = User.query.first()
    return dict(user=user)



