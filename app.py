import streamlit as st
import sqlite3
import pandas as pd

# Initialisation de la base de données SQLite
conn = sqlite3.connect('app_database.db')
cursor = conn.cursor()

# Création de la table des utilisateurs si elle n'existe pas
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    points INTEGER DEFAULT 0
);
''')

# Création de la table des posts si elle n'existe pas
cursor.execute('''
CREATE TABLE IF NOT EXISTS posts (
    post_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    content TEXT,
    likes INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
''')

# Fonction pour ajouter un utilisateur
def add_user(username):
    cursor.execute('INSERT INTO users (username) VALUES (?)', (username,))
    conn.commit()

# Fonction pour ajouter un post
def add_post(user_id, content):
    cursor.execute('INSERT INTO posts (user_id, content) VALUES (?, ?)', (user_id, content))
    conn.commit()

# Fonction pour liker un post
def like_post(post_id):
    cursor.execute('UPDATE posts SET likes = likes + 1 WHERE post_id = ?', (post_id,))
    
    # Mettre à jour les points de l'utilisateur correspondant
    user_id = cursor.execute('SELECT user_id FROM posts WHERE post_id = ?', (post_id,)).fetchone()[0]
    cursor.execute('UPDATE users SET points = points + 1 WHERE user_id = ?', (user_id,))
    
    conn.commit()

# Fonction pour récupérer les posts par ordre chronologique
def get_posts():
    cursor.execute('SELECT * FROM posts ORDER BY post_id DESC')
    return cursor.fetchall()

# Interface Streamlit
st.title('Sanji tik-App')

# Récupérer le nom d'utilisateur
username = st.text_input('Entrez votre nom d\'utilisateur :')

# Vérifier si l'utilisateur existe dans la base de données
user = cursor.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

if st.button('Se connecter'):
    if user is None:
        add_user(username)
        user = cursor.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        st.success(f'Bienvenue, {username}!')

# Créer un post
st.subheader('Créer un nouveau post')
new_post_content = st.text_area('Contenu du post:')
if st.button('Publier'):
    if user is not None:
        add_post(user[0], new_post_content)
        st.success('Post publié avec succès!')

# Afficher les posts
st.subheader('New Post')
posts = get_posts()

if len(posts) > 0:
    current_post = posts[0]

    if st.button('❤️ Like'):
        like_post(current_post[0])
        user_points = cursor.execute('SELECT points FROM users WHERE user_id = ?', (user[0],)).fetchone()[0]
        st.success(f'Vous avez gagné un point! Total des points : {user_points + 1}')

    st.write(f'Post ID: {current_post[0]}')
    st.write(f'Contenu du post: {current_post[2]}')
    st.write(f'Likes: {current_post[3]}')
else:
    st.info('Aucun post disponible pour le moment.')

# Fermer la connexion à la base de données à la fin
conn.close()

# Section pour afficher le contenu de la base de données
st.title('Contenu de la base de données')

# Ouvrir une nouvelle connexion pour récupérer les données
conn_display = sqlite3.connect('app_database.db')
cursor_display = conn_display.cursor()

# Afficher le contenu de la table des utilisateurs avec Pandas
st.subheader('Table des utilisateurs')
users_data = cursor_display.execute('SELECT * FROM users').fetchall()
users_df = pd.DataFrame(users_data, columns=[col[0] for col in cursor_display.description])
st.write(users_df)

# Afficher le contenu de la table des posts avec Pandas
st.subheader('Table des posts')
posts_data = cursor_display.execute('SELECT * FROM posts').fetchall()
posts_df = pd.DataFrame(posts_data, columns=[col[0] for col in cursor_display.description])
st.write(posts_df)

# Fermer la nouvelle connexion à la fin de l'affichage des données
conn_display.close()
