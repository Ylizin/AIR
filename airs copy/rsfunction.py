import airs.utils

global num_rs_result
num_rs_result = 10
global num_ES_result
num_ES_result = 200

def get_rs_result(plist, score=[], userinfo={}):
    print('recommend '+str(num_rs_result)+' docs from '+str(num_ES_result)+' ES docs...')
    rs_result = plist[0:num_rs_result]
    print('RS recommend complete!')
    return rs_result

def test():

    # simulate ES result
    test_collection = airs.utils.read_db()
    docs = test_collection.find({}).limit(num_ES_result)
    plist = [doc for doc in docs ]
    score = len(plist)*[100]
    userinfo = {}

    rs_rst = get_rs_result(plist, score, userinfo)
    print('print rs docs...')
    print(rs_rst)
    print('test finish!')
    
    

  

