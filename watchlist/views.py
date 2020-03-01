from watchlist import app,db
from flask import request,redirect,url_for,flash,render_template
from flask_login import login_user,logout_user,login_required,current_user
from watchlist.models import User,Ariticle
import re 
 
 
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
        re_h=re.compile('</?\w+[^>]*>')
        content=re_h.sub('',content)
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
        re_h=re.compile('</?\w+[^>]*>')
        content=re_h.sub('',content)
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
