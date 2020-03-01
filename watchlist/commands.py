
import click
from watchlist import app,db
from watchlist.models import User,Ariticle





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
