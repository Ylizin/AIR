import json

# body_raw='{"degree":"master","interests":[[{"CV":1.2},{"object detection":0.8},{"SLAM":0.4}],[{"NLP":1.3},{"word embedding":0.7},{"SVD":0.8}]]}'

body_raw='[[{"CV":1.2},{"object detection":0.8},{"SLAM":0.4}],[{"NLP":1.3},{"word embedding":0.7},{"SVD":0.8}]]'

# body_unicode=body_raw.decode('utf-8')
body_unicode = body_raw
# print(str(body_unicode)+str('!'))
body = json.loads(body_raw)
for item in body:
    # print(item)
    for x in item:
        key,value = next(iter(x.items()))
        tup=[key,value]
        print(tup)

query_text_raw = body
query_text = [ next(iter(x.items())) for item in query_text_raw for x in item ]
print(query_text)
my_tuple = next(iter(item[0].items()))
# print(str(body[0][0].values()))
# print(my_tuple)
# print(body[0][0].keys())
hhh = {'CV':0.8}
print(tuple(hhh))