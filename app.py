from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from datetime import datetime
import os
import json

app = Flask(__name__)
app.secret_key = "your-secret-key-123"

MENU_FILE = "menu.json"
ORDERS_FILE = "orders.json"
USERS_FILE = "users.json"


def load_menu_data():
    with open(MENU_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_orders():
    if not os.path.exists(ORDERS_FILE):
        return []

    with open(ORDERS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_orders(orders):
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)


def load_users():
    if not os.path.exists(USERS_FILE):
        return []

    with open(USERS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def find_user(username):
    users = load_users()
    for user in users:
        if user["username"] == username:
            return user
    return None


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if not username or not password:
        return render_template("register.html", message="用户名和密码不能为空")

    if find_user(username):
        return render_template("register.html", message="用户名已存在")

    users = load_users()
    new_user = {
        "username": username,
        "password": password,
        "order_count": 0,
        "role": "user"
    }
    users.append(new_user)
    save_users(users)

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    user = find_user(username)

    if not user or user["password"] != password:
        return render_template("login.html", message="用户名或密码错误")

    session["username"] = user["username"]
    session["role"] = user["role"]

    if user["role"] == "merchant":
        return redirect(url_for("merchant_home"))

    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
def home():
    if "username" not in session:
        return redirect(url_for("login"))

    menu_data = load_menu_data()
    return render_template("index.html", menu_data=menu_data, username=session["username"])


@app.route("/checkout", methods=["POST"])
def checkout():
    if "username" not in session:
        return jsonify({
            "success": False,
            "message": "请先登录"
        }), 401

    data = request.get_json()
    cart = data.get("cart", {})

    if not cart:
        return jsonify({
            "success": False,
            "message": "购物车为空"
        }), 400

    total = 0
    order_items = []

    for name, item in cart.items():
        price_text = item.get("price", "0元")
        quantity = item.get("quantity", 0)

        price = float(price_text.replace("元", ""))
        item_total = price * quantity
        total += item_total

        order_items.append({
            "name": name,
            "price": price_text,
            "quantity": quantity,
            "item_total": f"{item_total}元"
        })

    order_id = "ORD" + datetime.now().strftime("%Y%m%d%H%M%S")
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    order = {
        "order_id": order_id,
        "username": session["username"],
        "status": "待接单",
        "created_at": created_at,
        "items": order_items,
        "total": f"{total}元"
    }

    orders = load_orders()
    orders.append(order)
    save_orders(orders)

    users = load_users()
    for user in users:
        if user["username"] == session["username"]:
            user["order_count"] = user.get("order_count", 0) + 1
            break
    save_users(users)

    return jsonify({
        "success": True,
        "message": "下单成功",
        "order": order,
        "redirect_url": f"/order/{order_id}"
    })


@app.route("/order/<order_id>")
def order_detail(order_id):
    if "username" not in session:
        return redirect(url_for("login"))

    orders = load_orders()

    target_order = None
    for order in orders:
        if order["order_id"] == order_id:
            target_order = order
            break

    if not target_order:
        return f"订单 {order_id} 不存在", 404

    # 普通用户只能看自己的订单
    if session.get("role") != "merchant" and target_order.get("username") != session["username"]:
        return "无权查看该订单", 403

    return render_template("order_detail.html", order=target_order)


@app.route("/orders")
def orders_list():
    if "username" not in session:
        return redirect(url_for("login"))

    # 商家不要走这个页面
    if session.get("role") == "merchant":
        return redirect(url_for("merchant_orders"))

    orders = load_orders()

    # 普通用户只看自己的订单
    orders = [order for order in orders if order.get("username") == session["username"]]

    # 最新订单排前面
    orders = list(reversed(orders))

    return render_template("orders.html", orders=orders, username=session["username"])


@app.route("/merchant/orders")
def merchant_orders():
    if "username" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "merchant":
        return "无权限访问商户订单页面", 403

    orders = load_orders()

    # 最新订单排前面
    orders = list(reversed(orders))

    return render_template("merchant_orders.html", orders=orders, username=session["username"])


@app.route("/merchant/order/<order_id>/status", methods=["POST"])
def update_order_status(order_id):
    if "username" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "merchant":
        return "无权限执行此操作", 403

    new_status = request.form.get("status", "").strip()

    allowed_status = ["待接单", "已接单", "制作中", "已完成", "已取消"]
    if new_status not in allowed_status:
        return "不支持的订单状态", 400

    orders = load_orders()
    target_order = None

    for order in orders:
        if order.get("order_id") == order_id:
            target_order = order
            break

    if not target_order:
        return f"订单 {order_id} 不存在", 404

    current_status = target_order.get("status", "")

    allowed_transitions = {
        "待接单": ["已接单", "已取消"],
        "已接单": ["制作中", "已取消"],
        "制作中": ["已完成", "已取消"],
        "已完成": [],
        "已取消": []
    }

    if new_status == current_status:
        return redirect(url_for("merchant_orders"))

    if new_status not in allowed_transitions.get(current_status, []):
        return f"订单状态不能从“{current_status}”改为“{new_status}”", 400

    target_order["status"] = new_status
    save_orders(orders)

    return redirect(url_for("merchant_orders"))


@app.route("/merchant")
def merchant_home():
    if "username" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "merchant":
        return "无权限访问商户端", 403

    return render_template("merchant_home.html", username=session["username"])


@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect(url_for("login"))

    return "<h1>个人中心页面开发中...</h1><p><a href='/'>返回首页</a></p>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)