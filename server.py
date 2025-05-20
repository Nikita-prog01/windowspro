from flask import Flask, send_from_directory, render_template
from flask_cors import CORS
import os

app = Flask(__name__, static_url_path='')
CORS(app)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/terms.html')
def terms():
    return send_from_directory('.', 'terms.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    print("Сервер запущен на http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=True) 