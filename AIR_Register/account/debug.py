import json

body_raw=b'username=gggg&password=ddddd'
body_unicode=body_raw.decode('utf-8')
print(str(body_unicode)+str('!'))
body = json.loads(body_raw)
print(body)

