from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
from datetime import datetime, time, timedelta

app = Flask(__name__)
CORS(app)

conn = pymysql.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    password='PASSWORD',
    database='flight_tracking',
    cursorclass=pymysql.cursors.DictCursor,
    init_command="SET SESSION sql_mode=''"
)

def call_proc(name, args):
    with conn.cursor() as cur:
        cur.execute(f"CALL {name}({','.join(['%s']*len(args))})", args)
    conn.commit()

@app.route('/api/health', methods=['GET'])
def health():
    with conn.cursor() as cur:
        cur.execute("SELECT 1")
    return jsonify({"db": "ok"})

@app.route('/api/views/<view_name>', methods=['GET'])
def get_view(view_name):
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM `{view_name}`")
        rows = cur.fetchall()
    for row in rows:
        for k, v in row.items():
            if isinstance(v, (datetime, time, timedelta)):
                row[k] = str(v)
    return jsonify(rows)

@app.route('/api/airplanes', methods=['POST'])
def add_airplane():
    d = request.json or {}
    args = [
        d.get("ip_airlineID"),
        d.get("ip_tail_num"),
        d.get("ip_seat_capacity"),
        d.get("ip_speed"),
        d.get("ip_locationID"),
        d.get("ip_plane_type"),
        d.get("ip_maintenanced"),
        d.get("ip_model"),
        d.get("ip_neo")
    ]
    call_proc("add_airplane", args)
    return jsonify({"status": "OK"})

@app.route('/api/airports', methods=['POST'])
def add_airport():
    d = request.json or {}
    args = [
        d.get("ip_airportID"),
        d.get("ip_airport_name"),
        d.get("ip_city"),
        d.get("ip_state"),
        d.get("ip_country"),
        d.get("ip_locationID")
    ]
    call_proc("add_airport", args)
    return jsonify({"status": "OK"})

@app.route('/api/people', methods=['POST'])
def add_person():
    d = request.json or {}
    args = [
        d.get("ip_personID"),
        d.get("ip_first_name"),
        d.get("ip_last_name"),
        d.get("ip_locationID"),
        d.get("ip_taxID"),
        d.get("ip_experience"),
        d.get("ip_miles"),
        d.get("ip_funds")
    ]
    call_proc("add_person", args)
    return jsonify({"status": "OK"})

@app.route('/api/pilots/<person_id>/license', methods=['POST'])
def toggle_license(person_id):
    d = request.json or {}
    args = [person_id, d.get("ip_license")]
    call_proc("grant_or_revoke_pilot_license", args)
    return jsonify({"status": "OK"})

@app.route('/api/flights', methods=['POST'])
def offer_flight():
    d = request.json or {}
    args = [
        d.get("ip_flightID"),
        d.get("ip_routeID"),
        d.get("ip_support_airline"),
        d.get("ip_support_tail"),
        d.get("ip_progress"),
        d.get("ip_next_time"),
        d.get("ip_cost")
    ]
    call_proc("offer_flight", args)
    return jsonify({"status": "OK"})

@app.route('/api/flights/<flight_id>/land', methods=['POST'])
def flight_land(flight_id):
    call_proc("flight_landing", [flight_id])
    return jsonify({"status": "OK"})

@app.route('/api/flights/<flight_id>/takeoff', methods=['POST'])
def flight_takeoff(flight_id):
    call_proc("flight_takeoff", [flight_id])
    return jsonify({"status": "OK"})

@app.route('/api/flights/<flight_id>/board', methods=['POST'])
def flight_board(flight_id):
    call_proc("passengers_board", [flight_id])
    return jsonify({"status": "OK"})

@app.route('/api/flights/<flight_id>/disembark', methods=['POST'])
def flight_disembark(flight_id):
    call_proc("passengers_disembark", [flight_id])
    return jsonify({"status": "OK"})

@app.route('/api/flights/<flight_id>/assign-pilot', methods=['POST'])
def assign_pilot(flight_id):
    d = request.json or {}
    args = [flight_id, d.get("ip_personID")]
    call_proc("assign_pilot", args)
    return jsonify({"status": "OK"})

@app.route('/api/flights/<flight_id>/recycle-crew', methods=['POST'])
def recycle_crew(flight_id):
    call_proc("recycle_crew", [flight_id])
    return jsonify({"status": "OK"})

@app.route('/api/flights/<flight_id>', methods=['DELETE'])
def retire_flight(flight_id):
    call_proc("retire_flight", [flight_id])
    return jsonify({"status": "OK"})

@app.route('/api/simulation-cycle', methods=['POST'])
def simulation_cycle():
    call_proc("simulation_cycle", [])
    return jsonify({"status": "OK"})

if __name__ == "__main__":
    app.run(debug=True)