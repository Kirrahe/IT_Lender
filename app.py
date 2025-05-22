from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = 'library.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS reservations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id INTEGER NOT NULL,
                    user TEXT NOT NULL,
                    start TEXT NOT NULL,
                    end TEXT NOT NULL,
                    FOREIGN KEY(item_id) REFERENCES items(id)
                )''')
    conn.commit()
    conn.close()

@app.before_first_request
def setup():
    init_db()

@app.route('/items', methods=['GET'])
def list_items():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM items')
    items = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(items)

@app.route('/items', methods=['POST'])
def add_item():
    data = request.get_json() or {}
    name = data.get('name')
    description = data.get('description', '')
    if not name:
        return jsonify({'error': 'name required'}), 400
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO items(name, description) VALUES(?, ?)', (name, description))
    conn.commit()
    item_id = c.lastrowid
    conn.close()
    return jsonify({'id': item_id, 'name': name, 'description': description}), 201

@app.route('/items/<int:item_id>/reservations', methods=['GET'])
def list_reservations(item_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM reservations WHERE item_id=? ORDER BY start', (item_id,))
    reservations = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(reservations)

@app.route('/items/<int:item_id>/reserve', methods=['POST'])
def reserve_item(item_id):
    data = request.get_json() or {}
    user = data.get('user')
    start = data.get('start')
    end = data.get('end')
    if not all([user, start, end]):
        return jsonify({'error': 'user, start, and end required'}), 400
    # validate time format
    try:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
        if end_dt <= start_dt:
            raise ValueError()
    except Exception:
        return jsonify({'error': 'invalid date format or range'}), 400
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # check for conflict
    c.execute('''SELECT COUNT(*) FROM reservations WHERE item_id=? AND
                 NOT (? >= end OR ? <= start)''', (item_id, start, end))
    if c.fetchone()[0] > 0:
        conn.close()
        return jsonify({'error': 'time conflict'}), 409
    c.execute('INSERT INTO reservations(item_id, user, start, end) VALUES(?,?,?,?)',
              (item_id, user, start, end))
    conn.commit()
    res_id = c.lastrowid
    conn.close()
    return jsonify({'id': res_id, 'item_id': item_id, 'user': user, 'start': start, 'end': end}), 201

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0')
