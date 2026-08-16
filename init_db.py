import sqlite3

# 连接到数据库（如果不存在会自动创建）
conn = sqlite3.connect('blog.db')  #意思是sqlite3.connect('blog.db')链接到了数据库，然后把可以对这个数据库进行的第一级操作（打开数据库关闭数据库）给了conn保存
cursor = conn.cursor()  #把对数据库的具体操作（增删改查）打包给cursor

# 创建文章表
cursor.execute('''  
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
#cursor.execute的意思是执行如下命令
#CREATE TABLE IF NOT EXISTS posts是在数据库里建一张叫 posts 的表，如果已经存在就跳过
#id INTEGER PRIMARY KEY AUTOINCREMENT	"建一个编号列，自动编号，每条记录独一无二。"
#title TEXT NOT NULL	"建一个标题列，必须填文字。"
#content TEXT NOT NULL	"建一个内容列，必须填文字。"
#summary TEXT	"建一个摘要列，可以不填。"
#created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP	"建一个创建时间列，不填的话自动填当前时间。"
cursor.execute()

conn.commit()  #保存
conn.close()  #关闭数据库

print("✅ 数据库初始化完成！")