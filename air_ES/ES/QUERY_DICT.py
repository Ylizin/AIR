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