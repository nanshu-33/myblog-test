import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging

app = Flask(__name__)

# ===== 使用绝对路径 =====相对路径出现问题没办法直接连接到数据库文件，这里是绝对路径的代码
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'  相对路径代码是这样
BASE_DIR = r'D:\my_blog'
db_path = os.path.join(BASE_DIR, 'blog.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ===== 开启 SQL 日志，看实际执行了什么 =====
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

db = SQLAlchemy(app)

class Test(db.Model):
    __tablename__ = 'test'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

with app.app_context():
    print("正在创建表...")
    db.create_all()
    print("创建完成！")

# ===== 验证 =====
import sqlite3
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
conn.close()

print("当前数据库中的表：", tables)
if 'test' in tables:
    print("✅ test 表创建成功！")
else:
    print("❌ test 表仍然不存在")