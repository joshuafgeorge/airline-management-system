# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
from datetime import timedelta, datetime, time

app = Flask(__name__)
#CORS(app)
CORS(app)

conn = pymysql.connect(
    host='localhost',
    port=3306, #put ur local instance number (this was mine)
    user='root',
    password='PASSWORD',   ##put ur mysql password
    database='flight_tracking',
    cursorclass=pymysql.cursors.DictCursor
)

valid_views = [
    "flights_in_the_air", "flights_on_the_ground", "people_in_the_air", 
    "people_on_the_ground", "route_summary", "alternative_airports"
]

@app.route('/api/view/<name>', methods=['GET']) ## to get data
def get_view(name):
    if name not in valid_views:
        return jsonify({"error": "Invalid view name"}), 400
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM {name}")
        rows = cur.fetchall()
    
    # Convert all time/datetime objects to strings
    for row in rows:
        for key, value in row.items():
            if isinstance(value, (timedelta, datetime, time)):
                row[key] = str(value)

    return jsonify(rows)



@app.route('/api/procedure/<name>', methods=['POST']) #post used to submit data
def call_procedure(name):
    args = request.json.get('args', [])
    placeholders = ','.join(['%s'] * len(args))
    with conn.cursor() as cur:
        cur.execute(f"CALL {name}({placeholders})", args)
        conn.commit()
    return jsonify({"status": "OK"})



if __name__ == '__main__':
    app.run(debug=True)