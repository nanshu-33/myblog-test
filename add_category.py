"""import sqlite3

conn = sqlite3.connect('blog.db')
cursor = conn.cursor()


cursor.execute('ALTER TABLE posts ADD COLUMN user_id INTEGER REFERENCES users(id)')
cursor.execute('ALTER TABLE posts ADD COLUMN author VARCHAR(80)')
conn.commit()
conn.close()

print("✅列添加成功！")"""

from blog_4 import app, db
from blog_4 import User, Post  # 根据你的导入方式调整

with app.app_context():
    # 1️⃣ 找到 ID 为 8 的用户
    user = User.query.get(8)
    if not user:
        print('❌ 用户 ID 8 不存在！')
    else:
        # 2️⃣ 更新所有文章
        posts = Post.query.all()
        for post in posts:
            post.user_id = user.id
            post.author = user.username
        db.session.commit()
        print(f'✅ 已更新 {len(posts)} 篇文章，作者为 {user.username}')