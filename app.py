from flask import Flask, render_template, request, redirect, session
from supabase import create_client
import uuid
import config

app = Flask(__name__)
app.secret_key = "secret123"

supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

# ---------- USER FLOW ----------

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")

        # check existing user
        existing = supabase.table("users").select("*").eq("email", email).execute()

        if existing.data:
            user = existing.data[0]
        else:
            new_user = supabase.table("users").insert({
                "name": name,
                "email": email
            }).execute()
            user = new_user.data[0]

        session["user_id"] = user["id"]
        session["name"] = user["name"]

        return redirect("/chat")

    return render_template("index.html")


@app.route("/chat")
def chat():
    if "user_id" not in session:
        return redirect("/")
    return render_template("chat.html", user_id=session["user_id"], name=session["name"])


# ---------- ADMIN ----------

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin/dashboard")

    return render_template("admin_login.html")


@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect("/admin")

    users = supabase.table("users").select("*").execute().data
    return render_template("admin.html", users=users)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
    

if __name__ == "__main__":
    app.run(debug=True)