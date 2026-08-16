from flask import Flask, render_template, request, redirect, url_for,flash
import sqlite3  #导入数据库
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_user,login_required,logout_user,LoginManager,current_user
#为用户系统提供支撑，服务与user表
import os
from werkzeug.security import generate_password_hash,check_password_hash

#generate_password_hash   是处理密码的一个工具，在用户系统中一般都要使用

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-please-change-this-in-production'

#数据库相关概念：SQL数据库本质是一个有很多表格的文件，我们创建一个表格比如posts后，数据内容会存进表格当中，每一行在我们的博客中其实就是一篇文章，每一列是每个文章的属性，比如标题，内容等等。
#主键就是识别每一行数据的一个标志，通常是id，也可以是其他内容，id是自增的，比较方便
#SQL是轻量级的一个数据库，在很多编程环境下都可以使用，但数据上限低，且只能在本地使用
# ========== 数据库操作函数 ==========
login_manager = LoginManager()    # 1. 创建 LoginManager 实例
login_manager.init_app(app)    # 2. 初始化，绑定到 Flask 应用
login_manager.login_view = 'login'  # 未登录时跳转到登录页

@login_manager.user_loader   #每一次用户访问页面的时候，在后台运行,跳转页面的时候用它来查验一下用户身份
#user_id 来自 session，session 来自浏览器的 Cookie，Cookie 来自 login_user(user) 执行时服务器返回的响应
def load_user(user_id):  #意思是用id找信息，每次跳转页面都查一下用户
    return User.query.get(int(user_id))

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect('blog.db')
    conn.row_factory = sqlite3.Row  # 让查询结果可以用列名访问
    #给conn这个一级操作里的row_factory这个命令赋予了列名读取的功能，sqlite3.Row 是用列名访问的工具，只要 conn 的 row_factory 被使用了，就去使用这个工具。
    return conn  #这里conn是局部变量，我们要把局部变量的修改结果传递出去
#第一个函数规定好了conn里的标准访问操作，后续操作数据库的时候都要先调用第一个函数把操作规范，然后再进行后面的内容

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'blog.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Post(db.Model,UserMixin):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='未分类')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.Column(db.String(80))

class User(db.Model,UserMixin):     
#UserMixin是方便处理数据的一些操作,专门给用户数据的
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Comment(db.Model):     

    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    parent_id = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)



def get_all_comments():
    comment=Comment.query.order_by(Comment.created_at.desc()).all()
    return comment


def get_category_posts(post_category):
    conn = get_db()
    if current_user.is_admin:
        
        posts = conn.execute(
            'SELECT id, title, content, created_at, author, category FROM posts WHERE category = ? ORDER BY created_at DESC',
            (post_category,)
        ).fetchall()
    else:
        
        posts = conn.execute(
            'SELECT id, title, content, created_at, author, category FROM posts WHERE category = ? AND user_id = ? ORDER BY created_at DESC',
            (post_category, current_user.id)
        ).fetchall()
    conn.close()
    return posts

def get_category_user(author_name):
    posts = Post.query.filter_by(author=author_name).all()
    return posts

def get_all_posts():
    """获取所有文章，按时间倒序"""
    conn = get_db()  #打开数据库连接
    if current_user.is_admin:
       
        posts = conn.execute(
            'SELECT id, title, content, summary, created_at, author, category FROM posts ORDER BY created_at DESC'
        ).fetchall()
    else:
        posts = conn.execute(
        'SELECT id, title, content, summary, created_at, author,category FROM posts WHERE user_id = ? ORDER BY created_at DESC',  (current_user.id,) 
        #select是查询的意思，后续是要查询的列名， FEOM是告诉你从posts这张表里查询，
        # ORDER BY created_at DESC意思是取出的内容按照created_at内容倒叙排列，ASC是正序排列的意思
        ).fetchall() #查询到的所有结果一次性取出来。.fetchone()	只取第一条结果   .fetchmany(5)	只取前 5 条结果
    #取出来的结果会存储到posts这个变量中，posts本身是列表，每条数据（上述所有同文章的所有标签中的内容）是字典
    #这里可以使用ORM语句，效果相同：
    #posts = Post.query.order_by(Post.created_at.desc()).all()
    conn.close()  #关闭数据库连接
    return posts

def get_post_by_id(post_id):
    """根据 ID 获取单篇文章"""
    conn = get_db()
    if current_user.is_admin:
      
        post = conn.execute(
            'SELECT id, title, content, created_at, author, category FROM posts WHERE id = ?',
            (post_id,)
        ).fetchone()
    else:
        post = conn.execute(
            'SELECT id, title, content, created_at, author, category FROM posts WHERE id = ? AND user_id = ?',
            (post_id, current_user.id)
        ).fetchone() #输出查到的第一条数据，用post这个变量储存
    conn.close()
    return post

def create_post(title, content, summary, category,author,user_id):
    """创建新文章"""
    conn = get_db()
    conn.execute(
        'INSERT INTO posts (title, content, summary, category,author,user_id) VALUES (?, ?, ?, ?,?,?)',
        (title, content, summary, category,author,user_id)
        #INSERT INTO posts	往 posts 表里插入数据
        #(title, content, summary)	指定要插入的列（字段）
        #VALUES (?, ?, ?)	这三个 ? 是占位符，分别对应 title、content、summary
    )
    conn.commit()#保存存入的数据
    conn.close()

def create_comment( content, user_id,username,is_admin,parent_id):
        comment = Comment(  # ← ORM 方式
        is_admin = is_admin,
        content=content,
        parent_id = parent_id,
        username=username,
        user_id=user_id
    )
        db.session.add(comment)
        db.session.commit()

# ========== 路由 ==========

@app.route('/')

def index():
    posts = get_all_posts()  #调用了取出全部文章的函数
    authors = [a[0] for a in db.session.query(User.username).distinct().all()]
    return render_template('content.html', posts=posts,authors=authors)

@app.route('/article')
@login_required
def article_list():
    # 文章列表页（和首页一样，但可以分开）
    posts = get_all_posts() 
    return render_template('article.html', posts=posts)  

@app.route('/category/<string:category_name>')
@login_required
def category_post(category_name):
    posts=get_category_posts(category_name)
    return render_template('category.html', posts=posts, category_name=category_name)

@app.route('/author/<string:author_name>')
@login_required
def author_post(author_name):
    posts=get_category_user(author_name)
    return render_template('author.html', posts=posts, author_name=author_name)

    
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/new_comment', methods=['GET', 'POST'])
@login_required
def new_post_comment():
    if request.method == 'POST':
        content = request.form.get('content')
        parent_id = request.form.get('parent_id', 0, type=int)
        if not content :
            flash('评论内容不能为空！', 'error')
            return redirect(url_for('message'))


        user_id = current_user.id
        username = current_user.username
        is_admin = current_user.is_admin

        create_comment( content, user_id,username,is_admin,parent_id)
        return redirect(url_for('message'))
    comments = get_all_comments()
    return render_template('message.html',comments=comments)

        
@app.route('/new', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category = request.form.get('category', '未分类')  # ← 新增：从下拉框获取分类
        if not title or not content or not category:
            return render_template('new.html',error='标题,内容和分类都不能为空！')
        
        # 自动生成简介
        summary = content[:100]
        if len(content) > 100:
            summary += '...'
        
        # 存入数据库
        create_post(title, content, summary,category,current_user.username ,current_user.id)  #调用了存入文章数据的函数
        
        return redirect(url_for('index'))
    
    return render_template('new.html')

@app.route('/post/<int:post_id>')
@login_required
def view_post(post_id):
    post = get_post_by_id(post_id)   #调用了按id取出文章的函数
    
    if post:
        return render_template('post.html', post=post)
    else:
        return '<h1>文章不存在</h1><a href="/">返回首页</a>', 404
#删除文章的操作，由于我们日常访问网页几乎都是get操作，如果删除文章也使用就容易出现安全风险，所以这里是post命令，让用户发起删除操作
@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    conn = get_db()
    if current_user.is_admin:
        # 管理员：删任何文章
        conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    else:
        # 普通用户：只能删自己的
        conn.execute('DELETE FROM posts WHERE id = ? AND user_id = ?', (post_id, current_user.id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if current_user.is_admin or current_user.id == comment.user_id:
        db.session.delete(comment)
        db.session.commit()
        flash('评论已删除','success')  #函数运行到这，flash中存的这句话就会存进session（会话） 中，html的模版就会使用get_flashed_messages取出这些内容，存进变量中，然后弹窗渲染显示。
    else:
        flash('你没有权限删除这条评论', 'error')
       
        
    return redirect(url_for('message'))


@app.route('/post/<int:post_id>/edit', methods=['GET'])
@login_required
def edit_post(post_id):
    post = get_post_by_id(post_id)
    if not post:
        return '<h1>文章不存在</h1><a href="/">返回首页</a>', 404
    return render_template('edit.html', post=post)

@app.route('/post/<int:post_id>/edit', methods=['POST'])
@login_required
def update_post(post_id):
    title = request.form.get('title')
    content = request.form.get('content')
    category = request.form.get('category', '未分类')  # ← 新增

    
    if not title or not content or not category:
        return render_template('edit.html',error='标题,内容和分类都不能为空！')
    
    conn = get_db()
    if current_user.is_admin:
        conn.execute(
            'UPDATE posts SET title = ?, content = ?, category = ?, author = ? WHERE id = ?',
            (title, content, category, current_user.username, post_id)
        )
    else:
        conn.execute(
            'UPDATE posts SET title = ?, content = ?, category = ?, author = ? WHERE id = ? AND user_id = ?',
            (title, content, category, current_user.username, post_id, current_user.id)
        )
    conn.commit()
    conn.close()
    return redirect(url_for('view_post', post_id=post_id))

@app.route('/register',methods=['POST','GET'])  #注册页面
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if not username:
            return render_template('register.html', error='用户名不能为空')
        if not password:
            return render_template('register.html', error='密码不能为空')
        if password !=  confirm_password :
            return render_template('register.html', error='两次密码不一致')
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='用户名已被注册')

        hashed = generate_password_hash(password)
        user = User(username=username,password_hash=hashed)
        db.session.add(user)
        db.session.commit()
        return render_template('register.html', show_alert=True)
    return render_template('register.html')

@app.route('/login',methods=['POST','GET'])  #登录页面
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            #用当前用户输入的密码和数据库里这个用户名对应的密码进行比对
            #check_password_hash是把用户输入的密码也转化成哈希值看看和数据库里存着的一不一样
            login_user(user)  #用户通过身份验证后，建立并记录其登录会话,记录一下当前用户的登录状态是已登录
            if user.is_admin:
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('index'))
        else:
            return render_template('login.html', error='请检查密码或用户名')
    return render_template('login.html')

@app.route('/admin')
@login_required
def admin():
    conn = get_db()
    if not current_user.is_admin:
        return render_template('login.html', error='你没有权限访问此页面')
    user_count = User.query.count()
    post_count = conn.execute('SELECT COUNT(*) FROM posts').fetchone()[0]   #这里是查询第一列的总数，id列比较不容易出错
    
    users = User.query.order_by(User.id).all()
    for user in users:
        user.post_count = Post.query.filter_by(user_id=user.id).count()
    return render_template('admin.html', users=users,user_count=user_count, 
                         post_count=post_count)

@app.route('/admin/delete_user/<int:user_id>',methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if user_id == current_user.id:
        flash('不能删除自己','error')
        return redirect(url_for('admin'))
    user = User.query.get(user_id)
    if not user:
        flash('用户不存在','error')
        return redirect(url_for('admin'))
        
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/admin/reset_password/<int:user_id>',methods=['POST'])
@login_required
def admin_reset_password(user_id):
    
    user = User.query.get(user_id)
    if not user:
        return '用户不存在', 404
    
    user.password_hash = generate_password_hash('123456')
    db.session.commit()
    flash('重置密码成功','success')

    return redirect(url_for('admin'))

@app.route('/admin/add_user',methods=['GET','POST'])
@login_required
def admin_add_user():
    if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            password_hash = generate_password_hash(password)
            is_admin = request.form.get('is_admin') == 'on'  # 复选框，选中为 True 
            if not username:
                return render_template('admin_add_user.html', error='用户名不能为空')
            if not password:
                return render_template('admin_add_user.html', error='密码不能为空')
            if User.query.filter_by(username=username).first():
                return render_template('admin_add_user.html', error='用户名已被注册')
            if password !=  confirm_password :
                return render_template('admin_add_user.html', error='两次密码不一致')
            new_user = User(
            username=username,
            password_hash=password_hash,
            is_admin=is_admin
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('admin'))
    return render_template('admin_add_user.html')

@app.route('/message')
@login_required
def message():
    comments=get_all_comments()
    return render_template('message.html',comments=comments)

@app.route('/logout')
@login_required
def logout():
    logout_user()   #变成未登录状态
    return redirect(url_for('login'))


with app.app_context():
    db.create_all()
    print("✅ 数据库表已创建或已存在")



if __name__ == '__main__':
    app.run(debug=True)

