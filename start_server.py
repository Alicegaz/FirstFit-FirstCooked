from user import User

from flask import Flask
from flask import request
from flask_cors import CORS

import json


user1 = User('358480786506', {'lat': 60.17072, 'lon': 24.943043})
USERS = {'358480786506': user1}
for user in USERS.values():
    user.start()

app = Flask(__name__)
CORS(app)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.users = USERS


# Requests from ngrok
@app.route('/nokia', methods=['POST'])
def update_reachable():
    event_info = read_nokia_response()
    event_type = parse_call_event(event_info)

    print(event_type)

    return "OK"


def read_nokia_response():
    info_str = request.data.decode('utf-8')
    info = json.loads(info_str)

    return info


def parse_call_event(call_event_info):
    event_type = call_event_info['callEventNotification']['eventDescription']['callEvent']

    return event_type


@app.route('/api/start_tracking', methods=['GET'])
def start_user():
    addr_num = request.args.get('addr_num')
    app.users[addr_num].start_user_tracking()

    return json.dumps("STARTED")


@app.route('/api/user_status', methods=['GET'])
def user_status():
    addr_num = request.args.get('addr_num')
    user_status = app.users[addr_num].get_user_status()

    return json.dumps(user_status)


@app.route('/api/user_location', methods=['GET'])
def user_location():
    addr_num = request.args.get('addr_num')
    user_loc = app.users[addr_num].get_user_location()

    return json.dumps(user_loc)


if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')
