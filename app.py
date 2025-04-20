from flask import Flask, request, jsonify, render_template
import redis
from datetime import datetime

app = Flask(__name__)
r = redis.Redis(host='redis', port=6379, decode_responses=True)


# Initialize vote counts and reset history
r.set('cats', 0)
r.set('dogs', 0)
r.delete('latest_history')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/vote', methods=['POST'])
def vote():
    vote = request.json.get('vote')
    if vote in ['cats', 'dogs']:
        r.incr(vote)
        save_history()
    return results()

@app.route('/results')
def results():
    cats = int(r.get('cats') or 0)
    dogs = int(r.get('dogs') or 0)
    total = cats + dogs
    cat_percent = round((cats / total) * 100, 1) if total > 0 else 0
    dog_percent = round((dogs / total) * 100, 1) if total > 0 else 0
    return jsonify({
        'cats': cats,
        'dogs': dogs,
        'cat_percent': cat_percent,
        'dog_percent': dog_percent
    })

@app.route('/history')
def history():
    history = r.get('latest_history')
    return jsonify({'history': history})

@app.route('/reset', methods=['POST'])
def reset():
    r.set('cats', 0)
    r.set('dogs', 0)
    r.delete('latest_history')
    return results()

def save_history():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cats = int(r.get('cats') or 0)
    dogs = int(r.get('dogs') or 0)
    r.set('latest_history', f"{now} — Cats: {cats}, Dogs: {dogs}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
