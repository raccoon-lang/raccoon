import json

def json_dumps(value):
    value = eval(repr(value))
    return json.dumps(value, indent=4)

