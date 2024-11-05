import sqlite3

# Connect to the database (this will create the file if it doesn't exist)
conn = sqlite3.connect('musicandface.db')
cursor = conn.cursor()

# Create the songs table
cursor.execute('''
CREATE TABLE IF NOT EXISTS songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    emotion TEXT NOT NULL,
    path TEXT NOT NULL
)
''')

# Sample songs to insert into the database
songs = [
    ('Pharrell Williams - Happy', 'happy', 'songs/happy/Pharrell Williams - Happy.mp3'),
    ('Blue - Yung Kai', 'neutral', 'songs/neutral/Blue - Yung Kai.mp3'),
    ('Maroon 5 Ft. Wiz Khalifa - Payphone', 'neutral', 'songs/neutral/Maroon 5 Ft. Wiz Khalifa - Payphone.mp3'),
    ('Harry Styles - Watermelon Sugar', 'happy', 'songs/happy/Harry Styles - Watermelon Sugar.mp3'),
    ('Justin Timberlake - CANT STOP THE FEELING!', 'happy', 'songs/happy/Justin Timberlake - CANT STOP THE FEELING!.mp3'),
    ('Eminem - Guts Over Fear ft. Sia', 'fear', 'songs/fear/Eminem - Guts Over Fear ft. Sia.mp3'),
    ('Hanuman Chalisa', 'fear', 'songs/fear/Hanuman Chalisa.mp3'),
    ('Nirvana - Stay Away', 'disgust', 'songs/disgust/Nirvana - Stay Away.mp3'),
    ('Lola Blanc-Angry Too', 'angry', 'songs/angry/Lola Blanc-Angry Too.mp3'),
    ('Chlöe - Surprise', 'surprise', 'songs/surprise/Chlöe - Surprise.mp3'),
    

]

# Insert songs into the songs table
cursor.executemany('INSERT INTO songs (title, emotion, path) VALUES (?, ?, ?)', songs)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database and songs table created successfully with sample songs inserted!")
