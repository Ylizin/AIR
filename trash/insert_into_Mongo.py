from pymongo import MongoClient
from pymongo import IndexModel,TEXT, DESCENDING
import pandas as pd

conn = MongoClient()
db = conn.paper
db_set = db.arxiv
# text index should be only one field, it will be used in searching text
# index = IndexModel([('title',DESCENDING),('url',DESCENDING)],unique=True)

db_set.create_index([('title',DESCENDING),('url',DESCENDING)],unique=True)
df = pd.read_csv('../../paper.csv')


columns = df.columns

for tup in df.itertuples():
    tup = tup[1:]
    info = zip(columns,tup)
    try:
        db_set.insert_one(dict(info))
    except Exception as e:
        print(e)