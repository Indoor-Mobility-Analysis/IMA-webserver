from pymongo import MongoClient

if __name__ == '__main__':
    client = MongoClient('127.0.0.1', 27017)
    db = client['mapping']
    collection = db['people_activity']
    showN = 0
    for record in collection.find():
        if showN > 15:
            break
        if record['floor'] != 0:
            continue
        pts = []
        if record['small_clusters'] == -1:
            continue
        for cluster in record['small_clusters']:
            if cluster[1] > 160:
                pts.append(cluster[0:2])
        if len(pts) != 0:
            print(record['time_stamp'], len(pts), pts)
        showN += 1