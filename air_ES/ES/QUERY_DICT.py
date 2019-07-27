TEXT_QUERY={  
    "query": 
    {
      "function_score": {
        "functions": [
          # {
          #   "filter": {
          #     "match": {
          #       'title':'美国'  
          #   }},
          #   "weight": "4"
          # },
          # {
          #   "filter": {
          #     "match": {
          #       "text": "cool"
          #     }
          #   },
          #   "weight": "10"
          # }
        ],
        "score_mode": "sum"
      }
}
}

def get_weighted_query(fields_texts_w):
    '''generate the QUERY for the field and text and weighted
    
    Arguments:
        fields_texts {[type]} -- [description]
    '''
    func = TEXT_QUERY['query']['function_score']['functions']
    for field,text,weighted in fields_texts_w:
        _f_t_w = {}
        _f_t_w['weight'] = str(weighted)
        _f_t_w['filter'] = {'match':{field:text}}
        func.append(_f_t_w)
    return TEXT_QUERY

def get_newly_added_query():
    '''for records in mongo, we add a mark to represent if it has been added into ES
    '''
    query = {'updated':{'$exists':False}}
    return query
  
def mark_added_query(id_list):
    query = {'_id':{'$in':id_list}}
    update = {'$set':{'updated':True}}
    return query,update


def generate_bulk_query(to_index_list):
    _query = []
    _index_q = {'index':{'_index':'test-index'}}
    for record in to_index_list:
        _query.append(_index_q)
        record = {'abstrct':record['abstract'],'title':record['title']}
        _query.append(record)
    # print(_query)
    return _query