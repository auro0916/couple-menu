from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import json

app = Flask(__name__)
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
            json.dump(users, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

# 辅助函数：读取菜单数据
def load_menu():
    if not os.path.exists(MENU_FILE):
        return []
    try:
        with open(MENU_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def group_menu_by_category(menu_data):
    if not menu_data:
        return []

    result = []

    # 你的 menu.json 是 dict 结构：
    # {
    #   "火锅底料": [...],
    #   "配菜(需搭配锅底)": [...]
    # }
    if isinstance(menu_data, dict):
        for category, items in menu_data.items():
            normalized_items = []
            for item in items:
                normalized_items.append({
                    "name": item.get("name", "未命名菜品"),
                    "price": item.get("price", "0元"),
                    "image": item.get("image", ""),
                    "desc": item.get("desc", "")
                })
            result.append({
                "category": category,
                "items": normalized_items
            })
        return result

    # 如果未来 menu.json 改成 list，也顺手兼容一下
    if isinstance(menu_data, list):
        first_item = menu_data[0] if len(menu_data) > 0 else None

        # 已经是 [{"category": "...", "items": [...]}]
        if isinstance(first_item, dict) and 'category' in first_item and 'items' in first_item:
            return menu_data

        grouped = {}
        for item in menu_data:
            if isinstance(item, dict):
                category = item.get('category', '其他')
                if category not in grouped:
                    grouped[category] = []
                grouped[category].append({
                    "name": item.get("name", "未命名菜品"),
                    "price": item.get("price", "0元"),
                    "image": item.get("image", ""),
                    "desc": item.get("desc", "")
                })

        for category, items in grouped.items():
            result.append({
                "category": category,
                "items": items
            })

    return result

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        
        users = load_users()
        
        for user in users:
            if user['username'] == username:
                flash("该用户名已被注册，请换一个！")
                return redirect(url_for('register'))
        
        new_user = {
            "username": username,
            "password": password,
            "order_count": 0,
            "role": "user"
        }
        
        users.append(new_user)
        if save_users(users):
            flash("注册成功！请登录。")
            return redirect(url_for('login'))
        else:
            flash("注册保存失败，请稍后再试。")
            return redirect(url_for('register'))

    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        users = load_users()
        
        user_found = None
        for user in users:
            if user['username'] == username and user['password'] == password:
                user_found = user
                break
        
        if user_found:
            session['username'] = user_found['username']
            session['role'] = user_found.get('role', 'user')
            return redirect(url_for('order_page'))
        else:
            flash("用户名或密码错误，请重试！")
            return redirect(url_for('login'))
            
    return render_template("login.html")

@app.route('/order')
def order_page():
    username = session.get('username')
    if not username:
        flash("请先登录后再点餐！")
        return redirect(url_for('login'))

    menu_data = load_menu()
    menu_categories = group_menu_by_category(menu_data)

    return render_template(
        "order.html",
        username=username,
        menu_categories=menu_categories
    )

@app.route('/logout')
def logout():
    session.clear()
    flash("您已退出登录。")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)