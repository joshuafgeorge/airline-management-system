# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
from datetime import datetime, time, timedelta

app = Flask(__name__)
CORS(app)

# MySQL connection
conn = pymysql.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    password='macbook2004',
    database='flight_tracking',
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=False
)

# Valid view names
VALID_VIEWS = {
    "flights_in_the_air",
    "flights_on_the_ground",
    "people_in_the_air",
    "people_on_the_ground",
    "route_summary",
    "alternative_airports"
}

class ValidationError(Exception):
    pass

def require_str(data, key, *, min_len=1, max_len=None, exact_len=None):
    v = data.get(key)
    if not isinstance(v, str):
        raise ValidationError(f"Missing or invalid '{key}': must be a string")
    if exact_len and len(v) != exact_len:
        raise ValidationError(f"'{key}' must be exactly {exact_len} characters")
    if len(v) < min_len or (max_len and len(v) > max_len):
        rng = f"{min_len}-{max_len}" if max_len else f"≥{min_len}"
        raise ValidationError(f"'{key}' length must be {rng}")
    return v

def require_int(data, key, *, min_val=None, max_val=None):
    if key not in data:
        raise ValidationError(f"Missing '{key}'")
    try:
        i = int(data[key])
    except:
        raise ValidationError(f"'{key}' must be an integer")
    if min_val is not None and i < min_val:
        raise ValidationError(f"'{key}' must be ≥ {min_val}")
    if max_val is not None and i > max_val:
        raise ValidationError(f"'{key}' must be ≤ {max_val}")
    return i

def require_bool(data, key):
    if key not in data:
        raise ValidationError(f"Missing '{key}'")
    v = data[key]
    if isinstance(v, bool):
        return v
    if isinstance(v, str) and v.lower() in ("true","false","1","0"):
        return v.lower() in ("true","1")
    raise ValidationError(f"'{key}' must be boolean ('true'/'false')")

def require_time(data, key):
    if key not in data or not isinstance(data[key], str):
        raise ValidationError(f"Missing or invalid '{key}'")
    try:
        datetime.strptime(data[key], "%H:%M:%S")
    except:
        raise ValidationError(f"'{key}' must be in HH:MM:SS format")
    return data[key]

def call_proc(name, args):
    with conn.cursor() as cur:
        cur.execute(f"CALL {name}({','.join(['%s']*len(args))})", args)
    conn.commit()

@app.route('/api/health', methods=['GET'])
def health():
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        return jsonify({"db":"ok"})
    except Exception as e:
        return jsonify({"db":"error","message":str(e)}),500

@app.route('/api/views/<view_name>', methods=['GET'])
def get_view(view_name):
    if view_name not in VALID_VIEWS:
        return jsonify({"error":"Invalid view"}),400
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM `{view_name}`")
        rows = cur.fetchall()
    for row in rows:
        for k,v in row.items():
            if isinstance(v,(datetime,time,timedelta)):
                row[k] = str(v)
    return jsonify(rows)

# 1) add_airplane
@app.route('/api/airplanes', methods=['POST'])
def add_airplane():
    d = request.json or {}
    try:
        airline      = require_str(d, "ip_airlineID", max_len=50)
        tail          = require_str(d, "ip_tail_num", max_len=50)
        seat_capacity = require_int(d, "ip_seat_capacity", min_val=1)
        speed         = require_int(d, "ip_speed", min_val=1)
        locationID    = d.get("ip_locationID")
        if locationID is not None:
            locationID = require_str(d, "ip_locationID", max_len=50)
        plane_type    = require_str(d, "ip_plane_type", max_len=100)
        maintenanced  = require_bool(d, "ip_maintenanced")
        model         = d.get("ip_model")
        neo           = d.get("ip_neo")
        # type-specific
        if plane_type.lower() == "airbus":
            if neo is None:
                raise ValidationError("Missing 'ip_neo' for Airbus")
            neo = require_bool(d, "ip_neo")
            model = None
        elif plane_type.lower() == "boeing":
            if not model:
                raise ValidationError("Missing 'ip_model' for Boeing")
            model = require_str(d, "ip_model", max_len=50)
            neo = None
        else:
            # allow either or none
            if model is not None:
                model = require_str(d, "ip_model", max_len=50)
            if neo is not None:
                neo = require_bool(d, "ip_neo")
        call_proc("add_airplane", [
            airline, tail, seat_capacity, speed,
            locationID, plane_type, maintenanced, model, neo
        ])
        return jsonify({"status":"OK"})
    except ValidationError as e:
        return jsonify({"error":str(e)}),400
    except Exception as e:
        return jsonify({"error":str(e)}),500

# 2) add_airport
@app.route('/api/airports', methods=['POST'])
def add_airport():
    d = request.json or {}
    try:
        airportID   = require_str(d, "ip_airportID", exact_len=3)
        name        = require_str(d, "ip_airport_name", max_len=200)
        city        = require_str(d, "ip_city", max_len=100)
        state       = require_str(d, "ip_state", max_len=100)
        country     = require_str(d, "ip_country", exact_len=3)
        locationID  = require_str(d, "ip_locationID", max_len=50)
        call_proc("add_airport", [
            airportID, name, city, state, country, locationID
        ])
        return jsonify({"status":"OK"})
    except ValidationError as e:
        return jsonify({"error":str(e)}),400
    except Exception as e:
        return jsonify({"error":str(e)}),500

# 3) add_person
@app.route('/api/people', methods=['POST'])
def add_person():
    d = request.json or {}
    try:
        personID   = require_str(d, "ip_personID", max_len=50)
        first_name = require_str(d, "ip_first_name", max_len=100)
        last_name  = d.get("ip_last_name","")
        if last_name:
            last_name = require_str(d, "ip_last_name", max_len=100)
        locationID = require_str(d, "ip_locationID", max_len=50)
        taxID      = d.get("ip_taxID")
        if taxID:
            taxID = require_str(d, "ip_taxID", max_len=50)
            experience = require_int(d, "ip_experience", min_val=0)
            miles = None
            funds = None
        else:
            experience = None
            miles = require_int(d, "ip_miles", min_val=0)
            funds = require_int(d, "ip_funds", min_val=0)
        call_proc("add_person", [
            personID, first_name, last_name,
            locationID, taxID, experience, miles, funds
        ])
        return jsonify({"status":"OK"})
    except ValidationError as e:
        return jsonify({"error":str(e)}),400
    except Exception as e:
        return jsonify({"error":str(e)}),500

# 4) grant_or_revoke_pilot_license
@app.route('/api/pilots/<person_id>/license', methods=['POST'])
def grant_revoke_license(person_id):
    d = request.json or {}
    try:
        if not person_id:
            raise ValidationError("Missing URL parameter 'person_id'")
        license = require_str(d, "ip_license", max_len=100)
        call_proc("grant_or_revoke_pilot_license", [
            person_id, license
        ])
        return jsonify({"status":"OK"})
    except ValidationError as e:
        return jsonify({"error":str(e)}),400
    except Exception as e:
        return jsonify({"error":str(e)}),500

# 5) offer_flight
@app.route('/api/flights', methods=['POST'])
def offer_flight():
    d = request.json or {}
    try:
        flightID         = require_str(d, "ip_flightID", max_len=50)
        routeID          = require_str(d, "ip_routeID", max_len=50)
        support_airline  = d.get("ip_support_airline")
        support_tail     = d.get("ip_support_tail")
        if (support_airline is None) ^ (support_tail is None):
            raise ValidationError(
                "Both 'ip_support_airline' and 'ip_support_tail' must be provided together or both omitted"
            )
        if support_airline:
            support_airline = require_str(d, "ip_support_airline", max_len=50)
            support_tail    = require_str(d, "ip_support_tail", max_len=50)
        progress         = require_int(d, "ip_progress", min_val=0)
        next_time_str    = require_time(d, "ip_next_time")
        cost             = require_int(d, "ip_cost", min_val=0)
        call_proc("offer_flight", [
            flightID, routeID,
            support_airline, support_tail,
            progress, next_time_str, cost
        ])
        return jsonify({"status":"OK"})
    except ValidationError as e:
        return jsonify({"error":str(e)}),400
    except Exception as e:
        return jsonify({"error":str(e)}),500

# 6) flight_landing
@app.route('/api/flights/<flight_id>/land', methods=['POST'])
def flight_landing_endpoint(flight_id):
    try:
        if not flight_id:
            raise ValidationError("Missing URL parameter 'flight_id'")
        call_proc("flight_landing", [flight_id])
        return jsonify({"status":"OK"})
    except ValidationError as e:
        return jsonify({"error":str(e)}),400
    except Exception as e:
        return jsonify({"error":str(e)}),500

# 7) flight_takeoff
@app.route('/api/flights/<flight_id>/takeoff', methods=['POST'])
def flight_takeoff_endpoint(flight_id):
    try:
        if not flight_id:
            raise ValidationError("Missing URL parameter 'flight_id'")
        call_proc("flight_takeoff", [flight_id])
        return jsonify({"status":"OK"})
    except ValidationError as e:
        return jsonify({"error":str(e)}),400
    except Exception as e:
        return jsonify({"error":str(e)}),500

# 8) passengers_board
@app.route('/api/flights/<flight_id>/board', methods=['POST'])
def passengers_board_endpoint(flight_id):
    try:
        if not flight_id:
            raise ValidationError("Missing URL parameter 'flight_id'")
        call_proc("passengers_board", [flight_id])
        return jsonify({"status":"OK"})
    except ValidationError as e:
        return jsonify({"error":str(e)}),400
    except Exception as e:
        return jsonify({"error":str(e)}),500

# 9) passengers_disembark
@app.route('/api/flights/<flight_id>/disembark', methods=['POST'])
def passengers_disembark_endpoint(flight_id):
    try:
        if not flight_id:
            raise ValidationError("Missing URL parameter 'flight_id'")
        call_proc("passengers_disembark", [flight_id])
        return jsonify({"status":"OK"})
    except ValidationError as e:
        return jsonify({"error":str(e)}),400
    except Exception as e:
        return jsonify({"error":str(e)}),500

# 10) assign_pilot
@app.route('/api/flights/<flight_id>/assign-pilot', methods=['POST'])
def assign_pilot_endpoint(flight_id):
    d = request.json or {}
    try:
        if not flight_id:
            raise ValidationError("Missing URL parameter 'flight_id'")
        person_id = require_str(d, "ip_personID", max_len=50)
        call_proc("assign_pilot", [flight_id, person_id])
        return jsonify({"status":"OK"})
    except ValidationError as e:
        return jsonify({"error":str(e)}),400
    except Exception as e:
        return jsonify({"error":str(e)}),500

# 11) recycle_crew
@app.route('/api/flights/<flight_id>/recycle-crew', methods=['POST'])
def recycle_crew_endpoint(flight_id):
    try:
        if not flight_id:
            raise ValidationError("Missing URL parameter 'flight_id'")
        call_proc("recycle_crew", [flight_id])
        return jsonify({"status":"OK"})
    except ValidationError as e:
        return jsonify({"error":str(e)}),400
    except Exception as e:
        return jsonify({"error":str(e)}),500

# 12) retire_flight
@app.route('/api/flights/<flight_id>', methods=['DELETE'])
def retire_flight_endpoint(flight_id):
    try:
        if not flight_id:
            raise ValidationError("Missing URL parameter 'flight_id'")
        call_proc("retire_flight", [flight_id])
        return jsonify({"status":"OK"})
    except ValidationError as e:
        return jsonify({"error":str(e)}),400
    except Exception as e:
        return jsonify({"error":str(e)}),500

# 13) simulation_cycle
@app.route('/api/simulation-cycle', methods=['POST'])
def simulation_cycle_endpoint():
    try:
        call_proc("simulation_cycle", [])
        return jsonify({"status":"OK"})
    except Exception as e:
        return jsonify({"error":str(e)}),500

if __name__ == "__main__":
    app.run(debug=True)