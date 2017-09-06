# -*- coding: UTF-8 -*-
# from app import app
from app import *
import json
from app.DataService.DataService import DataService
from flask import request

start_time = 0
time_gap = 5
dataService = DataService('config.txt')

station_ids = ['admiralty']
@app.route('/')
def index():
    return app.send_static_file('index.html')

# @app.route('/test')
# def getStationConfig():
#     return json.dumps("test")

@app.route('/getStationMap',  methods = ['POST'])
def get_map():
    post_data = json.loads(request.data.decode())
    station_id = post_data['StationId']
    map = dataService.get_map(station_id)
    return json.dumps(map)

@app.route('/getLegendConfiguration',  methods = ['POST'])
def get_legend_config():
    post_data = json.loads(request.data.decode())
    station_id = post_data['StationId']
    config = dataService.get_legend_config(station_id)
    return json.dumps(config)

# getRecordWithTimeRange
@app.route('/getRecordWithTimeRange',  methods = ['POST'])
def get_realtime_data():
    post_data = json.loads(request.data.decode())
    station_id = post_data['StationId']
    start_time = post_data['starttime']
    time_range = post_data['timerange']
    print("Timing: ", start_time / 1000, time_range / 1000);
    data = dataService.get_recent_records(start_time / 1000, time_range / 1000)
    return json.dumps(data)

# getRecordWithTimeRange
@app.route('/getStationRecord',  methods = ['GET'])
def get_station_record():
    with open('config/point_positions2.csv', 'r') as input:
        line = input.readline()
        schemas = line.split(' ')
        schemas = [schema.strip() for schema in schemas]

        line = input.readline()
        station_records = []

        while line:
            segs = line.split()
            segs = [seg.strip() for seg in segs]
            stationObj = {}
            for i in range(0, len(schemas)):
                stationObj[schemas[i]] = segs[i]
            station_records.append(stationObj)
            line = input.readline()
    return json.dumps(station_records)

# getPeopleCount (Added by Qing Du)
@app.route('/getPeopleCount', methods = ['POST'])
def get_people_count():
    get_data = json.loads(request.data.decode())
    day = get_data['day']
    time = get_data['time']
    data = dataService.get_people_count(day, time)
    return json.dumps(data)

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    print('run here')
    global start_time
    while True:
        socketio.sleep(3)
        count += 1
        print("Timing: ", start_time, time_gap)
        data = dataService.get_recent_records(start_time, time_gap)
        start_time += 3
        # print('data', data)
        # print('\n\n')

        print('sent data')
        for station_name in station_ids:
            socketio.emit('my_response',
                      {'data': data, 'count': count},
                      namespace='/test', room=station_name)
#

@socketio.on('connect', namespace='/test')
def test_connect():
    print('CONNECTED')
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=background_thread)

@socketio.on('client_depart', namespace='/test')
def test_disconnect(data):
    print('Client disconnected', data)
    print("rooms", rooms())
    disconnect()

@socketio.on('client_join', namespace='/test')
def client_join_room(data):
    join_room(data['station_id'])
    print('join_room', data['station_id'])
    emit('join_successful')
    print("rooms", rooms())
if __name__ == '__main__':
    pass
