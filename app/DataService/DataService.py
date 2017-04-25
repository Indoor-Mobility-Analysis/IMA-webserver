# StationId, StationName, StationMap
import time
import json
from pymongo import MongoClient
import pymongo
HOST = '127.0.0.1'
PORT = 27017
DB = 'mapping'

class DataService:
    def __init__(self, configPath):
        self.client = MongoClient(HOST, PORT)
        self.db = self.client[DB]
        if configPath == None:
            return
        self.config_path = configPath
        self.init_config()


    def init_config(self):
        with open(self.config_path, 'r') as configFile:
            schemaString = configFile.readline()
            schemas = schemaString.split(',')
            schemas = [e.strip() for e in schemas]
            line = configFile.readline()
            self.station_config = []
            while line:
                elements = [e.strip() for e in line.split(',')]
                station_obj = {}
                for i in range(len(schemas)):
                    station_obj[schemas[i]] = elements[i]
                self.station_config.append(station_obj)

                line = configFile.readline()
            # print('sttion', self.station_config)

    def get_map(self, station_id):
        map_path = None
        for obj in self.station_config:
            if obj['StationId'] == station_id:
                map_path = obj['StationMap']

        if map_path == None:
            print('No station_id', station_id, 'is found')
            return None

        with open(map_path, 'r') as map_file:
            map = json.load(map_file)
            map['stationId'] = station_id
            return map

    def get_legend_config(self, station_id):
        config_path = None
        for obj in self.station_config:
            if obj['StationId'] == station_id:
                config_path = obj['LegendConfig']

        if config_path == None:
            print('No station_id', station_id, 'is found')
            return None

        with open(config_path, 'r') as map_file:
            legend_config = json.load(map_file)
            return {
                'stationId': station_id,
                'legendConfig': legend_config}

    def get_recent_records(self, start, time_range):
        collection = self.db['posts']
        num = 0
        recent_arr = []
        start_time = time.time()
        for record in collection.find({
            'time_stamp':{
                '$gte': start,
                '$lt': (start + time_range)
            }
        }).sort('time_stamp', pymongo.ASCENDING):
            del record['_id']
            del record['map_data']
            tmp1 = record['small_clusters'].lstrip('[(').rstrip(')]').split('), (')
            tmp2 = [x.split(',') for x in tmp1]
            tmp3 = []
            for item in tmp2:
                if len(item) == 6:
                    tmp3.append([int(item[0]), int(item[1]), float(item[2]), float(item[3]), float(item[4]), item[5].strip()])
            # print(tmp3)
            record['small_clusters'] = tmp3
            recent_arr.append(record)
        # recent_arr = sorted(recent_arr, key=lambda tup: tup['time_stamp'], reverse=False)

        print('time', len(recent_arr), time.time() - start_time)
        # print(recent_arr)
        return recent_arr


if __name__ == '__main__':
    dataService = DataService(None)
    dataService.get_recent_records(0, 100)