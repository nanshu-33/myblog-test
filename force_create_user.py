#import sqlite3

#conn = sqlite3.connect('blog.db')
#cursor = conn.cursor()

#cursor.execute('''
#    CREATE TABLE IF NOT EXISTS users (
#        id INTEGER PRIMARY KEY AUTOINCREMENT,
#        username TEXT NOT NULL UNIQUE,
#        password_hash TEXT NOT NULL,
#        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#        is_admin BOOLEAN DEFAULT 0
#    )
#''')

#conn.commit()
#conn.close()
#print("✅ users 表创建成功！")


import sqlite3

conn = sqlite3.connect('blog.db')
cursor = conn.cursor()



cursor.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        username TEXT NOT NULL,
        parent_id INTEGER DEFAULT 0,
        is_admin BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
print("✅ comments 表已创建")

conn.commit()
conn.close()
print("🎉 所有表创建完成！")