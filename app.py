from flask import Flask, render_template, request, session, flash, redirect, url_for, jsonify
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import model_from_json
from PIL import Image
import io
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "sEcreTkEY"  # Replace with a strong secret key

# Initialize the database if not exists
def init_db():
    conn = sqlite3.connect("musicandface.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()


# Load the emotion detection model
model_path = "emotiondetector.json"
weights_path = "emotiondetector.h5"

if os.path.exists(model_path) and os.path.exists(weights_path):
    with open(model_path, "r") as json_file:
        model_json = json_file.read()
    model = model_from_json(model_json)
    model.load_weights(weights_path)
else:
    raise FileNotFoundError("Model files not found. Please ensure emotiondetector.json and emotiondetector.h5 are in the directory.")

# Labels for prediction output
labels = {0: 'angry', 1: 'disgust', 2: 'fear', 3: 'happy', 4: 'neutral', 5: 'sad', 6: 'surprise'}

# Load Haar cascade for face detection
haar_file = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(haar_file)

def preprocess_image(image):
    try:
        gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            face = cv2.resize(face, (48, 48))
            face = face.reshape(1, 48, 48, 1) / 255.0
            return face
    except Exception as e:
        print(f"Error in image preprocessing: {e}")
    return None

@app.route("/")
def index():
    return render_template("index.html")  # Serve index.html

@app.route("/recommend")
def recommend():
    # Check if the user is logged in
    if not session.get("username"):
        # Flash a message indicating login is required
        flash("Login first for recommendation.")
        # Redirect to the login page
        return redirect(url_for("login"))

    # If logged in, render the recommend page
    return render_template("recommend.html")  # Serve recommend.html

@app.route("/about")
def about():
    return render_template("about.html")  # Serve about.html

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        cpassword = request.form["cpassword"]

        # Validate form inputs
        if password != cpassword:
            flash("Passwords do not match. Please try again.", "danger")
            return redirect(url_for("signup"))

        try:
            conn = sqlite3.connect("musicandface.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user (username, email, password) VALUES (?, ?, ?)",
                           (username, email, password))
            conn.commit()
            conn.close()

            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username or email already exists. Please try again.", "danger")
            return redirect(url_for("signup"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            conn = sqlite3.connect("musicandface.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            conn.close()

            if user:
                session["username"] = username
                flash("Login successful!", "success")
                return redirect(url_for("index"))
            else:
                flash("Invalid username or password. Please try again.", "danger")
        except sqlite3.Error as e:
            flash(f"Database error: {e}", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/detect-emotion", methods=["POST"])
def detect_emotion():
    try:
        file = request.files["frame"].read()
        image = Image.open(io.BytesIO(file))

        face_image = preprocess_image(image)
        if face_image is None:
            return jsonify({"emotion": "No face detected"})

        prediction = model.predict(face_image)
        emotion = labels[np.argmax(prediction)]
        return jsonify({"emotion": emotion})

    except Exception as e:
        print(f"Error in emotion detection: {e}")
        return jsonify({"emotion": "Error in emotion detection"})

@app.route("/get-songs", methods=["GET"])
def get_songs():
    emotion = request.args.get("emotion")
    songs = []

    # try:
    #     conn = sqlite3.connect("musicandface.db")
    #     cursor = conn.cursor()
        
        # cursor.execute("SELECT title, path FROM songs WHERE emotion=?", (emotion,))
    try:
        conn = sqlite3.connect("musicandface.db")
        cursor = conn.cursor()

        if emotion:
            # Fetch songs for the specified emotion
            cursor.execute("SELECT title, path FROM songs WHERE emotion=?", (emotion,))
        else:
            # Fetch all songs if no emotion is specified
            cursor.execute("SELECT title, path FROM songs")
        
        songs = cursor.fetchall()
        conn.close()

        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify([])  # Return an empty list on error

    song_list = [{"title": song[0], "path": song[1]} for song in songs]
    return jsonify(song_list)

if __name__ == "__main__":
    app.run(debug=True)
