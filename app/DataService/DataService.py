# StationId, StationName, StationMap
import time
import json
from pymongo import MongoClient
import pymongo
import numpy as np

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

    def hack_find_largest_time(self, c_name):
        # Should be packaged
        collection = self.db[c_name]
        largest_record = collection.find().sort('time_stamp',pymongo.DESCENDING).limit(1)
        records = list(largest_record)
        if len(records) == 0:
            return None
        return records[0]['time_stamp']


    def get_recent_records_single_collection(self, c_name, start, time_range):
        collection = self.db[c_name] # people_activity / posts
        num = 0
        recent_arr = []
        start_time = time.time()

        for record in collection.find({
            'time_stamp':{
                '$gte': start,
                '$lt': (start + time_range)
            }
        }).sort('time_stamp', pymongo.ASCENDING):
            if "_id" in record:
                del record['_id']
            if "map_data" in record:
                del record['map_data']
            # small cluster
            if "small_clusters" in record:
                # Hack since no people count for each clusters, I assign each small clusters an average value to the last element

                for index, c in enumerate(record['small_clusters']):
                    r_path = record['small_clusters'][index][6]
                    if type(r_path) is not list:
                        record['small_clusters'][index][6] = None


            recent_arr.append(record)

        return recent_arr

    def get_recent_records(self, start, time_range):
        # people_activity = self.get_recent_records_single_collection('people_activity', start, time_range)
        people_activity = self.get_recent_records_single_collection('people_activity_merge', start, time_range)
        # all_people_activity
        ticket_record = self.get_recent_records_single_collection('tickets_ADM', start, time_range)

        return {
            'people_activity': people_activity,
            'ticket_record': ticket_record
        }


    def get_people_count(self, day, ttt):
        """
        This function is used to retrieve the people count collection from MongoDB.
        Created by Qing Du (q.du@ust.hk)
        """
        collection = self.db['people_count']
        max_count = collection.find().sort('count', pymongo.DESCENDING).limit(1)[0]['count']
        result = {}
        result['max_count'] = max_count
        for record in collection.find({'day': day, 'time': ttt}):
            result[record['station_ID']] = record['count']
        return result


if __name__ == '__main__':
    dataService = DataService(None)
    # vc = dataService.get_recent_records(100000000, 1000001000)
    vc = dataService.hack_find_largest_time('people_activity_600')
    print('vc', vc)