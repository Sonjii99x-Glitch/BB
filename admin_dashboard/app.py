from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)

SERVER_IP = '192.168.1.100'  # Configurable

@app.route('/')
def dashboard():
    # Fetch data from server
    try:
        sessions = requests.get(f'http://{SERVER_IP}:5000/coin_status').json()
        sales = requests.get(f'http://{SERVER_IP}:5000/sales').json()  # Assume endpoint
    except:
        sessions = {}
        sales = []
    return render_template('dashboard.html', sessions=sessions, sales=sales)

@app.route('/add_user', methods=['POST'])
def add_user():
    # Add user logic
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)