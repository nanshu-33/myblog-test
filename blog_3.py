from flask import Flask, render_template, request, redirect, url_for  
from datetime import datetime  # ← 导入 datetime

app = Flask(__name__)

all_posts = []  # 内存存储

@app.route('/')
def index():
    return render_template('content.html', posts=all_posts)

@app.route('/new', methods=['GET', 'POST'])  #这个网页可以接取两种请求
def new_post():
    if request.method == 'POST':
        title = request.form.get('title')  #request.form是一个类似字典的工具，会储存用户利用post命令输入的语句，然后用get取出数据，这里是取出键名为标题的内容
        content = request.form.get('content')
        #补充一个requst的用法：request.args.get('key')从 URL （一个地址）的查询参数（即 ? 后面的部分）中获取某个键所对应的值，搭配后续的函数功能，可以实现翻页搜索等一些功能
        
        if not title or not content:
            return '标题和内容都不能为空！', 400
        
        new_id = len(all_posts) + 1
        
        # ========== 自动生成简介 ==========
        summary = content[:100]      # 取前 100 个字符
        if len(content) > 100:
            summary += '...'         # 超过 100 字加省略号
        
        all_posts.append({
            'id': new_id,
            'title': title,
            'content': content,
            'summary': summary,      # ← 自动生成的简介
            'date': datetime.now().strftime('%Y-%m-%d')
            #datetime.now()生成当前日期，这行代码完整意思是：获取当前日期时间，然后格式化为 "年-月-日" 的字符串。
            #strftime→string format time→"字符串 格式化 时间"
        })
        
        return redirect(url_for('index'))  #这里也可以直接写首页的地址返回，但是这个写法更规范
    
    return render_template('new.html')

@app.route('/post/<int:post_id>')
def view_post(post_id):
    post = None
    for p in all_posts:
        if p['id'] == post_id:
            post = p
            break
    
    if post:
        return render_template('post.html', post=post)
    else:
        return '<h1>文章不存在</h1><a href="/">返回首页</a>', 404

if __name__ == '__main__':
    app.run(debug=True)   # 自动重启 + 错误页面调试  flask自带的功能