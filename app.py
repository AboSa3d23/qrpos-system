from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3




import sqlite3

conn = sqlite3.connect("restaurant.db")
c = conn.cursor()

# لو الجدول مش موجود اعمله
c.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_number INTEGER,
    item TEXT,
    status TEXT DEFAULT 'Pending'
)
""")

conn.commit()
conn.close()



app = Flask(__name__)
app.secret_key = "change_me_please"  # غيّرها لقيمة طويلة وعشوائية

# بيانات دخول الأدمن
ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# تخزين مؤقت في الذاكرة (من غير DB)
orders = []   # كل عنصر: {"id":..., "table":..., "item":..., "status":...}
next_id = 1   # عدّاد لرقم الطلب

ALLOWED_STATUSES = {"Pending", "Preparing", "Accepted", "Cancelled"}

@app.route("/")
def index():
    # صفحة الزبون/الكاشير البسيطة
    return render_template("home.html", orders=orders)

@app.route("/order", methods=["POST"])
def create_order():
    global next_id
    table = request.form.get("table", "").strip()
    item  = request.form.get("item", "").strip()
    if not table or not item:
        return redirect(url_for("index"))
    orders.append({
        "id": next_id,
        "table": int(table),
        "item": item,
        "status": "Pending"
    })
    next_id += 1
    # يرجّع تلقائي للصفحة الرئيسية بعد تسجيل الطلب
    return redirect(url_for("index"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username")
        pw   = request.form.get("password")
        if user == ADMIN_USER and pw == ADMIN_PASS:
            session["admin"] = True
            return redirect(url_for("admin_page"))
        return render_template("login.html", error="❌ اسم المستخدم أو كلمة المرور غير صحيح")
    return render_template("login.html")

@app.route("/admin")
def admin_page():
    if not session.get("admin"):
        return redirect(url_for("login"))
    # جدول بكل الطلبات + أزرار تغيير الحالة
    return render_template("admin.html", orders=orders)

@app.route("/update/<int:order_id>/<status>")
def update_status(order_id, status):
    if not session.get("admin"):
        return redirect(url_for("login"))
    if status not in ALLOWED_STATUSES:
        return redirect(url_for("admin_page"))
    for o in orders:
        if o["id"] == order_id:
            o["status"] = status
            break
    return redirect(url_for("admin_page"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    # للتشغيل المحلي
    app.run(host="0.0.0.0", port=5000, debug=True)
