from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import joblib
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load ML model
model = joblib.load("spam_classifier.pkl")

# Ensure users file exists
def init_user_file():
    if not os.path.exists("users.xlsx"):
        df = pd.DataFrame(columns=["username", "password"])
        df.to_excel("users.xlsx", index=False)

init_user_file()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        df = pd.read_excel("users.xlsx")

        if ((df["username"] == username) & (df["password"] == password)).any():
            session["user"] = username
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="❌ Invalid credentials")

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        df = pd.read_excel("users.xlsx")
        if (df["username"] == username).any():
            return render_template("signup.html", error="⚠️ Username already exists")

        new_user = pd.DataFrame([[username, password]], columns=["username", "password"])
        df = pd.concat([df, new_user], ignore_index=True)
        df.to_excel("users.xlsx", index=False)
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/home", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    prediction = None
    if request.method == "POST":
        message = request.form["message"]
        pred = model.predict([message])[0]
        prediction = "🚫 Spam" if pred == 1 else "✅ Not Spam"
    return render_template("index.html", prediction=prediction)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
