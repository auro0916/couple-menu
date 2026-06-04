from flask import Flask, render_template, request, redirect, url_for, flash
import os
import json

app = Flask(__name__)
# 设置密钥以支持闪现消息（flash message），生产环境请用随机字符串
app.secret_key = 'nailong_kitchen_secret_key'

MENU_FILE = os.path.join("data", "menu.json")
ORDERS_FILE = os.path.join("data", "orders.json")
USERS_FILE = os.path.join("data", "users.json")

# 辅助函数：读取用户数据
def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

# 辅助函数：将用户列表写入 JSON 文件
def save_users(users):
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            # indent=2 可以让 JSON 格式化排版，方便人类阅读
            json.dump(users, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

# 新增注册路由
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        
        # 1. 加载现有用户
        users = load_users()
        
        # 2. 检查用户名是否已经存在
        for user in users:
            if user['username'] == username:
                flash("该用户名已被注册，请换一个！")
                return redirect(url_for('register'))
        
        # 3. 构建新用户对象（匹配你现有的 JSON 字段结构）
        new_user = {
            "username": username,
            "password": password,
            "order_count": 0,    # 初始订单数为 0
            "role": "user"       # 默认注册为普通用户
        }
        
        # 4. 追加并保存
        users.append(new_user)
        if save_users(users):
            flash("注册成功！请登录。")
            return redirect(url_for('login')) # 注册成功后跳转到登录页
        else:
            flash("注册保存失败，请稍后再试。")
            return redirect(url_for('register'))

    # GET 请求时渲染注册页面
    return render_template("register.html")

@app.route('/')
def home():
    return render_template("index.html")

# 修改登录路由，支持 GET（显示页面）和 POST（提交表单）
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 获取表单提交的数据
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 加载 JSON 中的用户列表
        users = load_users()
        
        # 校验用户名和密码
        user_found = None
        for user in users:
            if user['username'] == username and user['password'] == password:
                user_found = user
                break
        
        if user_found:
            # 登录成功，根据角色跳转（这里临时都跳到首页，你可以根据需求修改）
            # if user_found['role'] == 'merchant': 
            #     return redirect(url_for('admin'))
            return redirect(url_for('home'))
        else:
            # 登录失败，向模板发送错误提示
            flash("用户名或密码错误，请重试！")
            return redirect(url_for('login'))
            
    # GET 请求时直接渲染页面
    return render_template("login.html")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
