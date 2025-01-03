from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import os
from contextlib import contextmanager

app = Flask(__name__)

# Veritabanı yolunu belirle
DATABASE_PATH = '/opt/render/project/src/blogs.db'

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    # Veritabanı yoksa oluştur
    if not os.path.exists(DATABASE_PATH):
        with get_db() as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS blogs
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         baslik TEXT NOT NULL,
                         icerik TEXT NOT NULL,
                         tarih TEXT NOT NULL)''')
            conn.commit()

def load_blogs():
    with get_db() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM blogs order by id')
        blogs = [{'id': row[0], 'baslik': row[1], 'icerik': row[2], 'tarih': row[3]} 
                for row in c.fetchall()]
        return blogs

def save_blog(baslik, icerik):
    with get_db() as conn:
        c = conn.cursor()
        c.execute('INSERT INTO blogs (baslik, icerik, tarih) VALUES (?, ?, ?)',
                (baslik, icerik, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()

def update_blog(id, baslik, icerik):
    with get_db() as conn:
        c = conn.cursor()
        c.execute('UPDATE blogs SET baslik=?, icerik=?, tarih=? WHERE id=?',
                (baslik, icerik, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id))
        conn.commit()

def delete_blog_db(id):
    with get_db() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM blogs WHERE id=?', (id,))
        conn.commit()

@app.route('/')
def home():
    with get_db() as conn:
        c = conn.cursor()
        # SQL ile sıralama yap
        c.execute('SELECT * FROM blogs ORDER BY id ')
        blogs = [dict(row) for row in c.fetchall()]
    return render_template('index.html', blogs=blogs)

@app.route('/blog/<int:id>')
def blog_detail(id):
    with get_db() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM blogs WHERE id=?', (id,))
        row = c.fetchone()
        
    if row:
        blog = {'id': row[0], 'baslik': row[1], 'icerik': row[2], 'tarih': row[3]}
        return render_template('blog_detail.html', blog=blog)
    return redirect(url_for('home'))

@app.route('/yeni-blog', methods=['GET', 'POST'])
def new_blog():
    if request.method == 'POST':
        save_blog(request.form['baslik'], request.form['icerik'])
        return redirect(url_for('home'))
    return render_template('new_blog.html')

@app.route('/blog/sil/<int:id>')
def delete_blog_route(id):
    delete_blog_db(id)
    return redirect(url_for('home'))

@app.route('/blog/duzenle/<int:id>', methods=['GET', 'POST'])
def edit_blog(id):
    with get_db() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM blogs WHERE id=?', (id,))
        row = c.fetchone()
        
    if not row:
        return redirect(url_for('home'))
    
    blog = {'id': row[0], 'baslik': row[1], 'icerik': row[2], 'tarih': row[3]}
    
    if request.method == 'POST':
        update_blog(id, request.form['baslik'], request.form['icerik'])
        return redirect(url_for('blog_detail', id=id))
    
    return render_template('edit_blog.html', blog=blog)

if __name__ == '__main__':
    init_db()  # Veritabanı yoksa oluştur
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False) 