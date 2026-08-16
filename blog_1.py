from flask import Flask,render_template

app = Flask(__name__)

@app.route('/')   

def index():
    posts_1 = [   #这里输入了一个类似数据库的内容在对应的html文件中会被引用，此处填入的内容就会动态的出现在网页中，注意需要对应
        {
            'title': 'Flask 入门教程',
            'date': '2026-07-22',
            'summary': 'Flask 是一个轻量级的 Python Web 框架，几行代码就能跑起一个网站。'
        },
        {
            'title': 'CSS Flexbox 布局详解',
            'date': '2026-07-21',
            'summary': 'Flexbox 是 CSS 的弹性盒子布局模型，是现代网页排版的必备技能。'
        }]
    return render_template('basic111.html', posts=posts_1)  #意思是模版按照basic111，内容按照posts_1.

if __name__ == '__main__':
    app.run(debug=True) 