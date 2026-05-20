import os
import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    if not DATABASE_URL: return None
    conn = psycopg2.connect(DATABASE_URL)
    return conn

@app.route('/init', methods=['GET'])
def init_db():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS items (id SERIAL PRIMARY KEY, name VARCHAR(100) NOT NULL);")
        conn.commit()
        cur.close()
        conn.close()
    return jsonify({"status": "DB initialized"})

@app.route('/api/data', methods=['GET'])
def get_data():
    conn = get_db_connection()
    if not conn: return jsonify([])
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM items;")
    items = [{"id": row[0], "name": row[1]} for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(items)

@app.route('/api/data', methods=['POST'])
def add_data():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO items (name) VALUES (%s) RETURNING id;", (data['name'],))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": new_id, "name": data['name']}), 201

@app.route('/api/data/<int:item_id>', methods=['DELETE'])
def delete_data(item_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM items WHERE id = %s;", (item_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "deleted"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
