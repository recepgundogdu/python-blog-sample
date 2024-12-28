from flask import Flask, render_template, request, redirect, url_for
import json
from datetime import datetime

app = Flask(__name__)

def load_blogs():
    try:
        with open('blogs.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_blogs(blogs):
    with open('blogs.json', 'w', encoding='utf-8') as file:
        json.dump(blogs, file, ensure_ascii=False, indent=4)

@app.route('/')
def home():
    blogs = load_blogs()
    blogs.sort(key=lambda x: x['tarih'], reverse=True)
    return render_template('index.html', blogs=blogs)

@app.route('/blog/<int:id>')
def blog_detail(id):
    blogs = load_blogs()
    blog = next((blog for blog in blogs if blog['id'] == id), None)
    if blog:
        return render_template('blog_detail.html', blog=blog)
    return redirect(url_for('home'))

@app.route('/yeni-blog', methods=['GET', 'POST'])
def new_blog():
    if request.method == 'POST':
        blogs = load_blogs()
        new_id = len(blogs) + 1
        new_blog = {
            'id': new_id,
            'baslik': request.form['baslik'],
            'icerik': request.form['icerik'],
            'tarih': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        blogs.append(new_blog)
        save_blogs(blogs)
        return redirect(url_for('home'))
    return render_template('new_blog.html')

@app.route('/blog/sil/<int:id>')
def delete_blog(id):
    blogs = load_blogs()
    blogs = [blog for blog in blogs if blog['id'] != id]
    save_blogs(blogs)
    return redirect(url_for('home'))

@app.route('/blog/duzenle/<int:id>', methods=['GET', 'POST'])
def edit_blog(id):
    blogs = load_blogs()
    blog = next((blog for blog in blogs if blog['id'] == id), None)
    
    if not blog:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        blog['baslik'] = request.form['baslik']
        blog['icerik'] = request.form['icerik']
        blog['tarih'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        save_blogs(blogs)
        return redirect(url_for('blog_detail', id=id))
    
    return render_template('edit_blog.html', blog=blog)

if __name__ == '__main__':
    app.run(debug=True) 