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
    ('Thats What I Like - Bruno Mars', 'happy', 'songs/happy/Thats What I Like - Bruno Mars.mp3'),
    ('Blue - Yung Kai', 'neutral', 'songs/neutral/Blue - Yung Kai.mp3'),
    ('Last Night On Earth - Green Day', 'neutral', 'songs/neutral/Last Night On Earth - Green Day.mp3'),    
    ('RISE - ft. The Glitch Mob, Mako, and The Word Alive', 'neutral', 'songs/neutral/RISE - ft. The Glitch Mob, Mako, and The Word Alive.mp3'),
    ('Maroon 5 Ft. Wiz Khalifa - Payphone', 'neutral', 'songs/neutral/Maroon 5 Ft. Wiz Khalifa - Payphone.mp3'),
    ('Immortals - Fall Out Boy', 'neutral', 'songs/neutral/Immortals - Fall Out Boy.mp3'),
    ('Harry Styles - Watermelon Sugar', 'happy', 'songs/happy/Harry Styles - Watermelon Sugar.mp3'),
    ('Jagwar Twin - Happy Face', 'happy', 'songs/happy/Jagwar Twin - Happy Face.mp3'),
    ('Justin Timberlake - CANT STOP THE FEELING!', 'happy', 'songs/happy/Justin Timberlake - CANT STOP THE FEELING!.mp3'),
    ('Eminem - Guts Over Fear ft. Sia', 'fear', 'songs/fear/Eminem - Guts Over Fear ft. Sia.mp3'),
    ('Hanuman Chalisa', 'fear', 'songs/fear/Hanuman Chalisa.mp3'),
    ('Nirvana - Stay Away', 'disgust', 'songs/disgust/Nirvana - Stay Away.mp3'),
    ('Imagine Dragons x JID - Enemy', 'angry', 'songs/angry/Imagine Dragons x JID - Enemy.mp3'),
    ('LET THE WORLD BURN - Chris Grey', 'angry', 'songs/angry/LET THE WORLD BURN - Chris Grey.mp3'),
    ('SAYGRACE - You Dont Own Me ft. G-Eazy', 'angry', 'songs/angry/SAYGRACE - You Dont Own Me ft. G-Eazy.mp3'),
    ('Lola Blanc-Angry Too', 'angry', 'songs/angry/Lola Blanc-Angry Too.mp3'),
    ('Chlöe - Surprise', 'surprise', 'songs/surprise/Chlöe - Surprise.mp3'),
    ('The Chainsmokers & Coldplay - Something Just Like This', 'surprise', 'songs/surprise/The Chainsmokers & Coldplay - Something Just Like This.mp3'),
    ('Joji - Die For You', 'sad', 'songs/sad/Joji - Die For You.mp3'),
    ('Tom Odell - Another Love', 'sad', 'songs/sad/Tom Odell - Another Love.mp3'),
    ('We The Kings ft. Elena Coats - Sad Song', 'sad', 'songs/sad/We The Kings ft. Elena Coats - Sad Song.mp3'),
    ('d4vd - Romantic Homicide', 'sad', 'songs/sad/d4vd - Romantic Homicide.mp3'),
    ('Olivia Rodrigo - Drivers License.mp3', 'sad', 'songs/sad/Olivia Rodrigo - Drivers License.mp3'),
    

]

# Insert songs into the songs table
cursor.executemany('INSERT INTO songs (title, emotion, path) VALUES (?, ?, ?)', songs)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database and songs table created successfully with sample songs inserted!")
