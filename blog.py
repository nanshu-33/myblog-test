from flask import Flask,render_template   #render_template() 是 Flask 提供的模板渲染函数
#它负责读取 templates/ 文件夹里的 HTML 文件，把数据填进去，然后返回完整的 HTML 页面。


# 创建 Flask 应用
app = Flask(__name__) # 1. 创建了一个叫 app 的 Flask 应用
 #__name__ 是 Python 给每个文件打的一个标签，如果文件是直接运行的，标签就是 '__main__'
#name在代码定义之初就指出当前运行代码的地址，以便于flask找到自己想要的文件，代码内部可以利用 __main__ 查到谁在执行，然后进一步给出地址。__name__的内部只存储两种值，代码直接运行时是main，被导入就是文件名
# 定义路由：用户访问 / 时，返回 "Hello, World!"
@app.route('/')   #route是路由表，这里相当于添加了一个对应关系，路由的概念就是用来连接函数和url对应表，是flask的理解用户操作的工具
def hello():
    return render_template('basic111.html')
# 2. 这个应用的功能是：当有人访问 / 时，返回 "Hello, World!"  

# 运行服务器
if __name__ == '__main__':
    app.run(debug=True)    # 3. 运行这个应用