

def get_weighted_query(fields_texts_w,slop=2):
    '''generate the QUERY for the field and text and weighted
        slop is how many intervals between a phrase is allowed
    Arguments:
        text {list of str,weighted} -- the list of string to be searched, and the score they correspond
    '''
    TEXT_QUERY={  
    "query": 
    {
      'bool':
      {'should':[]}
    }
    }
    should = TEXT_QUERY['query']['bool']['should']
    
    for field,text,weighted in fields_texts_w:
        for _tag,_score in text:
            _f_t_w = {}
            _f_t_w[field] = {'query':_tag,'boost':weighted*_score,'slop':slop}
            should.append({'match_phrase':_f_t_w})
    return TEXT_QUERY


def get_newly_added_query():
    '''for records in mongo, we add a mark to represent if it has been added into ES
    '''
    query = {'$and':[{'updated':{'$exists':False}},{'abstract':{'$exists':True}}]}
    return query
  
def mark_added_query(id_list):
    query = {'_id':{'$in':id_list}}
    update = {'$set':{'updated':True}}
    return query,update


def generate_bulk_query(to_index_list,_index='test-index'):
    _query = []
    _index_q = {'index':{'_index':_index}}
    for record in to_index_list:
        _query.append(_index_q)
        record = {'abstract':record['abstract'],'title':record['title']}
        _query.append(record)
    # print(_query)
    return _query

def get_paper_info_query(titles):
    _query = {'title':{'$in':titles}}
    return _query

def get_user_tags_query(user_id):
    _query = {'id':user_id}
    return _query