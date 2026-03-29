#!/usr/bin/env python3
import json
import os
import time
import hashlib
from flask import Flask, request, jsonify
from flask_cors import CORS
import OPi.GPIO as GPIO
import threading
import logging

app = Flask(__name__)
CORS(app)

# GPIO Setup
COIN_PIN = 3  # Coin signal pin
RELAY_PIN = 5  # Relay control pin
GPIO.setmode(GPIO.BOARD)
GPIO.setup(COIN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)  # Relay OFF by default

# Data paths
DATA_DIR = '/root/pisonet/data'
SESSIONS_FILE = os.path.join(DATA_DIR, 'sessions.json')
SALES_FILE = os.path.join(DATA_DIR, 'sales.json')
SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')
LICENSE_FILE = os.path.join(DATA_DIR, 'license.json')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

# Global variables
coin_slot_busy = False
coins_collected = 0
current_session = None
last_coin_time = time.time()

# Load JSON data
def load_json(file_path, default=None):
    if default is None:
        default = {}
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return default

def save_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

# Initialize data
sessions = load_json(SESSIONS_FILE, {"sessions": {}})
sales = load_json(SALES_FILE, {"sales": []})
settings = load_json(SETTINGS_FILE, {"coin_value": 1, "max_clients": 2, "trial_mode": True, "branding": {"name": "PisoNet", "theme": "dark"}})
license_data = load_json(LICENSE_FILE, {"activated": False, "serial": "", "trial_clients": 0})
users = load_json(USERS_FILE, {"users": {}})

# Coin detection thread
def coin_detection():
    global coins_collected, last_coin_time, coin_slot_busy
    while True:
        if GPIO.input(COIN_PIN) == GPIO.LOW and not coin_slot_busy:
            coins_collected += 1
            last_coin_time = time.time()
            logging.info(f"Coin detected. Total coins: {coins_collected}")
            time.sleep(0.1)  # Debounce
        time.sleep(0.01)

threading.Thread(target=coin_detection, daemon=True).start()

# Session timeout check
def check_timeouts():
    global sessions, coin_slot_busy, coins_collected
    while True:
        current_time = time.time()
        to_remove = []
        for client_id, session in sessions["sessions"].items():
            if current_time - session["last_heartbeat"] > 300:  # 5 min timeout
                to_remove.append(client_id)
                if session.get("user"):
                    users["users"][session["user"]]["time_remaining"] += session["time_remaining"]
                    save_json(USERS_FILE, users)
        for client_id in to_remove:
            del sessions["sessions"][client_id]
            coin_slot_busy = False
            GPIO.output(RELAY_PIN, GPIO.LOW)
            sales["sales"].append({"timestamp": current_time, "coins": coins_collected, "revenue": coins_collected * settings["coin_value"]})
            save_json(SALES_FILE, sales)
            coins_collected = 0
        save_json(SESSIONS_FILE, sessions)
        time.sleep(10)

threading.Thread(target=check_timeouts, daemon=True).start()

@app.route('/start_coin_session', methods=['POST'])
def start_coin_session():
    global coin_slot_busy, coins_collected, current_session
    data = request.json
    client_id = data.get('client_id')
    user = data.get('user', None)
    if coin_slot_busy:
        return jsonify({"status": "busy"}), 200
    coin_slot_busy = True
    current_session = {"client_id": client_id, "user": user, "start_time": time.time(), "last_heartbeat": time.time(), "time_remaining": 0}
    sessions["sessions"][client_id] = current_session
    save_json(SESSIONS_FILE, sessions)
    GPIO.output(RELAY_PIN, GPIO.HIGH)  # Activate relay
    return jsonify({"status": "started"}), 200

@app.route('/stop_coin_session', methods=['POST'])
def stop_coin_session():
    global coin_slot_busy, coins_collected, current_session
    data = request.json
    client_id = data.get('client_id')
    if client_id in sessions["sessions"]:
        session = sessions["sessions"][client_id]
        if session["user"]:
            users["users"][session["user"]]["time_remaining"] += session["time_remaining"]
            save_json(USERS_FILE, users)
        del sessions["sessions"][client_id]
        save_json(SESSIONS_FILE, sessions)
        coin_slot_busy = False
        GPIO.output(RELAY_PIN, GPIO.LOW)
        sales["sales"].append({"timestamp": time.time(), "coins": coins_collected, "revenue": coins_collected * settings["coin_value"]})
        save_json(SALES_FILE, sales)
        coins_collected = 0
        current_session = None
    return jsonify({"status": "stopped"}), 200

@app.route('/coin_status', methods=['GET'])
def coin_status():
    return jsonify({"coins": coins_collected, "busy": coin_slot_busy, "session": current_session}), 200

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    data = request.json
    client_id = data.get('client_id')
    if client_id in sessions["sessions"]:
        sessions["sessions"][client_id]["last_heartbeat"] = time.time()
        save_json(SESSIONS_FILE, sessions)
    return jsonify({"status": "ok"}), 200

@app.route('/license_check', methods=['POST'])
def license_check():
    # Simple check, in real implementation validate against serial
    return jsonify({"valid": license_data["activated"], "trial": settings["trial_mode"]}), 200

@app.route('/user_login', methods=['POST'])
def user_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    if username in users["users"] and users["users"][username]["password"] == hashed_pw:
        return jsonify({"valid": True, "time_remaining": users["users"][username]["time_remaining"]}), 200
    return jsonify({"valid": False}), 401

@app.route('/save_user_time', methods=['POST'])
def save_user_time():
    data = request.json
    username = data.get('username')
    time_remaining = data.get('time_remaining')
    if username in users["users"]:
        users["users"][username]["time_remaining"] = time_remaining
        save_json(USERS_FILE, users)
        return jsonify({"status": "saved"}), 200
    return jsonify({"status": "error"}), 400

@app.route('/sales', methods=['GET'])
def get_sales():
    return jsonify(sales), 200