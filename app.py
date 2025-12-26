from flask import Flask, request, redirect
import mysql.connector as mysql
import time

app = Flask(__name__)

db_config = {
    "host": "db",
    "user": "appuser",
    "password": "apppassword",
    "database": "appdb"
}

def get_db():
    return mysql.connect(**db_config)

def wait_for_db():
    while True:
        try:
            conn = mysql.connect(**db_config)
            conn.close()
            print("MySQL is ready")
            break
        except mysql.Error:
            print("Waiting for MySQL...")
            time.sleep(2)

# wait until MySQL is ready
wait_for_db()

# create table
conn = get_db()
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE,
    password VARCHAR(255)
)
""")
conn.commit()
cursor.close()
conn.close()

@app.route("/")
def home():
    return """
    <h2>Login</h2>
    <form method="post" action="/login">
        <input name="username" placeholder="Username" required><br><br>
        <input type="password" name="password" placeholder="Password" required><br><br>
        <button>Login</button>
    </form>
    <a href="/register">Register</a>
    """

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (request.form["username"], request.form["password"])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect("/")

    return """
    <h2>Register</h2>
    <form method="post">
        <input name="username" required><br><br>
        <input type="password" name="password" required><br><br>
        <button>Register</button>
    </form>
    <a href="/">Login</a>
    """

@app.route("/login", methods=["POST"])
def login():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        (request.form["username"], request.form["password"])
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    return "<h3>Login successful</h3>" if user else "<h3>Invalid credentials</h3>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
