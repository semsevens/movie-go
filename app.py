#-*- coding: utf-8 -*-

from flask import Flask, request, render_template, send_from_directory
from models.movies import Movies

app = Flask(__name__)

m = Movies()
movies = m.data()
labels = m.getLabels()
cinemasName = m.getCinemasName()
pinyinCn = m.getPinyinCn()

@app.route('/', methods = ['GET', 'POST'])
def home():
    movies = m.getData()
    return render_template('index.html', movies = movies, labels = labels, cinemasName = cinemasName, pinyinCn = pinyinCn)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)

@app.route('/lib/<path:path>')
def send_lib(path):
    return send_from_directory('lib', path)

@app.route('/images/<path:path>')
def send_images(path):
    return send_from_directory('images', path)

if __name__ == '__main__':
    app.run(debug = True)

