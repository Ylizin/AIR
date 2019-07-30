import pymongo
import time

def read_db(address="mongodb://106.75.229.123:27017", database='spider', auth='spider', auth_pwd='boyu42', collection='arxiv'):

    start = time.time()
    print('DB connecting...')

    airs_client = pymongo.MongoClient(address)
    airs_db = airs_client[database]
    airs_db.authenticate(auth, auth_pwd)
    airs_collection = airs_db[collection]
    
    end = time.time()
    print('DB connect time usage '+str(end-start)+'s')
    print('DB connect complete!')
    
    return airs_collection
