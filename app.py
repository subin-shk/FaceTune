from flask import Flask, render_template, request, session, flash, redirect, url_for, jsonify, make_response
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
            password TEXT NOT NULL,
            user_type TEXT NOT NULL DEFAULT 'user'
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
        flash("Login first for Recommendation.")
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
            cursor.execute("SELECT user_type FROM user WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            conn.close()

            if user:
                session["username"] = username
                session["user_type"] = user[0]  # Store user_type in session
                flash("Login successful!", "success")

                # Check user type and redirect accordingly
                if user[0] == "admin":
                    flash("You have logged in as admin", "success")  # Flash message for admin
                    return redirect(url_for("admin_dashboard"))
                else:
                    return redirect(url_for("index"))
            else:
                flash("Invalid username or password. Please try again.", "danger")
        except sqlite3.Error as e:
            flash(f"Database error: {e}", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")



@app.route("/admin/admin-dashboard")
def admin_dashboard():
    # Check if the user is logged in and has admin privileges
    if session.get("user_type") == "admin":
        try:
            conn = sqlite3.connect("musicandface.db")
            cursor = conn.cursor()

            # Count the number of users
            cursor.execute("SELECT COUNT(*) FROM user")
            user_count = cursor.fetchone()[0]

            # Count the number of songs
            cursor.execute("SELECT COUNT(*) FROM songs")
            song_count = cursor.fetchone()[0]

            conn.close()
        except sqlite3.Error as e:
            flash(f"Database error: {e}", "danger")
            return redirect(url_for("login"))

        return render_template("admin/admin-dashboard.html", user_count=user_count, song_count=song_count)
    else:
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for("login"))
    

@app.route("/admin/view-users")
def view_users():
    if session.get("user_type") == "admin":
        try:
            conn = sqlite3.connect("musicandface.db")
            conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            cursor = conn.cursor()

            # Fetch user details, including user type
            cursor.execute("SELECT user_id, username, email, user_type FROM user")
            users = cursor.fetchall()
            conn.close()

            # Render the view-user template and pass the users list
            return render_template("admin/view-user.html", users=users)
        except sqlite3.Error as e:
            flash(f"Database error: {e}", "danger")
            return redirect(url_for("admin_dashboard"))
    else:
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for("login"))


@app.route("/admin/delete-user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    try:
        conn = sqlite3.connect("musicandface.db")
        cursor = conn.cursor()

        cursor.execute("DELETE FROM user WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

        # Flash a success message after deletion
        flash("User deleted successfully!", "success")

        # Redirect to the view_users route
        return redirect(url_for('view_users')) 
    except sqlite3.Error as e:
        flash(f"Error deleting user: {e}", "danger")
        return redirect(url_for('view_users'))
   



@app.route("/admin/view-songs")
def view_songs():
    if session.get("user_type") == "admin":
        try:
            conn = sqlite3.connect("musicandface.db")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Query to fetch songs grouped by emotion
            cursor.execute("SELECT emotion, title, path, id FROM songs")
            songs = cursor.fetchall()
            conn.close()

            # Group songs by emotion
            grouped_songs = {}
            for song in songs:
                emotion = song["emotion"]
                if emotion not in grouped_songs:
                    grouped_songs[emotion] = []
                grouped_songs[emotion].append(song)

            return render_template("admin/view-songs.html", grouped_songs=grouped_songs)
        except sqlite3.Error as e:
            flash(f"Database error: {e}", "danger")
            return redirect(url_for("admin_dashboard"))
    else:
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for("login"))


@app.route("/admin/edit-song/<int:song_id>", methods=["GET", "POST"])
def edit_song(song_id):
    if session.get("user_type") == "admin":
        conn = sqlite3.connect("musicandface.db")
        conn.row_factory = sqlite3.Row  # This makes rows accessible as dictionaries
        cursor = conn.cursor()

        if request.method == "POST":
            title = request.form["title"]
            emotion = request.form["emotion"]
            path = request.form["path"]  # Add form field for `path`

            try:
                cursor.execute(
                    "UPDATE songs SET title = ?, emotion = ?, path = ? WHERE id = ?",
                    (title, emotion, path, song_id),
                )
                conn.commit()
                flash("Song updated successfully.", "success")
                return redirect(url_for("view_songs"))
            except sqlite3.Error as e:
                flash(f"Error updating song: {e}", "danger")
            finally:
                conn.close()

        else:  # GET request
            cursor.execute("SELECT id, title, emotion, path FROM songs WHERE id = ?", (song_id,))
            song = cursor.fetchone()  # Fetch the specific song as a dictionary
            conn.close()

            if song:
                return render_template("admin/edit-songs.html", song=song)
            else:
                flash("Song not found.", "danger")
                return redirect(url_for("view_songs"))
    else:
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for("login"))



@app.route("/admin/delete-song/<int:song_id>", methods=["POST"])
def delete_song(song_id):
    try:
        conn = sqlite3.connect("musicandface.db")
        cursor = conn.cursor()

        # Delete song from database using its ID
        cursor.execute("DELETE FROM songs WHERE id = ?", (song_id,))
        conn.commit()
        conn.close()

        flash("Song deleted successfully!", "success")
    except sqlite3.Error as e:
        flash(f"Error deleting song: {e}", "danger")

    return redirect(url_for("view_songs"))



@app.route("/admin/add-song", methods=["GET", "POST"])
def add_songs():
    if request.method == "POST":
        title = request.form["title"]
        emotion = request.form["emotion"]
        path = request.form["path"]

        try:
            conn = sqlite3.connect("musicandface.db")
            cursor = conn.cursor()

            cursor.execute("INSERT INTO songs (title, emotion, path) VALUES (?, ?, ?)", (title, emotion, path))
            conn.commit()
            conn.close()

            flash("Song added successfully!", "success")
            return redirect(url_for("add_songs"))
        except sqlite3.Error as e:
            flash(f"Database error: {e}", "danger")
            return redirect(url_for("add_songs"))

    return render_template("admin/add-songs.html")



@app.route("/logout")
def logout():
    session.clear()
    session.pop("username", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

# For logout even after moving back from browser
@app.after_request
def add_cache_control(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


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
